from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton


class PlayIndicatorButton(ToggleButton):
    pass


# Implement an indicator to show current active step
# Use the toggle button widget with its on/off property, but make it non-interactive for the user
class PlayIndicator(BoxLayout):
    # nb_steps -> from Number of track steps defined in main
    # current_step_index -> know which button to light up
    # Manage layout offset
    nb_steps = 0
    left_align = NumericProperty(0)
    indicator_buttons = []

    # Create indicator buttons
    def set_nb_steps(self, nb_steps):
        if nb_steps != self.nb_steps:
            self.nb_steps = nb_steps    # Update value
            self.clear_widgets()        # Remove previous widgets on update

            # Style of left-aligned spacer -> First element and same size as sound button appearing underneath
            left_align_button = Button()
            left_align_button.size_hint_x = None
            left_align_button.width = self.left_align
            left_align_button.disabled = True
            left_align_button.background_disabled_normal = ''   # This is a texture by default
            left_align_button.background_color = (0, 0, 0, 0)   # RGBA value -> this property alone handles color
            self.add_widget(left_align_button)
            # Add actual step indicators
            self.indicator_buttons = []                              # Reset with each call
            for i in range(nb_steps):
                button = PlayIndicatorButton()
                button.disabled = True
                button.background_color = (0, 1.0, 1.0, 1.0)
                button.background_disabled_down = ''
                # if i == 0:
                #     button.state = 'down'
                self.indicator_buttons.append(button)
                self.add_widget(button)

    # Control which element lights up -> must be in sync with current step the audio mixer is playing
    def set_current_step_index(self, index):
        # Integer "index" cannot be greater than number of indicator buttons
        if index >= len(self.indicator_buttons):
            return

        for i in range(len(self.indicator_buttons)):
            button = self.indicator_buttons[i]
            if i == index:
                button.state = 'down'
            else:
                button.state = 'normal'
