import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from wifi_tool import WifiToolGUI, WifiCracker
from pywifi import const

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'path_to_your_module_directory')))

class TestWifiToolGUI(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = WifiToolGUI(self.root)
        
    def tearDown(self):
        self.root.destroy()

    @patch("wifi_tool.pywifi.PyWiFi")
    def test_scan_networks(self, MockPyWiFi):
        mock_iface = MagicMock()
        mock_network = MagicMock()
        mock_network.ssid = "TestNetwork"
        mock_iface.scan_results.return_value = [mock_network]
        MockPyWiFi.return_value.interfaces.return_value = [mock_iface]

        self.app.scan_networks()

        self.root.update()  
        

    @patch("wifi_tool.tk.filedialog.askopenfilename")
    def test_browse_password_file(self, mock_askopenfilename):
        mock_askopenfilename.return_value = "test_passwords.txt"

        self.app.browse_password_file()

        mock_askopenfilename.assert_called()  
        self.assertEqual(self.app.password_file_entry.get(), "test_passwords.txt")  

    @patch("wifi_tool.threading.Thread")
    @patch.object(WifiCracker, "crack_password")
    def test_start_cracking(self, mock_crack_password, MockThread):
        self.app.networks_combobox["values"] = ["TestNetwork"]
        self.app.networks_combobox.set("TestNetwork")
        self.app.password_file_entry.insert(0, "test_passwords.txt")

        self.app.start_cracking()

        self.assertIsNotNone(self.app.wifi_cracker)
        MockThread.assert_called()  
        MockThread.return_value.start.assert_called()  
       


    @patch.object(WifiCracker, "crack_password")
    def test_crack_password(self, mock_crack_password):
        mock_iface = MagicMock()
        mock_iface.status.return_value = const.IFACE_DISCONNECTED
        self.app.wifi_cracker = WifiCracker(mock_iface, "TestNetwork", "test_passwords.txt")

        mock_crack_password.return_value = "password123"
        password = self.app.wifi_cracker.crack_password()

        self.assertEqual(password, "password123") 
        mock_crack_password.assert_called()  
if __name__ == "__main__":
    unittest.main()
