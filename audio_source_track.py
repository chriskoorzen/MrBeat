from array import array

from audiostream.sources.thread import ThreadSource


# This does the actual playing of sounds by passing a channel and a wav stream
class AudioSourceTrack(ThreadSource):

    def __init__(self, output_stream, wav_samples, bpm, sample_rate, min_bpm, *args, **kwargs):
        ThreadSource.__init__(self, output_stream, *args, **kwargs)

        self.min_bpm = min_bpm                  # This setting allows to create the maximum size buffer needed
        self.bpm = bpm
        self.sample_rate = sample_rate

        self.wav_samples = wav_samples          # Get the wav source samples
        self.nb_wav_samples = len(wav_samples)  # Get the no. of samples in wav source

        # How many samples to play per step - this is dependent on BPM
        self.step_nb_samples = self.compute_step_nb_samples(bpm)
        self.steps = ()                         # Tuple index for enabled/disabled step to play sound

        self.current_sample_index = 0           # Remember sample index position
        self.current_step_index = 0
        self.last_sound_start_sample_index = 0

        # Calculate buffer size using min bpm
        self.buffer_nb_samples = self.compute_step_nb_samples(min_bpm)  # Save reference for Audio Mixer use
        self.buffer = array('h', b"\x00\x00" * self.buffer_nb_samples)

    def set_steps(self, steps):
        # If the number of steps change the step index must be reset
        if not len(steps) == len(self.steps):
            self.current_step_index = 0
        self.steps = steps

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.step_nb_samples = self.compute_step_nb_samples(bpm)

    def compute_step_nb_samples(self, bpm_value):
        # protect against div/0
        if not bpm_value == 0:
            # 4 steps per beat == 1/4 beat per step  -> arbitrary choice of how to split beats and steps
            # samples per step = ( sample rate (44100) * 60 sec ) / ( 4 steps * bpm )
            step_samples = int(self.sample_rate * 15 / bpm_value)  # cannot be fractional value
            return step_samples
        return 0

    # Override the get_bytes method of ThreadSource  -- see get_bytes_array
    # This is called internally by audio library and makes the magic happen
    def get_bytes(self, *args, **kwargs):
        # Add .tobytes() for audio library call
        return self.get_bytes_array().tobytes()  # Note - some implementations use tostring()

    # This is not necessary when audioMixer zero init is removed
    def no_steps_activated(self):
        if len(self.steps) == 0:
            return True
        for n in self.steps:
            if n == 1:
                return False
        return True

    # Alias of get_bytes to expose the buffer for AudioSourceMixer
    def get_bytes_array(self):

        for i in range(self.step_nb_samples):
            if len(self.steps) > 0 and not self.no_steps_activated():  # Check if any steps are present
                # Check if step at [index] position is enabled
                # and if index is smaller than wav samples allocated
                if self.steps[self.current_step_index] == 1 and i < self.nb_wav_samples:
                    self.buffer[i] = self.wav_samples[i]  # then pass the wav sample to buffer
                    if i == 0:                                                          # When new sound starts
                        self.last_sound_start_sample_index = self.current_sample_index  # Memorize sample position
                else:
                    index = self.current_sample_index - self.last_sound_start_sample_index
                    if index < self.nb_wav_samples:                 # If the sample position has not played through
                        self.buffer[i] = self.wav_samples[index]    # the entire sample, continue where left off
                    else:
                        self.buffer[i] = 0  # else place nothing
            else:
                self.buffer[i] = 0  # else place nothing
            self.current_sample_index += 1

        # Increment step index after each loop
        self.current_step_index += 1
        # Reset step index position once looped through
        if self.current_step_index >= len(self.steps):
            self.current_step_index = 0

        # Since the buffer size is fixed, only return the part of the buffer with valid samples
        # --based on the number of samples per step (changes with bpm)
        return self.buffer[0:self.step_nb_samples]
