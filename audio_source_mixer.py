from array import array

from audiostream.sources.thread import ThreadSource
# This does the actual playing of sounds by passing a channel and a wav stream
from audio_source_track import AudioSourceTrack

# Bounding condition for track sums that flow over 16 bits
MAX_16BITS = 32767
MIN_16BITS = -32768
def sum_16bits(n):
    s = sum(n)
    return min(max(s, MIN_16BITS), MAX_16BITS)


class AudioSourceMixer(ThreadSource):

    def __init__(self, output_stream, all_wav_samples, bpm, sample_rate, nb_steps, on_current_step_changed, min_bpm, *args, **kwargs):
        ThreadSource.__init__(self, output_stream, *args, **kwargs)

        self.tracks = []
        for i in range(len(all_wav_samples)):
            track = AudioSourceTrack(output_stream, all_wav_samples[i], bpm, sample_rate, min_bpm)
            # Init tracks with same number of steps
            # - not necessary -> remove empty step check in AudioTrack get_bytes
            track.set_steps((0,) * nb_steps)
            self.tracks.append(track)

        # Init buffer with same size as tracks
        buffer_nb_samples = self.tracks[0].buffer_nb_samples
        self.silence = array('h', b"\x00\x00" * buffer_nb_samples)     # AudioTrack buffers will be aggregated in here

        self.min_bpm = min_bpm
        self.bpm = bpm

        self.sample_rate = sample_rate
        self.nb_steps = nb_steps
        self.current_sample_index = 0           # Remember sample index position
        self.current_step_index = 0

        # Optional callback function to operate on change of current_step_index -- see get_bytes function
        self.on_current_step_changed = on_current_step_changed

        self.is_playing = False

    def set_bpm(self, bpm):
        # Protect against bad bpm value
        if bpm < self.min_bpm:
            return
        # Update all track bpm changes concurrently
        self.bpm = bpm

    def audio_play(self):
        self.is_playing = True

    def audio_stop(self):
        self.is_playing = False

    # Override the get_bytes method of ThreadSource
    # This is called internally somewhere and makes the magic happen
    def get_bytes(self, *args, **kwargs):

        # Update bpm for all tracks before going through rest of code in get_bytes
        # This guarantees to avoid a race condition where track buffer size may be changed half-way through the
        # get_bytes thread and cause an out-of-bounds error
        for i in range(len(self.tracks)):
            self.tracks[i].set_bpm(self.bpm)

        # Every track *should* have identical samples per step - use
        step_nb_samples = self.tracks[0].step_nb_samples

        # Return silence and end get_bytes call when is_playing is set to False
        if not self.is_playing:
            return self.silence[:].tobytes()

        # Loop over tracks and get every track buffer for every call of
        # get_bytes by audio library. get_bytes of AudioSourceTrack is overridden to return the buffer itself.
        track_buffers = []
        for i in range(len(self.tracks)):
            track = self.tracks[i]
            track_buffer = track.get_bytes_array()
            track_buffers.append(track_buffer)

        # zip rearranges buffers by index
        # map applies sum_16bits to index array, and creates a new array with the total values
        s = map(sum_16bits, zip(*track_buffers))
        result_buf = array("h", s)

        # VISUAL INDICATOR
        # transmit current_step_index to play indicator before it increments to the next step
        # Optional function parameter to operate on current_step_index for UI display
        if self.on_current_step_changed is not None:
            step_index_with_offset = self.current_step_index - 4    # Hardcoded offset to compensate for time delay
            if step_index_with_offset < 0:
                step_index_with_offset += self.nb_steps             # If a negative value, add total steps to correct
            self.on_current_step_changed(step_index_with_offset)   # This function expects the step_index parameter

        self.current_step_index += 1
        # Reset step index position once looped through
        if self.current_step_index >= self.nb_steps:
            self.current_step_index = 0

        # Since the buffer size is fixed, only return the part of the buffer with valid samples
        # --based on the number of samples per step (changes with bpm)
        return result_buf.tobytes()  # Note - some implementations use tostring()
