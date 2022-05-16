from audiostream.core import get_output

from audio_source import AudioSourceOneShot
from audio_source_track import AudioSourceTrack


class AudioEngine:

    NB_CHANNELS = 1         # 1 for Mono, 2 for Stereo
    SAMPLE_RATE = 44100
    BUFFER_SIZE = 1024
    SAMPLE_ENCODING = 16

    def __init__(self):
        # Define output channel characteristics using AudioStream
        self.output_stream = get_output(rate=self.SAMPLE_RATE,
                                        channels=self.NB_CHANNELS,
                                        encoding=self.SAMPLE_ENCODING,
                                        buffersize=self.BUFFER_SIZE
                                        )
        # Init single AudioSource thread
        # Pass channel handler to ThreadSource subclass (AudioSourceOneShot)
        # self.audio_source = AudioSourceOneShot(self.output_stream)
        # self.audio_source.start()  # Let 'er rip!

    def play_sound(self, wav_samples):
        self.audio_source.set_wav_samples(wav_samples)

    def create_track(self, wav_samples, bpm):
        source_track = AudioSourceTrack(self.output_stream, wav_samples, bpm, self.SAMPLE_RATE)
        # test_step = (1, 1, 0, 0)            # Test code
        # source_track.set_steps(test_step)   # Test code
        source_track.start()    # Starts the engine that consumes bytes out of buffer
        return source_track     # Return handler to AudioSourceTrack to allow call of set_steps


