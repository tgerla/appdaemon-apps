# appdaemon-apps
These are some apps written for Home Assistant using the AppDaemon framework. I noticed there were not too many example AppDaemon apps out there yet, so I thought I would share my own. I hope you find them useful!

[bedroom_heater.py](bedroom_heater.py) -- This app turns on a space heater downstairs in the bedroom at 8PM, but only if the outdoor temperature is less than 50F.

[motion_lights.py](motion_lights.py) -- This app flashes a strip of RGB LED lights in my hallway red and white if motion is sensed on my entryway camera.

[generic_timer.py](generic_timer.py) -- This app is intended to implement a simple plug-in mechanical timer, with multiple on/off events per switch per 24 hours, and knows how to determine whether the switch should be on or off
at initialization, based on the current time.
