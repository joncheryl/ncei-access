"""
Includes dataType_ref and dataSet_ref objects.
"""

import json
from pathlib import Path

_data_path = Path(__file__).parent / "data" / "daily-summaries.json"

with _data_path.open("r", encoding="utf-8") as f:
    _data = json.load(f)
    _data = _data["dataTypes"]


class DataType:
    """Contains metadata for the different data types in the daily-summaries dataset.
    May include (but not necessarily) the following attributes:

    - id: The ID of the data type.
    - name: The name of the data type.
    - units: The units of the data type.
    - metricOutputUnits: The metric output units of the data type.
    - metricOutputPrecision: The precision of the metric output.
    - standardOutputUnits: The output units of the data type if requested in Imperial units.
    - standardOutputPrecision: The precision of the standard output if requested in Imperial units.
    - scaleFactor: The scale factor for the data type. Eg. if scaleFactor is 0.1, then the value is in tenths of the unit. If scaleFactor is 1, then the value is in the unit directly.
    - scaleWeight: The scale weight for the data type. ???
    """  # pylint: disable=line-too-long

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


_datasets_path = Path(__file__).parent / "data" / "datasets.json"

with _datasets_path.open("r", encoding="utf-8") as f:
    _datasets = json.load(f)


class DataSet:
    """Contains metadata for the different data sets in the Access API. Here we include
    the following attributes but they are not comprehensive:

    - id: The ID of the dataset.
    - name: The name of the dataset.
    - dataTypes: A list of data type IDs that are available in the dataset.
    """

    def __init__(self, d):
        self.id = d["id"]
        self.name = d.get("name")
        self.data_types = d.get("dataTypes", [])


dataSet_ref = {d["id"]: DataSet(d) for d in _datasets}
