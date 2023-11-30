import os
import logging
from beeapi import __version__, Client

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

def test_version():
    assert __version__ == "0.2.0"



config = {
		"company_id": os.getenv("COMPANY_ID", None),
		"auth": {
			"username": os.getenv("USERNAME", None),
			"password": os.getenv("PASSWORD", None),
			"cert_file": os.getenv("CERT_FILE", None),
			"key_file": os.getenv("KEY_FILE", None)
		},
		"endpoints": {
			"contracts": "/v1/contracts",
			"measures": "/v1/amon_measures",
			"tertiary": "/v1/tertiary_amon_measures",
			"tou": "/v1/residential_timeofuse_amon_measures"
		},
		"base_url": os.getenv("BEEACTIVA_URL", "https://devapi.beedataanalytics.com")
	}


data = {
  "measurements":
  [
    {
      "timestamp": "2013-10-11T16:37:05Z",
      "type": "electricityConsumption",
      "value": 7.0
    },
    {
      "timestamp": "2013-10-11T16:37:05Z",
      "type": "electricityKiloVoltAmpHours",
      "value": 11.0
    }
  ],
  "meteringPointId": "c1759810-90f3-012e-0404-34159e211070",
  "readings":
  [
    {"type": "electricityConsumption", "period": "INSTANT", "unit": "kWh"},
    {"type": "electricityKiloVoltAmpHours", "period": "INSTANT", "unit": "kVArh"}
  ],
  "deviceId": "c1810810-0381-012d-25a8-0017f2cd3574",
  "contractId": "c18108104"
}

import requests

client = Client(config)

try:
    response = client.put_measures(data)
    response.raise_for_status()
    print(f"response {response}")
except requests.exceptions.HTTPError as e:
    print(f"error {e}")
    raise

