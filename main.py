import kivy
import audiostream
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty, Clock
from kivy.uix.relativelayout import RelativeLayout

from audio_engine import AudioEngine
from sound_kit_service import SoundKitService
from track import TrackWidget

TRACKS_NB_STEPS = 16
MIN_BPM = 80
MAX_BPM = 160


class MainWidget(RelativeLayout):
    control_layout = ObjectProperty()
    play_indicator_widget = ObjectProperty()    # Create reference to PlayIndicator class object defined in kv file
    tracks_layout = ObjectProperty()
    audio_mixer = ObjectProperty()
    bpm = NumericProperty(100)

    indicator_step_index = 0                    # This value is received from Audio Mixer

    TRACK_STEPS_LEFT_ALIGN = NumericProperty(dp(100))

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.sound_kit_service = SoundKitService()
        self.audio_engine = AudioEngine()
        all_wav_samples = self.sound_kit_service.get_all_samples()
        self.audio_mixer = self.audio_engine.create_mixer(all_wav_samples, 100, TRACKS_NB_STEPS, self.on_mixer_current_step_changed, MIN_BPM)

    # on_parent calls when the MainWidget is hooked to the prepared window
    def on_parent(self, widget, parent):
        # Build the Play Indicator display
        self.play_indicator_widget.set_nb_steps(TRACKS_NB_STEPS)

        # Build a track for each sound loaded into sound kit
        for index in range(self.sound_kit_service.get_nb_tracks()):
            sound = self.sound_kit_service.get_sound(index)
            track_source = self.audio_mixer.tracks[index]
            self.tracks_layout.add_widget(TrackWidget(sound, self.audio_engine, TRACKS_NB_STEPS, track_source, self.TRACK_STEPS_LEFT_ALIGN))

    def on_mixer_current_step_changed(self, step_index):
        # This function gets passed to the Audio Mixer to call on its current step index, so that we may display it
        # Since we should never call UI elements from a separate thread, use kivy's Clock scheduler to
        # call the function from the main UI thread
        # Save reference to Audio Mixer step index when it gets passed to this function
        self.indicator_step_index = step_index
        Clock.schedule_once(self.update_play_indicator_callback, 0)

    def update_play_indicator_callback(self, delta_time):
        # delta_time is a requirement for using Clock property -- see on_mixer_current_step_changed
        # UI elements may not be init'd when audio thread has started
        if self.play_indicator_widget is not None:
            self.play_indicator_widget.set_current_step_index(self.indicator_step_index)

    def audio_play(self):
        self.audio_mixer.audio_play()

    def audio_stop(self):
        self.audio_mixer.audio_stop()

    # Kivy auto-calls "on_* ", where * == name of {type}Property that is defined,
    # and when used inside kv (see kv file root.bpm)
    def on_bpm(self, widget, value):
        # Limit bpm values to between MIN_BPM and MAX_BPM
        if value < MIN_BPM:
            self.bpm = MIN_BPM
            return
        if value > MAX_BPM:
            self.bpm = MAX_BPM
            return

        self.audio_mixer.set_bpm(self.bpm)


class MrBeatApp(App):
    pass


MrBeatApp().run()
