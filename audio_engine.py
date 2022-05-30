from audiostream.core import get_output

from audio_source import AudioSourceOneShot
from audio_source_mixer import AudioSourceMixer
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
        self.audio_mixer = None
        # Init single AudioSource thread
        # Pass channel handler to ThreadSource subclass (AudioSourceOneShot)
        self.audio_source_oneshot = AudioSourceOneShot(self.output_stream)
        # This activates the audio library that calls get_bytes and send data to sound card
        self.audio_source_oneshot.start()

    def play_sound(self, wav_samples):
        self.audio_source_oneshot.set_wav_samples(wav_samples)

    def create_track(self, wav_samples, bpm):
        source_track = AudioSourceTrack(self.output_stream, wav_samples, bpm, self.SAMPLE_RATE)
        source_track.start()    # Starts the engine that consumes bytes out of buffer
        return source_track     # Return handler to AudioSourceTrack to allow call of set_steps

    def create_mixer(self, all_wav_samples, bpm, nb_steps, on_current_step_changed, min_bpm):
        self.audio_mixer = AudioSourceMixer(self.output_stream, all_wav_samples, bpm, self.SAMPLE_RATE, nb_steps, on_current_step_changed, min_bpm)
        self.audio_mixer.start()
        return self.audio_mixer
