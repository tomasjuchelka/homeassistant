#!/bin/sh

docker ps
docker stop home-assistant
docker rm home-assistant
docker pull homeassistant/raspberrypi4-homeassistant:stable
docker run -d --net=host --name home-assistant -v /home/pi/docker/homeassistant:/config -v /home/pi/media:/media -v /etc/localtime:/etc/localtime:ro --restart=always homeassistant/raspberrypi4-homeassistant:stable
docker start home-assistant
docker image prune -f