from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton

Builder.load_file("track.kv")


class TrackStepButton(ToggleButton):
    pass


class TrackSoundButton(Button):
    pass


class TrackWidget(BoxLayout):

    def __init__(self, sound, audio_engine, track_nb_steps, track_source, track_left_align, **kwargs):
        super(TrackWidget, self).__init__(**kwargs)
        self.name = sound.displayname
        self.sound = sound                  # Save reference to Sound class object init'd in sound_kit_service
        self.audio_engine = audio_engine    # Save reference to Audio Engine object init'd in main
        self.step_buttons = []              # Save a list of step buttons created to access state later
        self.track_nb_steps = track_nb_steps
        self.track_source = track_source    # Save reference to AudioSourceTrack class object

        sound_button = TrackSoundButton(text=self.name, width=track_left_align)
        self.add_widget(sound_button)
        sound_button.on_press = self.on_soundbutton_press
        for i in range(track_nb_steps):
            step_button = TrackStepButton()
            self.step_buttons.append(step_button)
            step_button.bind(state=self.on_step_button_state)  # Bind a function to trigger when state is changed
            self.add_widget(step_button)

    def on_step_button_state(self, widget, value):
        # When state is "down" -> 1 else 0  -- determining active steps
        steps = []
        for i in range(0, self.track_nb_steps):
            if self.step_buttons[i].state == "down":
                steps.append(1)
            else:
                steps.append(0)
        # self.track_source.set_steps(steps)  # Pass the step settings to AudioSource # DEV
        print("Track:: steps set")
        print("Track:: " + str(steps))
        self.track_source.set_steps(steps)

    def on_soundbutton_press(self):
        self.audio_engine.play_sound(self.sound.samples)
        pass
