# John Sherrill
# June 2025
"""
Main class for accessing NCEI Access API.
"""

import logging
from typing import Union, List
from datetime import datetime, timedelta
from ncei_access.rest_adapter import RestAdapter

# from ncei_access.exceptions import NceiAccessException
from ncei_access.models import Result, Station


class NceiAccessor:
    """High level class to interact with NCEI Access API."""

    def __init__(self, logger: logging.Logger = None):
        self._rest_adapter = RestAdapter(logger=logger)
        self._logger = logger or logging.getLogger(__name__)

    def get_daily(
        self,
        data_types: Union[str, List[str]],
        stations: Union[str, List[str]],
        start: str = "2024-04-21",
        end: str = "2025-04-21",
    ) -> Result:
        """Obtain daily data from user specified stations (or just a single station)
        over the specified period of interest.

        :param data_types: data type(s) of interest. Can be a single string or a list of strings. See ncei_access.dataType_ref for available data types.
        :param stations: station id. Obtained from find_station function.
        :param start: beginning date of period of interest. See NCEI Access documentation for string format, defaults to "2024-04-21"
        :param end: end date of period of interest. See NCEI Access documentation for string format, defaults to "2025-04-21"
        :return: Daily highs and lows from station requested.
        """ # pylint: disable=line-too-long
        params = {
            "dataset": "daily-summaries",
            "dataTypes": [data_types] if isinstance(data_types, str) else data_types,
            "stations": [stations] if isinstance(stations, str) else stations,
            "startDate": start,
            "endDate": end,
        }
        temps = self._rest_adapter.get(ep_params=params)

        return temps.data

    def get_daily_hilow(
        self, stations, start: str = "2024-04-21", end: str = "2025-04-21"
    ) -> Result:
        """Obtain daily high and low temperatures from one user specified station over
        period of interest. For convenience, this is a wrapper around get_daily.

        :param stations: station id. Obtained from find_station function.
        :param start: beginning date of period of interest. See NCEI Access documentation for string format, defaults to "2024-04-21"
        :param end: end date of period of interest. See NCEI Access documentation for string format, defaults to "2025-04-21"
        :return: Daily highs and lows from station requested.
        """ # pylint: disable=line-too-long

        return self.get_daily(
            data_types=["TMAX", "TMIN"],
            stations=stations,
            start=start,
            end=end,
        )

    def find_closest_station(
        self, lat, lon, data_type: str = "", start_date: str = "", end_date: str = ""
    ) -> Station:
        """Find closest station to provided coordinates.

        :param lat: Latitude (decimal format)
        :param lon: Longitude (decimal format)
        :param data_type: Optional data type to filter stations by.
        :param start_date: Optional start date to filter stations by.
        :param end_date: Optional end date to filter stations by.
        :return: Station object containing name, station_id, lat, lon.
        """

        area_width = 0.5
        attempt = 0

        while attempt < 10:
            attempt += 1
            self._logger.debug(
                msg=f"Attempt {attempt} to find closest station to lat={lat}, lon={lon}."  # pylint: disable=line-too-long
            )

            # Find all stations within a bounding box around the provided coordinates.
            stations = self.stations_in_boundary(
                north=lat + area_width,
                west=lon - area_width,
                south=lat - area_width,
                east=lon + area_width,
            )

            # Only keep stations with data type of interest, if provided.
            if data_type:
                stations = [
                    station
                    for station in stations
                    if station.has_data_type(data_type, start_date, end_date)
                ]
            self._logger.debug(
                msg=f"Found {len(stations)} stations within bounds: {area_width} degrees around lat={lat}, lon={lon}."  # pylint: disable=line-too-long
            )
            # If no stations found, increase area width and try again.
            if not stations:
                self._logger.debug(
                    msg=f"No stations found within bounds: {area_width} degrees around lat={lat}, lon={lon}. "  # pylint: disable=line-too-long
                    f"Increasing area width to {area_width * 1.5}."
                )
                area_width = area_width * 1.5
                continue
            # If stations found, sort by distance and return closest.
            else:
                self._logger.debug(
                    msg=f"Found {len(stations)} stations within bounds: {area_width} degrees around lat={lat}, lon={lon}. "  # pylint: disable=line-too-long
                    f"Returning closest station."
                )
                # Sort stations by distance to provided coordinates.
                stations.sort(key=lambda s: s.distance_to(lat, lon))
                return stations[0]
        # If no stations found after 10 attempts, return None.
        self._logger.error(msg="No stations found within bounds after 10 attempts.")
        return None

    def stations_in_boundary(
        self, north: float, west: float, south: float, east: float
    ) -> list:
        """Find all stations within bounds that have at least some data within the last
        100 days.

        :param lat_N: _description_
        :param lon_W: _description_
        :param lat_S: _description_
        :param lat_E: _description_
        :return: list of stations
        """

        recently = datetime.now() - timedelta(days=100)
        params = {
            "dataset": "daily-summaries",
            "startDate": recently.strftime("%Y-%m-%d"),
            "bbox": f"{north},{west},{south},{east}",
            "limit": 1000,
        }

        station_results = self._rest_adapter.get(
            endpoint="search/v1/data", ep_params=params
        )
        station_results = station_results.data

        stations = []

        # Assuming we're getting something back here.
        for station in station_results:
            stations.append(
                Station(
                    name=station["stations"][0]["name"],
                    station_id=station["stations"][0]["id"],
                    lat=station["location"]["coordinates"][1],
                    lon=station["location"]["coordinates"][0],
                    data_types=station["stations"][0]["dataTypes"],
                )
            )

        return stations

    def find_station(self, station_id: str) -> Station:
        """Get a station by its ID.

        :param station_id: NCEI/NOAA? ID for station
        :return: Station object with name, station_id, lat, lon, and data_types.
        """
        params = {
            "dataset": "daily-summaries",
            "stations": station_id,
            "limit": 1,
        }

        station_results = self._rest_adapter.get(
            endpoint="search/v1/data", ep_params=params
        )
        station_results = station_results.data

        if not station_results or not station_results[0]["stations"]:
            self._logger.error(f"No station found with ID {station_id}.")
            return None

        return Station(
            name=station_results[0]["stations"][0]["name"],
            station_id=station_results[0]["stations"][0]["id"],
            lat=station_results[0]["location"]["coordinates"][1],
            lon=station_results[0]["location"]["coordinates"][0],
            data_types=station_results[0]["stations"][0]["dataTypes"],
        )
