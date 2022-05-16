
# filename (path), displayname
import wave
from array import array


class Sound:

    def __init__(self, file_path_name, displayname):
        self.file_path_name = file_path_name
        self.displayname = displayname
        self.nb_frames = None
        self.samples = None                   # This is what gets passed to Audio Engine for playback
        self.load_sound()

    # Read the raw wav file (as bytes) and cast to suitable format (16-bit pieces)
    def load_sound(self):
        wav_file = wave.open(self.file_path_name, 'rb')  # Use wave lib to handle wav file
        self.nb_frames = wav_file.getnframes()           # No of samples
        frames = wav_file.readframes(self.nb_frames)     # get bytes (8 bits) of wav file
        self.samples = array('h', frames)                # use array to write as signed 2 byte int (16 bits)


class SoundKit:
    # Container class for Sound class
    sounds = ()

    def get_nb_tracks(self):
        return len(self.sounds)


class SoundKit_1(SoundKit):
    sounds = (Sound('sounds/kit1/kick.wav', 'KICK'),
              Sound('sounds/kit1/clap.wav', 'CLAP'),
              Sound('sounds/kit1/snare.wav', 'SNARE'),
              Sound('sounds/kit1/bass.wav', 'BASS'),
              Sound('sounds/kit1/pluck.wav', 'PLUCK'),
              Sound('sounds/kit1/shaker.wav', 'SHAKER'),
              Sound('sounds/kit1/vocal_chop.wav', 'VOCAL'),
              Sound('sounds/kit1/effects.wav', 'EFFECTS')
              )

    pass


class SoundKitService:
    soundkit = SoundKit_1()

    def get_nb_tracks(self):
        return self.soundkit.get_nb_tracks()

    # Return handler of Sound class object at [index]
    def get_sound(self, index):
        if index >= len(self.soundkit.sounds):
            return None
        return self.soundkit.sounds[index]

