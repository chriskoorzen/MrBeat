import kivy
import audiostream
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.relativelayout import RelativeLayout

from audio_engine import AudioEngine
from sound_kit_service import SoundKitService
from track import TrackWidget


class MainWidget(RelativeLayout):
    control_layout = ObjectProperty()
    tracks_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.sound_kit_service = SoundKitService()
        self.audio_engine = AudioEngine()

        # Test sound playing
        # test_sound = self.sound_kit_service.get_sound(7)  # Get a Sound class object
        # self.audio_engine.play_sound(test_sound.samples)  # Hit play and pass the Sound class wav samples
        # self.audio_engine.create_track(test_sound.samples, 60)

    def on_parent(self, widget, parent):
        # Add a track for each sound loaded to sound kit
        for index in range(self.sound_kit_service.get_nb_tracks()):
            sound = self.sound_kit_service.get_sound(index)
            self.tracks_layout.add_widget(TrackWidget(sound, self.audio_engine))


class MrBeatApp(App):
    pass


MrBeatApp().run()
