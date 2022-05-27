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

        self.current_step_index = 0
        self.buf_index_pntr = 0  # Remember sample index position

        # Calculate buffer size using min bpm
        self.buffer_nb_samples = self.compute_step_nb_samples(min_bpm)  # Save reference for Audio Mixer use
        self.silence = array('h', b"\x00\x00" * self.buffer_nb_samples)

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
            step_samples = self.sample_rate * 15 // bpm_value  # cannot be fractional value
            return step_samples
        return 0

    def increment_pointer(self, step):
        self.buf_index_pntr += step
        if self.buf_index_pntr > self.nb_wav_samples:
            # current sample cannot be greater than nb_wav_samples -> Overflow error
            # reset
            self.buf_index_pntr = 0

    # Override the get_bytes method of ThreadSource  -- see get_bytes_array
    # This is called internally by audio library and makes the magic happen
    def get_bytes(self, *args, **kwargs):
        # Add .tobytes() for audio library call
        return self.get_bytes_array().tobytes()  # Note - deprecated versions use tostring()

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

        result_buf = None

        # 1 - No steps activated -> return silence
        if self.no_steps_activated():
            result_buf = self.silence[0:self.step_nb_samples]
            self.buf_index_pntr = 0

        elif self.steps[self.current_step_index] == 0:
            # 2 - Step is Not Activated
            if self.buf_index_pntr == 0:
                # 2.1 - Pointer is at start of track
                result_buf = self.silence[0:self.step_nb_samples]

            elif self.buf_index_pntr + self.step_nb_samples > self.nb_wav_samples:
                # 2.2 Overflow detected
                result_buf = self.wav_samples[self.buf_index_pntr:]     # Give remaining samples
                pad = self.step_nb_samples - len(result_buf)
                result_buf.extend(self.silence[0:pad])                  # Pad out with zeros
                self.increment_pointer(self.step_nb_samples)

            else:
                # 2.3 Requested samples is within range
                result_buf = self.wav_samples[self.buf_index_pntr:self.buf_index_pntr+self.step_nb_samples]
                self.increment_pointer(self.step_nb_samples)
            
        else:
            # 3 - Step is Activated
            # Reset pointer -- start track afresh
            self.buf_index_pntr = 0
            if self.step_nb_samples > self.nb_wav_samples:
                # 2.2 Overflow detected
                result_buf = self.wav_samples[:]     # Give remaining samples
                pad = self.step_nb_samples - len(result_buf)
                result_buf.extend(self.silence[0:pad])                  # Pad out with zeros
                self.increment_pointer(self.step_nb_samples)
            else:
                # 2.3 Requested samples is within range
                result_buf = self.wav_samples[self.buf_index_pntr:self.buf_index_pntr + self.step_nb_samples]
                self.increment_pointer(self.step_nb_samples)

        # Track sync
        # Increment step index after each loop
        self.current_step_index += 1
        # Reset step index position once looped through
        if self.current_step_index >= len(self.steps):
            self.current_step_index = 0

        # Trace calls and breakpoints
        if result_buf is None:
            print("result buf is none")

        elif len(result_buf) == 0:
            print("Result buf no length")

        elif not len(result_buf) == self.step_nb_samples:
            print("result buf is not size of step_nb_samples")

        # Since the buffer size is fixed, only return the part of the buffer with valid samples
        # --based on the number of samples per step (changes with bpm)
        return result_buf
