from array import array

from audiostream.sources.thread import ThreadSource


# This does the actual playing of sounds by passing a channel and a wav stream
from audio_source_track import AudioSourceTrack


class AudioSourceMixer(ThreadSource):

    def __init__(self, output_stream, all_wav_samples, bpm, sample_rate, nb_steps, *args, **kwargs):
        ThreadSource.__init__(self, output_stream, *args, **kwargs)

        self.tracks = []
        for i in range(len(all_wav_samples)):
            track = AudioSourceTrack(output_stream, all_wav_samples[i], bpm, sample_rate)
            # Init tracks with same number of steps - not necessary -> remove empty step check in AudioTrack get_bytes
            track.set_steps((0,) * nb_steps)
            self.tracks.append(track)

        self.sample_rate = sample_rate
        self.nb_steps = nb_steps
        self.current_sample_index = 0           # Remember sample index position
        self.current_step_index = 0

        self.buffer = None                      # AudioTrack buffers will be aggregated in here
        '''
    def set_steps(self, index, steps):
        # Index cannot be greater than number of tracks loaded
        print("AudioMixer set steps called")
        if index >= len(self.tracks):
            print("mixer: did nothing (index >= steps)")
            return
        
        # Make sure step length stay consistent
        if len(steps) == self.nb_steps:
            print(self.tracks[index])
            self.tracks[index].set_steps(steps)
            print("mixer: steps given to AudioSourceTrack")
        '''
    def set_bpm(self, bpm):
        # Update all track bpm changes concurrently
        for i in range(len(self.tracks)):
            self.tracks[i].set_bpm(bpm)

    # Override the get_bytes method of ThreadSource
    # This is called internally somewhere and makes the magic happen
    def get_bytes(self, *args, **kwargs):

        # Every track *should* have identical samples per step as determined by compute_step_nb_samples_and_alloc_buffer
        step_nb_samples = self.tracks[0].step_nb_samples

        # If buffer is not yet init'd or the step_length has changed, init buffer
        if self.buffer is None or not len(self.buffer) == step_nb_samples:
            self.buffer = array('h', b"\x00\x00" * step_nb_samples)

        # Loop over tracks and get every track buffer for every call of
        # get_bytes by audio library. get_bytes of AudioSourceTrack is overridden to return the buffer itself.
        track_buffers = []
        for i in range(len(self.tracks)):
            track = self.tracks[i]
            track_buffer = track.get_bytes_array()
            track_buffers.append(track_buffer)

        # For every index, loop over track buffer samples and aggregate samples into single output value
        for sample in range(step_nb_samples):
            self.buffer[sample] = 0         # Reset on each loop
            for track in range(len(self.tracks)):
                self.buffer[sample] += track_buffers[track][sample]

        self.current_step_index += 1
        # Reset step index position once looped through
        if self.current_step_index >= self.nb_steps:
            self.current_step_index = 0

        return self.buffer.tobytes()  # Note - some implementations use tostring()
