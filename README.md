<img align=right src="./image/ha.png" width="100"/>

# **Home assistant**

Open source home automation that puts local control and privacy first. Powered by a worldwide community of tinkerers and DIY enthusiasts. Perfect to run on a Raspberry Pi or a local server.

## Vision

The home automation should help and simplify daily routines, provide important information relevant for daily life. It should be easily extensible and accessible to all family members. The focus is on local control instead of cloud based solution.  

## Climate Control

The climate control was the first reason to start with home automation at all. To tackle the humidity problem in our apartment, I build a simple solution based on MQTT and Python script running on Raspberry Pi Zero W. This node was gathering data from temperature and humidity sensor DHT22 and carbon dioxide (co2) from MH-Z19 sensor. I risked that and bought it from China. It is pretty sufficient for ventilation control (not speaking about absolute accuracy, since it is not so important). Since that time, I only integrated it as part of HA using MQTT sensor integration. In future it would be great to find a better looking and more professional solution.

Shelly1 relay is used for switching of an industrial fan in bathroom and toilet. There is a logic that turns the fan on, if co2 or humidity level goes above a given treshold.
The limits are now set for for co2:
<ul>
<li>if co2 > 1000 ppm</li>
</ul>

The limit is set to a maximum recomended value for indoor areas. An experiment has shown that during night the concentration of co2 in bedroom can easily go over 2000 ppm. Using this fan control it is possible to keep is stable around 1000 ppm with windows closed. Note that the bathroom fan is not powerfull enough to exchange air in the whole flat fast enough. 

| Shelly1 | CO2 Sensor MH-Z19 | DHT22 Sensor | MQTT |  
| --- | --- | --- | --- |
| <img src="./image/shelly1.jpg" width="200"/> | <img src="./image/mh-z19.jpg" width="200"/></a> | <img src="./image/dht22.jpg" width="200"/></a> | <img src="./image/mqtt.png" width="200"/> |

## Safety first

After our old smoke detector had few false alarms, it was replaced by a smart solution - Fibaro smoke detector. It is connected over z-wave communication protocol (currently the only device). The only fear I have is that the system is not well tested, z-wave is not very user friendly for debugging (unlike zigbee with deconz events).

To minimize problems of water leaks, there is placed AQUARA water detector behind wash machine. Of course doesn't prevent damage, but at least inform us over notification service with highest priority. Important e.g. when we are on shopping or somewhere nearby. There is a plan to combine it with automatic closing of valves, but so far I didn't find a fitting solution. Sensor uses a Zigbee connection.

| Fibaro smoke detector | AQUARA water detector | z-wave |  
| --- | --- | --- |
| <img src="./image/fibaro_smoke_detector.jpg" width="200"/> | <img src="./image/aquara-water.jpg" width="200"/></a> | <img src="./image/z-wave.png" width="200"/> |

## Hardware and connectivity

Home Assistant runs on Raspberry Pi, which is nice, versatile and low power device.
Zigbee devices are connected to Conbee II Zigbee gateway and Z-Wave devices to Aeotec Z-Stick gen5 - both are USB sticks.
There is also MQTT server running.

| Raspberry Pi 3B | Conbee-II | Aeotec Z-Stick gen5 | Raspberry Pi Zero W |  
| --- | --- | --- | --- |
| <img src="./image/pi-3b.jpg" width="200"/> | <img src="./image/conbee2.png" width="200"/></a> | <img src="./image/aeotec-zstick.jpg" width="200"/></a> | <img src="./image/pi-zero-w.jpg" width="200"/> |

## Software

Home Assistant Core runs in Docker container installed on Raspbian. Z-Stick must be provided to docker contained as a device. 
Great thing is that Docker runs on many platforms, e.g. Windows and one can debug HA pretty fast. Reload time of HA is then just a few seconds.
A simple bash script is used to do all steps to update docker image automaticaly (it takes some time on RPI):

```sh
docker stop home-assistant
docker rm home-assistant
docker pull homeassistant/raspberrypi3-homeassistant:stable
docker run -d --net=host --device=/dev/serial/by-id/usb-0658_0200-if00 --name home-assistant -v /home/pi/homeassistant:/config --restart=always homeassistant/raspberrypi3-homeassistant:stable
docker start home-assistant
```

Python is used as a programming language for custom components and more. It is not the language I would know that much, so it is a limitation for me to overcome some problems and do bigger customizations. I just need to google sometimes :)
Before it has been switched to Docker, HA run in Python virtual environent. It was OK, but it caused always troubles with missing dependencies. With one of the recent HA release it crashed completely and I moved to Docker.

The source code is versioned with GIT version control. Pushing the sources to GitHub was straightforward and the only issue was how to hide confidential files (secrets). There is an elegant solution <a href="https://git-secret.io/">git secret</a> using RSA encryption.
The following commands can be used to encrypt and decrypt of confidential files.

```sh
git secret hide -m
git secret reveal
```

| Home Assistant | Docker | Git | Python |
| --- | --- | --- | --- |
| <img src="./image/ha.png" width="200"/> | <img src="./image/docker.png" width="200"/></a> | <img src="./image/git.png" width="200"/></a> | <img src="./image/python.png" width="200"/></a> |

## Google home

Google assistant is a cool device, with quite nice sound and voice control. It is most used to play music over Spotify and for various questions (unfortunately only in EN language and not localized). Commonly asked question: weather forecast, travel time to work, play some music and more :) 

Chromecast is connected to the TV, but actualy not so often used. The TV doesn't support power commands from HDMI devices and there is no logic implemented to remotely select input devices at this moment.

| Google Nest Mini 2.gen  | Google assistant | Google Chromecast 3 |
| --- | --- | --- |
| <img src="./image/google_nest_mini.jpg" width="200"/> | <img src="./image/google_assistant.jpg" width="200"/></a> | <img src="./image/google-chromecast.jpg" width="200"/></a> |

## Vacuum cleaner

Our best friend at our home is the robotic vacuum cleaner. Xiaomi vacuum is a solid devices for a reasonable price. It could work out of the box with original SW/app but the integration into HA gives more flexibility.
The cleaning process starts only if:
<ul>
<li>no one is at home</li>
<li>not within quiet hours</li>
<li>time since last cleaning > 1 day</li>
</ul>

It can be triggered manually.
I created a nice lovelace dashboard card with the basic controls. Inspired at <a href="https://community.home-assistant.io/t/xiaomi-vacuum-cleaner-card/64456/">Xiaomi Vacuum cleaner card</a> in the community forum.
Nice feature is zone clean up. There are preconfigured zones, so it is possible to do cleaning only in a specified area.
The zone definition is quite trial and error process. It consisted of sending a zone coordinates over developer service call in HA and visual control on the mobile app.
At the end a user can select a room and start cleaning there.

The biggest pain point is the connection *token* needed by the xiaomi_miio integration.
It is not easily accessible and there are principally two ways how to get it:
<ul>
<li>Send a special UDP packet and capture the traffic using e.g. wireshark</li>
<li>Read the token from a specific mobile app version</li>
</ul>

For me the first way didn't work so I will describe the second approach:
<ul>
<li>Intall Mi Home 5.4.49 (another phone if you like)</li>
<li>Select a region - russian server works</li>
<li>Locate a text file in files /Smarthome/logs... and search for *token*</li>
</ul>

Just keep in mind that this token is valid only till next FW update or WIFI reset on the device. Maybe also if you connect it to a different network.

| Xiaomi Vacuum |
| --- |
| <img src="./image/xiaomi_vacuum.jpg" width="200"/> |

## Lighting

The biggest part of the automation is regarding lights. Automatic switching of lights after sunset and in frequent areas based on motion sensor.
All it started with Philips Hue starter kit and now it is all migrated to the local solution using Conbee II Zigbee gateway.

Here you can see an example of non-conceptual home automation growth. Fortunately it doesn't matter as all runs on Zigbee. There are devices from various manufactures, because have only Hue devices is quite expensive. The best experience I have with Hue. With others were observed some small issues as needed reset of Mi motion sensor and strange battery readings from IKEA devices. But in most application the benefit/cost ratio is much higher.

Nice feature is turning on the light after sun set.
After some experiments I found the most fitting setting of Sun elevation < 2°.
If the sun falls below horizon and is below this angle, it is a good time to turn on the defined lights (e.g. lamp in living room). One can understand this also as kind of security functions.

### Light bulbs

There are Hue white and Tradfri dimmable bulbs in the hall and service rooms, small 5W RGBs in decorative lamps and Hue play behind the computer monitor. 

| Hue White 9W E27 | Immax Neo 5W RGB E14 | Tradfri E27 806lm | Hue play |
| --- | --- | --- | --- |
| <img src="./image/philips-hue-white.jpg" width="200"/> | <img src="./image/immax-neo-5W.jpg" width="200"/></a> | <img src="./image/tradfi_bulb.jpg" width="200"/></a> | <img src="./image/philips-hue-play.jpg" width="200"/></a> |

### Remote controls

A disadvantage if you use these devices without an App is that you must implement an automation for it. So there is an automation handling all the events using the sequences. It was finally possible to have only one automation per remote control.

| Hue Dimmer | Tradfri remote | Tradfri Dimmer |
| --- | --- | --- |
| <img src="./image/philips-hue-dimmer.jpg" width="200"/> | <img src="./image/tradfri-remote.jpg" width="200"/></a> | <img src="./image/tradfri-dimmer.jpg" width="200"/></a> |

### Motion sensors

There are two motion sensors placed on frequent areas. One is in the entrance hall and one on the toilet.
The automation is configured to set the brightness to the minimum level in the night.

| Hue Motion | Mi Motion | Tradfri motion |
| --- | --- | --- |
| <img src="./image/philips-hue-move.jpg" width="200"/> | <img src="./image/xiaomi-mi-motion.jpg" width="200"/></a> | <img src="./image/tradfri-sensor-move.jpg" width="200"/></a> |

### Switches

The following devices use a WIFI connection. This appeared to be a mistake and they are going to be replaced by Zigbee solution. Note that they support only 2.4Ghz and are cloud based. Thanks to <a href="https://github.com/AlexxIT/SonoffLAN">Sonoff LAN</a> custom component it works great, but still not working if wifi is down.

On the other hand using the basic switch I have made 2 lamps "smart" and controllable.
The wall switch is located in bedroom and 3 touch buttons serve to various purposes:
<ul>
<li>Button 1: ceiling light in bedroom</li>
<li>Button 2: lamp in bedroom</li>
<li>Button 3: turn off all light</li>
</ul>

The third button is used to turn all the lights off, but even more is possible regarding the night mode.

| Sonoff TX-3 | Sonoff Basic |
| --- | --- |
| <img src="./image/sonoff-T1-EU-TX-3.jpg" width="200"/> | <img src="./image/sonoff-basic-zbr3.jpg" width="200"/></a> |

## Notifications

HA is sending notifications as results of automation procedures, sensors, warnings and emergency states.
The <a href="https://www.home-assistant.io/integrations/pushover">Pushover</a> service is a platform for the notify component. This allows integrations to send messages to the user using Pushover.

It has many features as priority setting, different tones and url links.
For low prio messages a user gets only notification without sound, for normal priority it sounds like a standard message and emergency priority must be confirmed by the user.
The ammount of messages in limited to 5000 and you must purchase the mobile app for a small amount (it's worth it in my opinion).

## Other features

In the case of missing or not fitting functionality I was forced to implement custom component or update existing one.
Some examples are below.

### School news

I implemented a custom component basically from scratch. It accesses a specific webpage of elementary school and reads articles. It is not a rocket science code, but works. We are notified if there is a new article on the school webpage.

### Stock price tracking

The aim was to use <a href="https://www.home-assistant.io/integrations/alpha_vantage">Alpha Vantage</a> integration, but it doesn't provide intraday time series data for (some) European indexes. I modified it so it uses only global quote data, but works for the requested companies.

### Other noteworthy features

<ul>
<li>Sending info about new Home Assistant releases</li>
<li>Notification in case of problems with vacuum cleaner</li>
<li>Notification about air pollution levels based on <a href="https://www.home-assistant.io/integrations/waqi">WAQI</a> integration</li>
</ul>

## Final thoughts

I personaly find it great that, there is such a big community around HA, great source of inspiration and I would also like to contribute at least of sharing my concept of home automation. It is not that easy sometimes, requires a lot of time, trial and error, but it is still moving forward and new great features are comming in every release.
