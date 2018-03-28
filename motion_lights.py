import appdaemon.plugins.hass.hassapi as hass

"""
Flash some RGB lights red and white when motion is detected (or a signal
from any binary sensor.)

The "monitoring_input_entity" points to a binary sensor to control
when the alert flashes are enabled or disabled. Once they are enabled,
the lights will flash on motion. At 60 minutes, the lights will not flash
until the binary sensor is set to True again.

Example configuration:

---
motion_lights:
  module: motion_lights
  class: MotionLights
  light_entity: light.hallway_lights
  motion_sensor_entity: binary_sensor.ip_camera_motion
  monitoring_input_entity: input_boolean.monitor_motion

TODO:

- make the flashing better, make the strip itself do it instead of timers.
- parameterize flash color, number of pulses, etc.
- figure out a way to let the user customize the time period the alerting
  is on.

"""


class MotionLights(hass.Hass):
    light_state = {}
    monitoring = False

    def initialize(self):
        self.light_entity = self.args["light_entity"]
        self.motion_sensor_entity = self.args["motion_sensor_entity"]
        self.monitoring_input_entity = self.args["monitoring_input_entity"]

        self.listen_state(self.onMotion, self.motion_sensor_entity, new = "on")
        self.listen_state(self.onMonitoring, self.monitoring_input_entity)
        self.run_in(self.turnOffMonitoring, 3600)

    def turnOffMonitoring(self, kwargs):
        self.log("Time limit reached--disabling monitoring")
        self.turn_off(self.monitoring_input_entity)
        self.monitoring = False

    def onMonitoring(self, entity, attribute, old, new, kwargs):
        self.monitoring = "on" == new
        self.log("Monitoring: %s" % self.monitoring)

    def onMotion(self, entity, attribute, old, new, kwargs):
        if not self.monitoring:
            self.log("Not monitoring--ignoring motion")
            return

        self.light_state = self.get_state(self.light_entity, attribute = "all").copy()

        self.log(self.light_state)
        self.run_in(self.pulse, 0, pulse_count = 10)

    def pulse(self, kwargs):
        if kwargs['pulse_count'] > 0:
            if kwargs['pulse_count'] % 2 == 0:
                self._pulse1()
            else:
                self._pulse2()

            self.run_in(self.pulse, 1, pulse_count = kwargs['pulse_count'] - 1)
            self.log("pulsing: %d" % kwargs['pulse_count'])
        else:
            self.resetLight()

    def _pulse1(self):
        self.turn_on(self.light_entity, rgb_color = [255,0,0],
            white_value = 0,
            brightness = 255,
            transition = 0)

    def _pulse2(self):
        self.turn_on(self.light_entity, rgb_color = [255,255,255],
            white_value = 0,
            brightness = 255,
            transition = 0)

    def resetLight(self):
        if self.light_state["state"] == "on":
            self.log("resetting light state: %s" % self.light_state)
            self.turn_on(self.light_entity,
                brightness = self.light_state["attributes"]["brightness"],
                rgb_color = self.light_state["attributes"]["rgb_color"],
                white_value = self.light_state["attributes"]["white_value"])
        else:
            self.turn_off(self.light_entity)
