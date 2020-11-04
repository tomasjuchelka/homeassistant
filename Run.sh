#!/bin/sh

docker ps
docker stop home-assistant
docker rm home-assistant
docker pull homeassistant/raspberrypi4-homeassistant:stable
docker run -d --net=host --device=/dev/serial/by-id/usb-0658_0200-if00 --name home-assistant -v /home/pi/homeassistant:/config --restart=always homeassistant/raspberrypi4-homeassistant:stable
docker start home-assistant