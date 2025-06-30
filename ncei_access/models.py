"""
Classes that organize the outputs of functions into defined objects.
"""

from typing import List, Dict
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


class Result:
    """The formatted version of what we get back from the low level request.get()"""

    def __init__(self, status_code: int, message: str = "", data: List[Dict] = None):
        """
        :param status_code: Standard HTTP Status code
        :param message: Human readable result, defaults to ""
        :param data: dict or list of dicts, defaults to None
        """
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []


class Station:
    """Class representing a weather station with all the details. It's the returned
    object from the find_station function"""

    def __init__(
        self,
        name: str = "",
        station_id: str = "",
        lat: float = 0.0,
        lon: float = 0.0,
        data_types: list = None,
    ):
        """
        :param name: Name of station
        :param station_id: NCEI/NOAA? ID for station
        :param lat: Latitude of station. Decimal format.
        :param lon: Longitude of station. Decimal format.
        :param dataTypes: Dict of dataTypes reported with a tuple for each (startDate, endDate)
        """  # pylint: disable=line-too-long
        self.name = name
        self.station_id = station_id
        self.lat = lat
        self.lon = lon
        self.data_types = data_types

    def has_data_type(
        self, data_type: str, start_date: str = None, end_date: str = None
    ) -> bool:
        """Return true if data_type of interest is recorded at station and if optional
        start and/or end dates are passed, return true if period of record for data_type
        is equal to or excedes start and/or end dates. Return false otherwise.

        :param data_type: dataType of interest
        :param start_date: data_type records should begin on or before start_date, defaults to None
        :param end_date: data_type records should end on or after end_date, defaults to None
        :return: boolean
        """  # pylint: disable=line-too-long
        type_dict = next((d for d in self.data_types if d["id"] == data_type), None)

        if not type_dict:
            return False

        if start_date:
            start_dt = datetime.fromisoformat(start_date.upper())
            type_start = datetime.fromisoformat(type_dict["startDate"])
            if start_dt < type_start:
                return False

        if end_date:
            end_dt = datetime.fromisoformat(end_date.upper())
            type_end = datetime.fromisoformat(type_dict["endDate"])
            if end_dt > type_end:
                return False

        return True

    def distance_to(self, lat: float, lon: float) -> float:
        """Calculate distance to provided coordinates from station using the haversine
        formula.

        :param lat: Latitude (decimal format)
        :param lon: Longitude (decimal format)
        :return: Distance in kilometers.
        """

        r = 6371.0  # Earth radius in kilometers
        lat1 = radians(self.lat)
        lon1 = radians(self.lon)
        lat2 = radians(lat)
        lon2 = radians(lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = r * c
        return distance

    def elevation(
        self,
        start_date: str = None,
        end_date: str = None,
    ) -> float:
        """Return the elevation of the station in meters. If start and/or end dates are
        provided, return the elevations if it's recorded during that period. If no dates are
        provided, return the most recent elevation record. This is actually kindof a hack
        because the NCEI API doesn't seem to include station elevation in the station
        metadata but it *is* recorded as a daily data type. So we just get the daily
        elevation data and return the most-ish recent record or all records if dates are
        provided.

        :param start_date: Optional start date to check for elevation records, defaults to '2015-01-01'
        :param end_date: Optional end date to check for elevation records, defaults to '2025-01-01'
        :return: Elevation in meters.
        """  # pylint: disable=line-too-long

        # Importing here to avoid circular import issues
        from ncei_access import ncei_accessor as na

        ncei_db = na.NceiAccessor()

        elevation_data = ncei_db.get_daily(
            data_types="ELEVATION",
            stations=self.station_id,
            start=start_date if start_date else "2015-01-01",
            end=end_date if end_date else "2025-01-01",
        )

        if start_date or end_date:
            return [
                {"DATE": x.get("DATE"), "ELEVATION": float(x.get("ELEVATION"))}
                for x in elevation_data
            ]

        return float(elevation_data[-1].get("ELEVATION"))
