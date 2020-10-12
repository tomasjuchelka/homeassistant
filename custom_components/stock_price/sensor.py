"""Stock price tracker integration
to use, add something like this to HA config:
sensor:
  - platform: stock_price
    api_key: !secret alpha_vantage_api_key
    symbols:
      - symbol: SIE.DEX
        currency: EUR
        name: Siemens
"""


from datetime import timedelta
import logging
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_CURRENCY, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

CONF_SYMBOL = "symbol"
CONF_SYMBOLS = "symbols"

ICONS = {
    "BTC": "mdi:currency-btc",
    "EUR": "mdi:currency-eur",
    "GBP": "mdi:currency-gbp",
    "INR": "mdi:currency-inr",
    "RUB": "mdi:currency-rub",
    "TRY": "mdi:currency-try",
    "USD": "mdi:currency-usd",
}

SCAN_INTERVAL = timedelta(minutes=60)

SYMBOL_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SYMBOL): cv.string,
        vol.Optional(CONF_CURRENCY): cv.string,
        vol.Optional(CONF_NAME): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_SYMBOLS): vol.All(cv.ensure_list, [SYMBOL_SCHEMA]),
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Alpha Vantage sensor."""
    
    symbols = config.get(CONF_SYMBOLS, [])

    if not symbols:
        msg = "No symbols configured."
        hass.components.persistent_notification.create(msg, "Sensor Stock price tracker")
        _LOGGER.warning(msg)
        return

    dev = []
    for symbol in symbols:
        dev.append(AlphaVantageSensor(symbol))

    add_entities(dev, True)
    _LOGGER.debug("Setup completed")


class AlphaVantageSensor(Entity):
    """Representation of a Alpha Vantage sensor."""

    def __init__(self, symbol):
        """Initialize the sensor."""
        self._symbol = symbol[CONF_SYMBOL]
        self._name = symbol.get(CONF_NAME, self._symbol)
        self.values = None
        self._unit_of_measurement = symbol.get(CONF_CURRENCY, self._symbol)
        self._icon = ICONS.get(symbol.get(CONF_CURRENCY, "USD"))

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.values["Global Quote"]['05. price']

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self.values is not None:
            return self.values["Global Quote"]

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    def update(self):
        """Get the latest data and updates the states."""
        _LOGGER.debug("Requesting new data for symbol %s", self._symbol)
        try:
            self.values = requests.get("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" + self._symbol + "&apikey=" + CONF_API_KEY).json()
            _LOGGER.debug("Received new values for symbol %s", self._symbol)
        except:
            _LOGGER.error("Request failed for symbol %s", self._symbol)