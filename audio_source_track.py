from array import array

from audiostream.sources.thread import ThreadSource


# This does the actual playing of sounds by passing a channel and a wav stream
class AudioSourceTrack(ThreadSource):

    def __init__(self, output_stream, wav_samples, bpm, sample_rate, *args, **kwargs):
        ThreadSource.__init__(self, output_stream, *args, **kwargs)
        self.steps = ()                         # Init as empty tuple
        self.step_nb_samples = 0

        self.bpm = bpm
        self.sample_rate = sample_rate

        self.wav_samples = wav_samples          # Get the wav source samples
        self.nb_wav_samples = len(wav_samples)  # Get the no. of samples in wav source

        self.current_sample_index = 0           # Remember sample index position
        self.current_step_index = 0
        self.last_sound_start_sample_index = 0

        self.buffer = None
        self.compute_step_nb_samples_and_alloc_buffer()

    def set_steps(self, steps):
        # If the number of steps change the step index must be reset
        if not len(steps) == len(self.steps):
            self.current_step_index = 0
        self.steps = steps

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.compute_step_nb_samples_and_alloc_buffer()  # bpm impacts the buffer size and must be reset at every change

    # 4 steps per beat == 1/4 beat per step
    # samples per step = ( sample rate (44100) * 60 sec ) / ( 4 steps * bpm )
    def compute_step_nb_samples_and_alloc_buffer(self):
        # protect against div/0
        if not self.bpm == 0:
            # Realloc buffer is costly and must only be done if step samples value is changed
            step_samples = int(self.sample_rate * 15 / self.bpm)  # cannot be fractional value
            if not step_samples == self.step_nb_samples:
                self.step_nb_samples = step_samples     # Set to new value if different
                self.buffer = array('h', b"\x00\x00" * self.step_nb_samples)

    # Override the get_bytes method of ThreadSource
    # This is called internally somewhere and makes the magic happen
    def get_bytes(self, *args, **kwargs):

        for i in range(self.step_nb_samples):
            if len(self.steps) > 0:  # Check if any steps are present
                # Check if step at [index] position is enabled, and index is smaller than wav samples allocated
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

        self.current_step_index += 1
        if self.current_step_index >= len(self.steps):
            self.current_step_index = 0

        return self.buffer.tobytes()  # Note - some implementations use tostring()
