import appdaemon.plugins.hass.hassapi as hass
from datetime import time

"""
Turn on the space heater in the bedroom if the outside temperature is
less than "temp_threshold" degrees.

Example configuration:

---
bedroom_heater:
  module: bedroom_heater
  class: BedroomHeater
  heater_entity: switch.sonoff_1
  temp_sensor_entity: sensor.dark_sky_temperature
  temp_threshold: 50.0

TODO:

- parameterize the start/end times
"""

class BedroomHeater(hass.Hass):

    def initialize(self):
        self.heater_entity = self.args["heater_entity"]
        self.temp_sensor_entity = self.args["temp_sensor_entity"]
        self.temp_threshold = float(self.args["temp_threshold"])

        self.run_daily(self.startHeater, time(20, 0))
        self.run_daily(self.stopHeater, time(22, 30))

    def startHeater(self, kwargs):
        outdoorTemp = float(self.get_state(self.temp_sensor_entity))
        self.log("Outdoor temperature: %s" % outdoorTemp)

        if outdoorTemp < self.temp_threshold:
            self.log("Outdoor temperature: %.2f < %.2f, turning on heater" \
                % (outdoorTemp, self.temp_threshold))
            self.turn_on(self.heater_entity)

    def stopHeater(self, kwargs):
        self.turn_off(self.heater_entity)
