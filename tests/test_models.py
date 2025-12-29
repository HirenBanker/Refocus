import unittest
import os
import json
import shutil
from models import DataManager, DEFAULT_DATA

TEST_DATA_DIR = "tests/data"
TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, "test_user_data.json")

class TestDataManager(unittest.TestCase):
    def setUp(self):
        # Create test data directory
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
        # Initialize DataManager with test file
        self.dm = DataManager(data_file=TEST_DATA_FILE)

    def tearDown(self):
        # Clean up test data
        if os.path.exists(TEST_DATA_DIR):
            shutil.rmtree(TEST_DATA_DIR)

    def test_load_default_data(self):
        # Ensure file doesn't exist initially
        if os.path.exists(TEST_DATA_FILE):
            os.remove(TEST_DATA_FILE)
        
        dm = DataManager(data_file=TEST_DATA_FILE)
        self.assertEqual(dm.data, DEFAULT_DATA)
        self.assertTrue(os.path.exists(TEST_DATA_FILE))

    def test_add_site(self):
        self.dm.add_site("example.com")
        self.assertIn("example.com", self.dm.get_blocked_sites())
        
        # Verify persistence
        with open(TEST_DATA_FILE, 'r') as f:
            data = json.load(f)
        self.assertIn("example.com", data["blocked_sites"])

    def test_remove_site(self):
        self.dm.add_site("example.com")
        self.dm.remove_site("example.com")
        self.assertNotIn("example.com", self.dm.get_blocked_sites())

    def test_update_user(self):
        self.dm.update_user(username="NewUser", email="new@example.com", phone="123456789")
        user = self.dm.get_user()
        self.assertEqual(user["username"], "NewUser")
        self.assertEqual(user["email"], "new@example.com")
        self.assertEqual(user["phone"], "123456789")

if __name__ == '__main__':
    unittest.main()
