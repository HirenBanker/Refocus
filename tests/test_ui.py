import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Kivy Window to avoid window creation
os.environ["KIVY_NO_WINDOW"] = "1"

from main import MainLayout, AccountPopup, RefocusApp
from kivy.uix.spinner import Spinner
from datetime import datetime, timedelta

class TestMainLayoutLogic(unittest.TestCase):
    def setUp(self):
        # Mock App.get_running_app
        self.app_patcher = patch('kivy.app.App.get_running_app')
        self.mock_get_app = self.app_patcher.start()
        
        self.app = RefocusApp()
        self.app.data_manager = MagicMock()
        self.app.blocking_service = MagicMock()
        self.app.blocking_service.is_active.return_value = False
        self.app.data_manager.get_blocked_sites.return_value = []
        self.app.data_manager.get_user.return_value = {"username": "TestUser", "email": "test@example.com"}
        
        self.mock_get_app.return_value = self.app
        
        # Initialize layout
        self.layout = MainLayout()

    def tearDown(self):
        self.app_patcher.stop()

    def test_set_timer(self):
        self.layout.set_timer(60)
        self.assertEqual(self.layout.selected_duration, 60)
        self.assertIn("60 minutes", self.layout.selected_label.text)

    def test_custom_timer_valid(self):
        self.layout.start_input.text = "10:00"
        self.layout.end_input.text = "11:00"
        self.layout.set_custom_timer(None)
        self.assertEqual(self.layout.selected_duration, 60)

    def test_add_site(self):
        self.layout.new_site_input.text = "test.com"
        self.layout.add_site(None)
        self.app.data_manager.add_site.assert_called_with("test.com")
        self.assertEqual(self.layout.new_site_input.text, "")

    def test_delete_site(self):
        self.layout.site_spinner.text = "test.com"
        self.layout.delete_site(None)
        self.app.data_manager.remove_site.assert_called_with("test.com")

    def test_toggle_blocking_start(self):
        self.app.blocking_service.is_active.return_value = False
        self.app.data_manager.get_blocked_sites.return_value = ["site1.com"]
        self.layout.selected_duration = 60
        
        # Mock block_until for wording check
        mock_until = datetime.now() + timedelta(minutes=60)
        self.app.blocking_service.get_block_until.return_value = mock_until
        until_str = mock_until.strftime("%H:%M")
        
        self.layout.toggle_blocking(None)
        
        self.app.blocking_service.start_blocking.assert_called_with(60, ["site1.com"], strict=True)
        self.assertIn("Status: Active", self.layout.status_label.text)
        self.assertEqual(self.layout.toggle_btn.text, f"blocked until {until_str}")

    def test_toggle_blocking_stop_success(self):
        self.app.blocking_service.is_active.return_value = True
        self.app.blocking_service.stop_blocking.return_value = True
        
        self.layout.toggle_blocking(None)
        
        self.app.blocking_service.stop_blocking.assert_called()
        self.assertIn("Status: Inactive", self.layout.status_label.text)

    def test_toggle_blocking_stop_strict_fail(self):
        self.app.blocking_service.is_active.return_value = True
        self.app.blocking_service.stop_blocking.return_value = False
        
        self.layout.toggle_blocking(None)
        
        self.app.blocking_service.stop_blocking.assert_called()
        self.assertIn("Status: Locked", self.layout.status_label.text)

    def test_account_popup(self):
        # Combined test to reduce instantiation issues
        self.app.data_manager.get_user.return_value = {"username": "TestUser", "email": "test@example.com", "phone": "12345"}
        popup = AccountPopup()
        self.assertEqual(popup.username_input.text, "TestUser")
        self.assertEqual(popup.phone_input.text, "12345")
        
        popup.username_input.text = "NewUser"
        popup.email_input.text = "new@example.com"
        popup.phone_input.text = "98765"
        popup.dismiss = MagicMock()
        
        popup.save_profile(MagicMock())
        self.app.data_manager.update_user.assert_called_with(username="NewUser", email="new@example.com", phone="98765")

if __name__ == '__main__':
    unittest.main()
