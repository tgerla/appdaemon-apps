"""
This is a generic timer app designed to emulate the mechanical plug-in timers
for lamps, heaters, etc. You can specify as many on/off events as you need,
down to a resolution of one minute.

When the app is restarted, it will figure out whether the switch is supposed
to be on or off based on the current time.

Example configuration:

generic_timer:
  module: generic_timer
  class: GenericTimer
  entries:
    - entity: switch.sonoff_3
      times:
        - ontime: "8:00"
          offtime: "10:00"
        - ontime: "20:00"
          offtime: "22:00"

periodic_timer:
  module: generic_timer
  class: PeriodicTimer
  switch_entity: switch.sonoff_3
  time_on: 60 # seconds
  interval: 1800 # every half hour



TODO:

- test multiple entities in one configuration
- additional testing for state restore on initialization
- abstract some logic out into functions and write tests
- handle a single ontime/offtime pair without a "times" list

"""

import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime

On = True
Off = False

class GenericTimer(hass.Hass):
    def initialize(self):
        for entry in self.args['entries']:
            entity = entry["entity"]

            times = []
            self.log(entry["times"])
            for t in entry["times"]:
                onTime = datetime.strptime(t["ontime"], "%H:%M").time()
                offTime = datetime.strptime(t["offtime"], "%H:%M").time()
                self.log("Entity %s on at %s, off at %s" %
                    (entity, onTime, offTime), level = "DEBUG")
                times.append((onTime, offTime))

                self.run_daily(self.entity_on, onTime, entity_id = entity)
                self.run_daily(self.entity_off, offTime, entity_id = entity)

            self.log("Times: %s" % times)

            # build a 2D array of on/off slots so we can figure out what
            # the correct state at initialization time should be
            hourSlots = []
            state = Off
            for hour in range(0, 24):
                minuteSlots = []
                for minute in range(0, 60):

                    for onTime, offTime in times:
                        if onTime.minute == minute and onTime.hour == hour:
                            state = On
                        if offTime.minute == minute and offTime.hour == hour:
                            state = Off
                    minuteSlots.append(state)
                hourSlots.append(minuteSlots)

            for x in hourSlots:
                self.log(x, level = "DEBUG")
            now = datetime.now()
            if hourSlots[now.hour][now.minute] == On:
                self.log("Initialize: turn on %s" % entity)
                self.turn_on(entity)
            else:
                self.log("Initialize: turn off %s" % entity)
                self.turn_off(entity)


    def entity_on(self, kwargs):
        self.log("Timer fired: turn on %s" % kwargs['entity_id'])
        self.turn_on(kwargs['entity_id'])

    def entity_off(self, kwargs):
        self.log("Timer fired: off %s" % kwargs['entity_id'])
        self.turn_off(kwargs['entity_id'])

###################

class PeriodicTimer(hass.Hass):
    time_on = 0
    interval = 0

    def initialize(self):
        self.switch_entity = self.args["switch_entity"]
        self.time_on = int(self.args["time_on"]) # seconds
        self.interval = int(self.args["interval"]) # seconds

        self.log("Turning off %s at start, waiting %d" % (self.switch_entity,
            self.interval))
        self.turn_off(self.switch_entity)
        self.run_in(self.turnOnSwitch, self.interval)

    def turnOnSwitch(self, kwargs):
        self.log("Turning on %s for %d seconds" % (self.switch_entity,
            self.time_on))
        self.turn_on(self.switch_entity)
        self.run_in(self.turnOffSwitch, self.time_on)

    def turnOffSwitch(self, kwargs):
        self.log("Turning off %s for %d seconds" % (self.switch_entity,
            self.interval))
        self.turn_off(self.switch_entity)
        self.run_in(self.turnOnSwitch, self.interval)
