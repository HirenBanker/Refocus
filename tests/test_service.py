import unittest
from datetime import datetime, timedelta
from blocking_service import BlockingService
import time

class TestBlockingService(unittest.TestCase):
    def setUp(self):
        self.service = BlockingService()

    def test_start_blocking(self):
        sites = ["example.com"]
        self.service.start_blocking(duration_minutes=1, sites=sites)
        self.assertTrue(self.service.is_active())
        self.assertEqual(self.service._blocked_sites, sites)

    def test_stop_blocking(self):
        self.service.start_blocking(duration_minutes=1, sites=["example.com"])
        self.service.stop_blocking()
        self.assertFalse(self.service.is_active())
        self.assertEqual(self.service._blocked_sites, [])

    def test_expiration(self):
        # Start blocking for a very short duration (e.g., 0 minutes/seconds)
        # Since we can't easily mock datetime without external libs or complex patching in this simple setup,
        # we will manually set the _block_until to the past.
        self.service.start_blocking(duration_minutes=10, sites=["example.com"])
        self.service._block_until = datetime.now() - timedelta(seconds=1)
        
        self.assertFalse(self.service.is_active())

if __name__ == '__main__':
    unittest.main()
