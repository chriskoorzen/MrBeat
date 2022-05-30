from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
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

        bounding_box = BoxLayout()
        bounding_box.width = track_left_align
        bounding_box.size_hint_x = None

        sound_button = TrackSoundButton()
        sound_button.text = self.name
        sound_button.size_hint_x = None
        sound_button.on_press = self.on_soundbutton_press
        bounding_box.add_widget(sound_button)

        separator_image = Image(source="images/track_separator.png")
        separator_image.size_hint_x = None
        separator_image.width = dp(15)
        bounding_box.add_widget(separator_image)

        self.add_widget(bounding_box)

        button_color1 = "images/step_normal2.png"
        button_color2 = "images/step_normal1.png"
        for i in range(track_nb_steps):
            # Every 4th track, alternate button color
            # It will swap on first run, i = 0
            if i % 4.0 == 0:
                # Swap variables around --- is there an elegant way to do this in Python?? Yes, yes there is.
                button_color1, button_color2 = button_color2, button_color1
            step_button = TrackStepButton(background_normal=button_color1)
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
        self.track_source.set_steps(steps)      # Pass the step settings to AudioSource

    def on_soundbutton_press(self):
        self.audio_engine.play_sound(self.sound.samples)
        pass
