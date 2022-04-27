"""School Sensor integration
to use, add something like this to HA config:
sensor:
 - platform: school
   name: School news
   url: "https://www.zschvaleticka.cz"
"""


import logging
import sys
import voluptuous as vol
from datetime import timedelta, datetime
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.util import Throttle
from homeassistant.const import CONF_NAME, CONF_URL

import requests

MIN_TIME_BETWEEN_SCANS = timedelta(seconds=10800)
_LOGGER = logging.getLogger(__name__)

DOMAIN = "school"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_URL): cv.string
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    conf_name = config.get(CONF_NAME)
    conf_url = config.get(CONF_URL)
    ents = []
    ents.append(School(hass, conf_name, conf_url))
    add_entities(ents)

class School(BinarySensorEntity):

    def __init__(self, hass, name, url):
        """Initialize the sensor."""
        self.hass = hass
        self._name = name
        self.url = url
        self.header = "N/A"
        self.link = "N/A"
        self.last_link = "N/A"
        self.initialize(False)
        self.update()

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def icon(self):
        return "mdi:school-outline"

    @property
    def is_on(self):
        """Return entity state."""
        if self.link == self.last_link:
            return False
        else:
            self.last_link = self.link
            return True

    @property
    def extra_state_attributes(self):
        attributes = {}
        attributes['header'] = self.header
        attributes['link'] = self.link
        return attributes

    @property
    def should_poll(self):
        return True

    # Parse title
    def _get_title(self, t):
        line = t[t.find("<h3>")+4:t.find("</h3>")]
        return line

    # Parse path to article
    def _get_path(self, t):
        path = t[t.find("<a href")+9:t.find("\">")]
        return path

    def get_url_content(self):
        url_link = self.url + "/clanky"
        try:
            req = requests.get(url_link)
            content = req.content.decode('utf8')
            return content
        except:
            LOGGER.error("Page not found: " + sys.exc_info()[0])
            return ""

    def initialize(self, rest):
        content = self.get_url_content()
        listx = content.splitlines()
        for w in range(len(listx)):
            if listx[w].find("h3") > 0:
                if rest is False:
                    self.header = self._get_title(listx[w])
                else:
                    self.header = "Došlo k aktualizaci článků na webu školy. Restart na nejnovější článek."
                self.link = self.url + self._get_path(listx[w])
                self.last_link = self.link
                break

    @Throttle(MIN_TIME_BETWEEN_SCANS)
    def update(self):
        content = self.get_url_content()
        if content == "":
            return
        listx = content.splitlines()
        path = ""
        i = 0
        for w in range(len(listx)):
            if listx[w].find("h3") > 0:
                path = self._get_path(listx[w])
                if self.url + path == self.last_link:
                    break
                if i == 1:
                    self.initialize(True)
                    break
                self.header = self._get_title(listx[w])
                self.link = self.url + path
                _LOGGER.info("link: " + self.link)
                i = i + 1
        if path == "":
            self.header = "Stránka nenalezena nebo neobsahuje žádné informace."
            self.link = self.url + "/clanky"