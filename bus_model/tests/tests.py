import unittest
from bus_model.app.gtfsr import GTFSR

class GTFSRTest(unittest.TestCase):
    def setUp(self):
        """Creates an instance of the GTFSR class."""
        self.instance = GTFSR()
    
    def test_fetch_vehicles(self):
        """Tests that the classmethod fetch_vehicles returns a dict."""
        self.assertIsInstance(GTFSR.fetch_vehicles(), dict)
    
    def test_fetch_trip_updates(self):
        """Tests that the classmethod fetch_trip_updates returns a dict."""
        self.assertIsInstance(GTFSR.fetch_trip_updates(), dict)

    def test_fetch_gtfsr(self):
        """Tests that the classmethod fetch_gtfsr returns a dict."""
        self.assertIsInstance(GTFSR.fetch_gtfsr(), dict)


if __name__ == "__main__":
    unittest.main()