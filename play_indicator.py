from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget


class PlayIndicatorLight(Image):
    pass


# Implement an indicator to show current active step
# Use the toggle button widget with its on/off property, but make it non-interactive for the user
class PlayIndicator(BoxLayout):
    # nb_steps -> from Number of track steps defined in main
    # current_step_index -> know which button to light up
    # Manage layout offset
    nb_steps = 0
    left_align = NumericProperty(0)
    indicator_lights = []

    # Create indicator lights
    def set_nb_steps(self, nb_steps):
        if nb_steps != self.nb_steps:
            self.nb_steps = nb_steps    # Update value
            self.clear_widgets()        # Remove previous widgets on update

            # Style of left-aligned spacer -> First element and same size as sound button appearing underneath
            left_align_spacer = Widget()
            left_align_spacer.size_hint_x = None
            left_align_spacer.width = self.left_align
            self.add_widget(left_align_spacer)
            
            # Add actual step indicators
            self.indicator_lights = []                              # Reset with each call
            for i in range(nb_steps):
                light = PlayIndicatorLight()
                light.source = "images/indicator_light_off.png"     # Default
                self.indicator_lights.append(light)
                self.add_widget(light)

    # Control which element lights up -> must be in sync with current step the audio mixer is playing
    def set_current_step_index(self, index):
        # Integer "index" cannot be greater than number of indicator lights
        if index >= len(self.indicator_lights):
            return

        for i in range(len(self.indicator_lights)):
            light = self.indicator_lights[i]
            if i == index:
                # Activated
                light.source = "images/indicator_light_on.png"
            else:
                # Normal
                light.source = "images/indicator_light_off.png"
