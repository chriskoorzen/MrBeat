from array import array

from audiostream.sources.thread import ThreadSource


# This does the actual playing of sounds by passing a channel and a wav stream
class AudioSourceOneShot(ThreadSource):

    def __init__(self, output_stream, *args, **kwargs):
        ThreadSource.__init__(self, output_stream, *args, **kwargs)
        self.wav_samples = None          # Init wav sample variable
        self.nb_wav_samples = 0          # Init wav sample length variable
        self.chunk_nb_samples = 32       # Define the number of samples played per chunk (somewhat arbitrary)
        self.current_sample_index = 0    # Remember sample index position
        self.buffer = array('h', b"\x00\x00" * self.chunk_nb_samples)  # Init with empty 32 * 16-bit (zero) samples
                                                                       # \x00 is one byte (8-bits)

    def set_wav_samples(self, wav_samples):
        self.wav_samples = wav_samples          # Get the wav source samples
        self.current_sample_index = 0  # Reset position index
        self.nb_wav_samples = len(wav_samples)  # Get the no. of samples in wav source

    # Override the get_bytes method of ThreadSource
    # This is called internally somewhere and makes the magic happen
    def get_bytes(self, *args, **kwargs):

        if self.nb_wav_samples > 0:
            for i in range(self.chunk_nb_samples):
                # Keep pushing bytes until sample is played through, i.e. while index is less than sample count
                if self.current_sample_index < self.nb_wav_samples:
                    self.buffer[i] = self.wav_samples[self.current_sample_index]  # Send data to buffer
                else:
                    self.buffer[i] = 0  # After one playthrough, stop, by passing empty (zero) int.
                self.current_sample_index += 1  # Increment position to play through entire sample

        return self.buffer.tobytes()  # Note - some implementations use tostring()
