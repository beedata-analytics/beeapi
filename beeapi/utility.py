import pandas as pd
import pytz

from beeapi import Client


class Utility:
    def __init__(self, config):
        self.config = config
        self.client = Client(self.config["beedata"])

    def post_measures(self, measures, id, measures_type, period, unit):
        measures["hour"] = pd.to_datetime(
            pd.to_datetime(measures["ts"]).dt.strftime("%Y-%m-%dT%H:00:00Z")
        )
        measures = (
            measures[["value", "hour"]]
            .groupby(["hour"])
            .sum()
            .reset_index()
            .to_dict("records")
        )

        if len(measures) > 0:
            data = {
                "deviceId": str(id),
                "meteringPointId": str(id),
                "readings": [
                    {
                        "type": measures_type,
                        "period": period,
                        "unit": unit,
                    }
                ],
                "measurements": [
                    {
                        "type": measures_type,
                        "timestamp": measure["hour"]
                        .astimezone(pytz.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "value": measure["value"],
                    }
                    for measure in measures
                ],
            }

            self.client.put_measures(data)
