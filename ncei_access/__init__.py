"""Just creating the dataType_ref object here for convenience later."""

import json
from pathlib import Path

_data_path = Path(__file__).parent / "data" / "daily-summaries.json"

with _data_path.open("r", encoding="utf-8") as f:
    _data = json.load(f)
    _data = _data["dataTypes"]


class DataType:
    """Convenience? class for storing info about the different data types in the
    daily-summaries dataset.
    """

    def __init__(self, d):
        self.id = d["id"]
        self.name = d.get("name")
        self.units = d.get("units")
        self.metric_output_units = d.get("metricOutputUnits")
        self.metric_output_precision = d.get("metricOutputPrecision")
        self.standard_output_units = d.get("standardOutputUnits")
        self.standard_output_precision = d.get("standardOutputPrecision")
        self.scale_factor = d.get("scaleFactor")
        self.scale_weight = d.get("scaleWeight")


dataType_ref = {d["id"]: DataType(d) for d in _data}
