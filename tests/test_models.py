"""Tets for the ncei_access.models module."""
# from datetime import datetime # do I need this?
import unittest
from ncei_access.models import Station, Result

class TestStation(unittest.TestCase):
    def setUp(self):
        self.station = Station(
            name="Test Station",
            station_id="ID1",
            lat=40.0,
            lon=-110.0,
            data_types=[
                {"id": "TMAX", "startDate": "2000-01-01", "endDate": "2025-01-01"},
                {"id": "TMIN", "startDate": "2010-01-01", "endDate": "2025-01-01"},
            ],
        )

    def test_has_data_type_basic(self):
        self.assertTrue(self.station.has_data_type("TMAX"))
        self.assertFalse(self.station.has_data_type("PRCP"))

    def test_has_data_type_with_dates(self):
        self.assertTrue(self.station.has_data_type("TMAX", start_date="2010-01-01"))
        self.assertFalse(self.station.has_data_type("TMAX", start_date="1990-01-01"))
        self.assertTrue(self.station.has_data_type("TMAX", end_date="2025-01-01"))
        self.assertFalse(self.station.has_data_type("TMAX", end_date="2026-01-01"))
        self.assertTrue(self.station.has_data_type("TMAX", start_date="2000-01-01", end_date="2025-01-01"))

    def test_distance_to(self):
        # Should be zero if same point
        self.assertAlmostEqual(self.station.distance_to(40.0, -110.0), 0.0, places=5)
        # Should be positive for different point
        self.assertGreater(self.station.distance_to(41.0, -110.0), 0.0)

class TestResult(unittest.TestCase):
    def test_result_init(self):
        r = Result(200, message="ok", data=[{"foo": "bar"}])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.message, "ok")
        self.assertEqual(r.data, [{"foo": "bar"}])

if __name__ == "__main__":
    unittest.main()
