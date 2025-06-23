"""Tests for the NceiAccessor class."""
import unittest
from unittest.mock import MagicMock, patch
from ncei_access.ncei_accessor import NceiAccessor
# from ncei_access.models import Station, Result # Do i need these imports?

class TestNceiAccessor(unittest.TestCase):
    def setUp(self):
        self.mock_adapter = MagicMock()
        self.accessor = NceiAccessor()
        self.accessor._rest_adapter = self.mock_adapter # pylint: disable=protected-access

    def test_get_daily_str_and_list(self):
        # Mock return value
        self.mock_adapter.get.return_value = MagicMock(data=[{"foo": "bar"}])
        # Single string
        result = self.accessor.get_daily("TMAX", "STATION1")
        self.assertEqual(result, [{"foo": "bar"}])
        # List of strings
        result = self.accessor.get_daily(["TMAX", "TMIN"], ["STATION1", "STATION2"])
        self.assertEqual(result, [{"foo": "bar"}])

    def test_get_daily_hilow(self):
        self.mock_adapter.get.return_value = MagicMock(data=[{"foo": "baz"}])
        result = self.accessor.get_daily_hilow("STATION1")
        self.assertEqual(result, [{"foo": "baz"}])

    @patch('ncei_access.ncei_accessor.Station')
    def test_stations_in_boundary(self, MockStation):
        # Simulate API response
        mock_station_data = [{
            "stations": [{"name": "Test", "id": "ID1", "dataTypes": []}],
            "location": {"coordinates": [1.0, 2.0]}
        }]
        self.mock_adapter.get.return_value = MagicMock(data=mock_station_data)
        MockStation.return_value = "station_obj"
        stations = self.accessor.stations_in_boundary(2, 1, 0, 3)
        self.assertEqual(stations, ["station_obj"])

if __name__ == "__main__":
    unittest.main()
