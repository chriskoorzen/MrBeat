import kivy
import audiostream
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.relativelayout import RelativeLayout

from audio_engine import AudioEngine
from sound_kit_service import SoundKitService
from track import TrackWidget

TRACKS_NB_STEPS = 16


class MainWidget(RelativeLayout):
    control_layout = ObjectProperty()
    tracks_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.sound_kit_service = SoundKitService()
        self.audio_engine = AudioEngine()
        all_wav_samples = self.sound_kit_service.get_all_samples()
        self.audio_mixer = self.audio_engine.create_mixer(all_wav_samples, 100, TRACKS_NB_STEPS)

    def on_parent(self, widget, parent):
        # Add a track for each sound loaded into sound kit
        for index in range(self.sound_kit_service.get_nb_tracks()):
            sound = self.sound_kit_service.get_sound(index)
            track_source = self.audio_mixer.tracks[index]
            self.tracks_layout.add_widget(TrackWidget(sound, self.audio_engine, TRACKS_NB_STEPS, track_source))


class MrBeatApp(App):
    pass


MrBeatApp().run()
