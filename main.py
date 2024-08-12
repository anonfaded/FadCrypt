import os
import json
import threading
import subprocess
import time
import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag
import psutil
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog, PhotoImage
import winreg
import signal
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
import sys
import base64
from cryptography.fernet import Fernet
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tkinterdnd2 import TkinterDnD, DND_FILES  # Import the tkinterdnd2 module
import ctypes
from ttkbootstrap import Style
from PIL import Image, ImageTk

# Embedded configuration and state data
embedded_config = {
    "applications": []
}

embedded_state = {
    "unlocked_apps": [
        "FreeTube.exe"
    ]
}


class AppLockerGUI:
    def __init__(self, master):
        self.master = master
        
        self.master.title("FadCrypt")
        self.master.geometry("600x450") # Adjusted size to accommodate new tabs
        self.app_locker = AppLocker(self)

        
        # Ensure the settings file is correctly initialized
        self.settings_file = os.path.join(self.app_locker.get_fadcrypt_folder(), 'settings.json')
        self.lock_tools_var = tk.BooleanVar(value=True)  # Default value is True

        self.set_app_icon()  # Set the custom app icon
        self.create_widgets()
        self.load_settings()  # Load settings at startup

    def open_add_application_dialog(self):
        self.add_dialog = tk.Toplevel(self.master)  # Store reference to the dialog
        self.add_dialog.title("Add Application")

        # Drag and Drop Area
        drop_frame = tk.LabelFrame(self.add_dialog, text="Drag and Drop .exe Here")
        drop_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Use TkinterDnD for drag-and-drop functionality
        drop_area = tk.Canvas(drop_frame, height=100, bg="lightgray")
        drop_area.pack(padx=10, pady=10, fill="both", expand=True)
        drop_area.create_text(100, 50, text="Drop your .exe file here", fill="black")

        # Enable the canvas for drag-and-drop
        drop_area.drop_target_register(DND_FILES)
        drop_area.dnd_bind('<<Drop>>', self.on_drop)

        # Manual Input Area
        manual_frame = tk.LabelFrame(self.add_dialog, text="Or Manually Add Application")
        manual_frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(manual_frame, text="Name:").pack(pady=5)
        self.name_entry = tk.Entry(manual_frame)
        self.name_entry.pack(padx=10, pady=5, fill="x")

        tk.Label(manual_frame, text="Path:").pack(pady=5)
        self.path_entry = tk.Entry(manual_frame)
        self.path_entry.pack(padx=10, pady=5, fill="x")

        browse_button = tk.Button(manual_frame, text="Browse", command=self.browse_for_file)
        browse_button.pack(pady=5)

        # Save Button
        save_button = tk.Button(self.add_dialog, text="Save", command=self.save_application)
        save_button.pack(pady=10)

    def on_drop(self, event):
        file_path = event.data.strip('{}')  # Strip curly braces if present
        if file_path.endswith('.exe'):
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)

            app_name = os.path.basename(file_path)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, app_name)
        else:
            messagebox.showerror("Invalid File", "Please drop a valid .exe file.")

    def browse_for_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)
            
            app_name = os.path.basename(file_path)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, app_name)

    def save_application(self):
        app_name = self.name_entry.get().strip()
        app_path = self.path_entry.get().strip()
        
        if not app_name or not app_path:
            messagebox.showerror("Error", "Both name and path are required.")
            return

        # Call the add_application method from AppLocker instance
        self.app_locker.add_application(app_name, app_path)
        self.update_apps_listbox()
        self.update_config_display()  # Update config tab

        # Close the dialog
        self.add_dialog.destroy()

        messagebox.showinfo("Success", f"Application '{app_name}' added successfully!")

        






    def set_app_icon(self):
        try:
            # Load the .ico icon image for the taskbar (Windows)
            ico_path = '1.ico'  # Update this path to your .ico file
            if os.path.exists(ico_path):
                self.master.iconbitmap(ico_path)
            else:
                print(f"Icon file {ico_path} not found, skipping .ico icon.")

            # Load the .png icon image for the window icon
            png_path = '2.png'  # Update this path to your .png file to set the app icon which appears in startbar and in the topbar
            if os.path.exists(png_path):
                icon_img = PhotoImage(file=png_path)
                self.master.iconphoto(False, icon_img)
            else:
                print(f"Icon file {png_path} not found, skipping .png icon.")

        except Exception as e:
            print(f"Failed to set application icon: {e}")






    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both")

        # Main Tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main")

        # Load and display image
        self.load_image()
        self.image_label = tk.Label(self.main_frame, image=self.img)
        self.image_label.pack(pady=10)  # Add padding if needed

        ttk.Button(self.main_frame, text="Create Password", command=self.create_password).pack(pady=5)
        ttk.Button(self.main_frame, text="Change Password", command=self.change_password).pack(pady=5)
        ttk.Button(self.main_frame, text="Start Monitoring", command=self.start_monitoring).pack(pady=5)
        ttk.Button(self.main_frame, text="Stop Monitoring", command=self.stop_monitoring).pack(pady=5)

        # Applications Tab
        self.apps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_frame, text="Applications")

        # Create a frame to hold the listbox and scrollbar
        list_frame = ttk.Frame(self.apps_frame)
        list_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # Create the listbox with a scrollbar
        self.apps_listbox = tk.Listbox(list_frame, width=50, font=("Helvetica", 10), selectmode=tk.SINGLE)
        self.apps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.apps_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.apps_listbox.config(yscrollcommand=scrollbar.set)

        self.update_apps_listbox()

        # Buttons frame
        button_frame = ttk.Frame(self.apps_frame)
        button_frame.pack(pady=10, padx=5, fill=tk.X)

        # Modify the Add button to open the new dialog
        ttk.Button(button_frame, text="Add", command=self.open_add_application_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove", command=self.remove_application).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rename", command=self.rename_application).pack(side=tk.LEFT, padx=5)





        # Config Tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Config")

        self.config_text = tk.Text(self.config_frame, width=60, height=10)
        self.config_text.pack(pady=5)
        self.update_config_display()

        # State Tab
        # self.state_frame = ttk.Frame(self.notebook)
        # self.notebook.add(self.state_frame, text="State")

        # self.state_text = tk.Text(self.state_frame, width=60, height=10)
        # self.state_text.pack(pady=5)
        # self.update_state_display()

        # Settings Tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")

        ttk.Button(self.settings_frame, text="Export Config", command=self.export_config).pack(pady=5)
        # ttk.Button(self.settings_frame, text="Export State", command=self.export_state).pack(pady=5)



        # Add the checkbox for disabling/enabling cmd, PowerShell, and Task Manager lock
        self.lock_tools_var = tk.BooleanVar(value=True)

        # Add the checkbox with wrapped text and left-aligned text
        lock_tools_checkbox = ttk.Checkbutton(
            self.settings_frame,
            text="Disable Command Prompt, Registry Editor, Control Panel, msconfig, and Task Manager during\nmonitoring.\n"
            "(Default: All are disabled for best security. For added security, please disable PowerShell as well; search\non internet for help. Otherwise, FadCrypt could be terminated via PowerShell.)",
            variable=self.lock_tools_var,
            # wraplength=500,  # Adjust this value based on your UI width
            # anchor="e",      # Align the text to the left
            # justify="left",  # Justify text to left
            # padx="20"
        )

        # The external padding is controlled by the pack() method's padx and pady options
        lock_tools_checkbox.pack(anchor="w", padx=10, pady=10)  # Adjust padx and pady for desired spacing
        
        # Save settings on state change (Optional, you can also handle this in the save settings function)
        self.lock_tools_var.trace_add("write", self.save_settings)





    # image for the main page above the buttons
    def load_image(self):
        # Open and prepare the image
        image = Image.open('1.png')  # Update this path
        image = image.resize((200, 100), Image.LANCZOS)  # Resize using LANCZOS filter
        self.img = ImageTk.PhotoImage(image)













    def update_config_textbox(self):
        # Update the content of the config text box with the latest config data
        config_json = json.dumps(self.app_locker.config, indent=4)
        self.config_textbox.config(state=tk.NORMAL)
        self.config_textbox.delete(1.0, tk.END)
        self.config_textbox.insert(tk.END, config_json)
        self.config_textbox.config(state=tk.DISABLED)



    def update_apps_listbox(self):
        self.apps_listbox.delete(0, tk.END)
        for index, app in enumerate(self.app_locker.config["applications"]):
            item = f"  {app['name']} - {app['path']}"  # Added two spaces for left padding
            self.apps_listbox.insert(tk.END, item)
            # Apply alternating row colors
            if index % 2 == 0:
                self.apps_listbox.itemconfig(index, {'bg': '#f0f0f0'})
            else:
                self.apps_listbox.itemconfig(index, {'bg': '#ffffff'})
        self.update_config_display()

    def update_config_display(self):
        self.config_text.config(state=tk.NORMAL)
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, json.dumps(self.app_locker.config, indent=4))
        self.config_text.config(state=tk.DISABLED)






    def update_state_display(self):
        self.state_text.delete(1.0, tk.END)
        self.state_text.insert(tk.END, json.dumps(self.app_locker.state, indent=4))

    def export_config(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", initialfile="FadCrypt_config.json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(self.app_locker.config, f, indent=4)
                messagebox.showinfo("Success", f"Config exported successfully to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export config: {e}")

    def export_state(self):
        self.app_locker.export_state()
        messagebox.showinfo("Info", "State exported to state.json")


        

    def update_apps_listbox(self):
        self.apps_listbox.delete(0, tk.END)
        for app in self.app_locker.config["applications"]:
            self.apps_listbox.insert(tk.END, f"{app['name']} - {app['path']}")

    def create_password(self):
        if os.path.exists(self.app_locker.password_file):
            messagebox.showinfo("Info", "Password already exists. Use 'Change Password' to modify.")
        else:
            password = simpledialog.askstring("Create Password", "Enter a new password:", show='*')
            if password:
                self.app_locker.create_password(password)
                messagebox.showinfo("Success", "Password created successfully.")

    def change_password(self):
        old_password = simpledialog.askstring("Change Password", "Enter your old password:", show='*')
        if old_password and self.app_locker.verify_password(old_password):
            new_password = simpledialog.askstring("Change Password", "Enter a new password:", show='*')
            if new_password:
                self.app_locker.change_password(old_password, new_password)
                messagebox.showinfo("Success", "Password changed successfully.")
        else:
            messagebox.showerror("Error", "Incorrect old password.")

    def add_application(self):
        app_name = simpledialog.askstring("Add Application", "Enter the name of the application:")
        if app_name:
            app_path = filedialog.askopenfilename(title="Select application executable")
            if app_path:
                self.app_locker.add_application(app_name, app_path)
                self.update_apps_listbox()
                self.update_config_display()  # Update config tab
                messagebox.showinfo("Success", f"Application {app_name} added successfully.")


    def remove_application(self):
        selection = self.apps_listbox.curselection()
        if selection:
            app_name = self.apps_listbox.get(selection[0]).split(" - ")[0].strip()  # Remove leading spaces
            self.app_locker.remove_application(app_name)
            self.update_apps_listbox()
            self.update_config_display()
            messagebox.showinfo("Success", f"Application {app_name} removed successfully.")
        else:
            messagebox.showerror("Error", "Please select an application to remove.")

    def rename_application(self):
        selection = self.apps_listbox.curselection()
        if selection:
            old_name = self.apps_listbox.get(selection[0]).split(" - ")[0].strip()  # Remove leading spaces
            new_name = simpledialog.askstring("Rename Application", f"Enter new name for {old_name}:")
            if new_name:
                for app in self.app_locker.config["applications"]:
                    if app["name"] == old_name:
                        app["name"] = new_name
                        break
                self.update_apps_listbox()
                self.update_config_display()
                messagebox.showinfo("Success", f"Application renamed from {old_name} to {new_name}.")
        else:
            messagebox.showerror("Error", "Please select an application to rename.")

    def start_monitoring(self):
            # Check if the user has enabled the tool lock
        if self.lock_tools_var.get():
            print("Disabling the cmd, powershell and task managaer...")
            self.disable_tools()

        threading.Thread(target=self.app_locker.start_monitoring, daemon=True).start()
        messagebox.showinfo("Info", "Monitoring started. Use the system tray icon to stop.")
        self.master.withdraw()  # Hide the main window

    def stop_monitoring(self):
        # Check if the user has enabled the tool lock
        if self.lock_tools_var.get():
            print("Enabling the cmd, Registry Editor and task managaer...")
            self.enable_tools()

        if self.app_locker.monitoring:
            password = simpledialog.askstring("Stop Monitoring", "Enter your password to stop monitoring:", show='*')
            if password and self.app_locker.verify_password(password):
                self.app_locker.stop_monitoring()
                messagebox.showinfo("Success", "Monitoring stopped.")
                self.master.deiconify()  # Show the main window
            else:
                messagebox.showerror("Error", "Incorrect password. Monitoring will continue.")
        else:
            messagebox.showinfo("Info", "Monitoring is not running.")



    
    def block_registry_editor():
        try:
            # Disable Registry Editor
            reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\System')
            winreg.SetValueEx(reg_key, 'DisableRegistryTools', 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(reg_key)
            print("Registry Editor blocked.")
        except Exception as e:
            print(f"Error blocking Registry Editor: {e}")

    def unblock_registry_editor():
        try:
            # Open the registry key
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 0, winreg.KEY_SET_VALUE)
            try:
                # Attempt to delete the DisableRegistryTools value
                winreg.DeleteValue(reg_key, 'DisableRegistryTools')
                print("Registry Editor unblocked.")
            except FileNotFoundError:
                print("Registry Editor was not blocked.")
            finally:
                winreg.CloseKey(reg_key)
        except Exception as e:
            print(f"Error unblocking Registry Editor: {e}")


    def disable_tools(self):
        """Disable Command Prompt, PowerShell, and Task Manager using winreg."""
        try:
            # Disable Command Prompt
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Policies\Microsoft\Windows\System', 0, winreg.KEY_CREATE_SUB_KEY | winreg.KEY_SET_VALUE) as cmd_key:
                winreg.SetValueEx(cmd_key, 'DisableCMD', 0, winreg.REG_DWORD, 1)
            print("Command Prompt disabled.")
            
            # Disable Task Manager
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\System') as taskmgr_key:
                winreg.SetValueEx(taskmgr_key, 'DisableTaskMgr', 0, winreg.REG_DWORD, 1)
            print("Task Manager disabled.")
            
            # Disable Control Panel
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer') as explorer_key:
                winreg.SetValueEx(explorer_key, 'NoControlPanel', 0, winreg.REG_DWORD, 1)
            print("Control Panel disabled.")
            
            # Disable System Configuration Utility (msconfig)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\System') as system_key:
                winreg.SetValueEx(system_key, 'DisableTaskMgr', 0, winreg.REG_DWORD, 1)
            print("System Configuration Utility (msconfig) disabled.")
            
            # Prevent system shutdown
            # with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System') as policy_key:
            #     winreg.SetValueEx(policy_key, 'DisableShutdown', 0, winreg.REG_DWORD, 1)
            # print("System shutdown disabled.")

            # Block Registry Editor
            AppLockerGUI.block_registry_editor()

        except Exception as e:
            print(f"Failed to disable tools: {e}")



    def enable_tools(self):
        """Enable Command Prompt, PowerShell, and Task Manager using winreg."""
        try:
            # Enable Command Prompt
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Policies\Microsoft\Windows\System', 0, winreg.KEY_SET_VALUE) as cmd_key:
                winreg.SetValueEx(cmd_key, 'DisableCMD', 0, winreg.REG_DWORD, 0)
            print("Command Prompt enabled.")
            
            # Enable Task Manager
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\System') as taskmgr_key:
                winreg.SetValueEx(taskmgr_key, 'DisableTaskMgr', 0, winreg.REG_DWORD, 0)
            print("Task Manager enabled.")
            
            # Enable Control Panel
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer') as explorer_key:
                try:
                    winreg.DeleteValue(explorer_key, 'NoControlPanel')
                except FileNotFoundError:
                    pass
            print("Control Panel enabled.")
            
            # Enable System Configuration Utility (msconfig)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Policies\System') as system_key:
                try:
                    winreg.DeleteValue(system_key, 'DisableTaskMgr')
                except FileNotFoundError:
                    pass
            print("System Configuration Utility (msconfig) enabled.")
            
            # Allow system shutdown
            # with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System') as policy_key:
            #     try:
            #         winreg.DeleteValue(policy_key, 'DisableShutdown')
            #     except FileNotFoundError:
            #         pass
            # print("System shutdown enabled.")

            # Unblock Registry Editor
            AppLockerGUI.unblock_registry_editor()

        except Exception as e:
            print(f"Failed to enable tools: {e}")

    


    def save_settings(self, *args):
        settings = {
            "lock_tools": self.lock_tools_var.get(),
            # Other settings can be added here
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"Settings saved to {self.settings_file}")  # Debug print



    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.lock_tools_var.set(settings.get("lock_tools", True))
        else:
            # If settings file does not exist, use defaults
            self.lock_tools_var.set(True)  # Default to locking tools





















class AppLocker:
    # def __init__(self, gui, config_file="config.json", state_file="state.json"):
    def __init__(self, gui):
        self.gui = gui # Store reference to the AppLockerGUI instance
        self.config_file = self.get_config_file_path()
        # self.key = self.generate_key()
        # self.fernet = Fernet(self.key)

        # self.config_file = {"applications": []}  # In-memory config
        self.password_file = os.path.join(self.get_fadcrypt_folder(), 'encrypted_password.bin')
        self.config = {"applications": []}  # In-memory configuration
        self.state = {"unlocked_apps": []}  # In-memory state

        self.load_config()
        self.load_state()
        self.monitoring = False
        self.monitoring_thread = None
        # self.state_file = {"unlocked_apps": []}  # In-memory state
        self.load_state()
        self.icon = None
        


    def get_fadcrypt_folder(self):
        path = os.path.join(os.getenv('APPDATA'), 'FadCrypt')
        os.makedirs(path, exist_ok=True)
        return path
    
        

    def load_config(self):
        print(f"Loading config from {self.config_file}")  # Debug print
        
        # Check if the config file exists
        if os.path.exists(self.config_file):
            if os.path.exists(self.password_file):
                password = self.load_password()
                self.config = self.decrypt_data(password, self.config_file)
                print(f"Config loaded: {self.config}")  # Debug print
            else:
                print("Password file does not exist.")
                self.config = {"applications": []}
                # Optionally, save default config if password file is missing
                self.save_config()
        else:
            print("Config file does not exist. Initialized with default config.")  # Debug print
            self.config = {"applications": []}
            # Create the config file with default content
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Config file created at {self.config_file} with default settings.")  # Debug print

    def save_config(self):
        if os.path.exists(self.password_file):
            password = self.load_password()
            self.encrypt_data(password, self.config, self.config_file)
            print(f"Config saved to {self.config_file}")  # Debug print
        else:
            print("Password file does not exist. Cannot save config.")

    def load_password(self):
        with open(self.password_file, 'rb') as f:
            return f.read()
        
    def get_key(self):
        # Generate a key for encryption/decryption
        # You can generate a key using: Fernet.generate_key()
        # Save this key securely; for demo, we're using a hardcoded key.
        return base64.urlsafe_b64encode(b"your-secret-key-32-bytes-long")

    def get_config_file_path(self):
        return os.path.join(self.get_fadcrypt_folder(), 'config.json')
    
        
    def generate_key(self):
        key_path = os.path.join(os.getenv('APPDATA'), 'FadCrypt', 'config.key')
        print(f"Key file path: {key_path}")  # Debug print
        if os.path.exists(key_path):
            with open(key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
            return key
    
    def encrypt_data(self, password, data, file_path):
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password)
        cipher = Cipher(algorithms.AES(key), modes.GCM(salt), backend=default_backend())
        encryptor = cipher.encryptor()
        json_data = json.dumps(data).encode()
        encrypted_data = encryptor.update(json_data) + encryptor.finalize()
        with open(file_path, 'wb') as f:
            f.write(salt + encryptor.tag + encrypted_data)

    def decrypt_data(self, password, file_path):
        with open(file_path, 'rb') as f:
            salt = f.read(16)
            tag = f.read(16)
            encrypted_data = f.read()
        print(f"Salt: {salt.hex()}")
        print(f"Tag: {tag.hex()}")
        print(f"Encrypted Data: {encrypted_data.hex()}")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password)
        cipher = Cipher(algorithms.AES(key), modes.GCM(salt, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return json.loads(decrypted_data)
    
    def load_state(self):
        # No file operation, use in-memory state
        pass

    def save_state(self):
        self._update_script("embedded_state", self.state)
    
    def export_config(self):
        export_path = "FadCrypt_config.json"
        print(f"Exporting config to {export_path}")  # Debug print
        with open(export_path, "w") as f:
            json.dump(self.config, f, indent=4)
        print("Config exported.")  # Debug print

    def export_state(self):
        export_path = "state.json"
        print(f"Exporting state to {export_path}")  # Debug print
        with open(export_path, "w") as f:
            json.dump(self.state, f, indent=4)
        print("State exported.")  # Debug print


    def _update_script(self, variable_name, data):
        # Update the script with new data
        script_path = sys.argv[0]  # Get the path of the running script

        print(f"Updating script: {script_path}")  # Debug print
        with open(script_path, 'r') as file:
            script = file.read()

        # Convert the current embedded data to a JSON string
        old_data_str = f"{variable_name} = " + json.dumps(eval(variable_name), indent=4)

        # Convert the new data to a JSON string
        new_data_str = f"{variable_name} = " + json.dumps(data, indent=4)

        # Replace the old data with the new data in the script
        script = script.replace(old_data_str, new_data_str)

        # Save the modified script
        with open(script_path, 'w') as file:
            file.write(script)
        print("Script updated.")  # Debug print



    def create_password(self, password):
        try:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            cipher = Cipher(algorithms.AES(key), modes.GCM(salt), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_hash = encryptor.update(password.encode()) + encryptor.finalize()
            
            with open(self.password_file, "wb") as f:
                f.write(salt + encryptor.tag + encrypted_hash)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating password: {e}")

    def change_password(self, old_password, new_password):
        if self.verify_password(old_password):
            self.create_password(new_password)

            # Re-encrypt the configuration file with the new password
            self.save_config()  # This will use the new password
            print("change_password: Re-encrypt the configuration file with the new password")
        else:
            messagebox.showerror("Error", "Incorrect old password.")

    def verify_password(self, password):
        try:
            if not os.path.exists(self.password_file):
                return False

            with open(self.password_file, "rb") as f:
                salt = f.read(16)
                tag = f.read(16)
                encrypted_hash = f.read()

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            cipher = Cipher(algorithms.AES(key), modes.GCM(salt, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_hash = decryptor.update(encrypted_hash) + decryptor.finalize()

            return password.encode() == decrypted_hash
        # except InvalidTag as ee:
        #     messagebox.showerror("Error", f"Encryptepd file corrupted: {ee}")
        #     return False
        except Exception as e:
            messagebox.showerror("Error", f"Error verifying password: {e}")
        return False

    def add_application(self, app_name, app_path):
        self.config["applications"].append({"name": app_name, "path": app_path})
        self.save_config()

    def remove_application(self, app_name):
        self.config["applications"] = [app for app in self.config["applications"] if app["name"] != app_name]
        self.save_config()

    def block_application(self, app_name, app_path):
        while self.monitoring:
            try:
                app_processes = [proc for proc in psutil.process_iter(['name', 'pid']) if proc.info['name'].lower() == app_name.lower()]

                if app_processes:
                    if app_name not in self.state["unlocked_apps"]:
                        for proc in app_processes:
                            proc.terminate()
                        
                        self.gui.master.after(0, self._show_password_dialog, app_name, app_path)
                        time.sleep(1)  # Wait for user input
                    else:
                        time.sleep(7)
                
                if app_name in self.state["unlocked_apps"] and not app_processes:
                    self.state["unlocked_apps"].remove(app_name)
                    self.save_state()
                
                time.sleep(1)
            except Exception as e:
                print(f"Error in block_application: {e}")

    def _show_password_dialog(self, app_name, app_path):
        try:
            password = simpledialog.askstring("Password", f"Enter your password to unlock {app_name}:", show='*', parent=self.gui.master)
            if password is None:
                return

            if self.verify_password(password):
                self.state["unlocked_apps"].append(app_name)
                self.save_state()

                if app_path:
                    try:
                        subprocess.Popen(app_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to start {app_name}: {e}")
            else:
                messagebox.showerror("Error", f"Incorrect password. {app_name} remains locked.")
        except Exception as e:
            print(f"Error in _show_password_dialog: {e}")

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            for app in self.config["applications"]:
                app_name = app["name"]
                app_path = app.get("path", "")
                threading.Thread(target=self.block_application, args=(app_name, app_path), daemon=True).start()
            self._create_system_tray_icon()
        else:
            messagebox.showinfo("Info", "Monitoring is already running.")

    def stop_monitoring(self):
        if self.monitoring:
            self.monitoring = False
            if self.icon:
                self.icon.stop()
            self.gui.master.deiconify()  # Show the main window
        else:
            messagebox.showinfo("Info", "Monitoring is not running.")

    def _create_system_tray_icon(self):
        def on_stop(icon, item):
            self.gui.master.after(0, self._password_prompt_and_stop)

        def on_quit(icon, item):
            self.gui.master.after(0, self._password_prompt_and_quit, icon)

        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color=(73, 109, 137))
        draw = ImageDraw.Draw(image)
        draw.rectangle([(width // 4, height // 4), (3 * width // 4, 3 * height // 4)], fill="white")

        menu = Menu(
            MenuItem('Stop Monitoring', on_stop),
            MenuItem('Quit', on_quit)
        )

        self.icon = Icon("AppLocker", image, "FadCrypt", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def _password_prompt_and_stop(self):
        password = simpledialog.askstring("Password", "Enter your password to stop monitoring:", show='*', parent=self.gui.master)
        if password is not None and self.verify_password(password):
            self.stop_monitoring()
            if self.gui.lock_tools_var.get():
                print("Enabling the cmd, powershell and task managaer...")
                self.gui.enable_tools()
            messagebox.showinfo("Info", "Monitoring has been stopped.")
        else:
            messagebox.showerror("Error", "Incorrect password or action cancelled. Monitoring will continue.")

    def _password_prompt_and_quit(self, icon):
        password = simpledialog.askstring("Password", "Enter your password to quit:", show='*', parent=self.gui.master)
        if self.verify_password(password):
            self.stop_monitoring()
            icon.stop()
            messagebox.showinfo("Info", "Application has been stopped.")
            self.gui.master.quit()
        else:
            messagebox.showerror("Error", "Incorrect password. Application will continue.")




class FileMonitor:
    def __init__(self):
        self.observer = Observer()
        self.backup_folder = None
        self.files_to_monitor = []

    def get_fadcrypt_folder(self):
        path = os.path.join(os.getenv('APPDATA'), 'FadCrypt')
        os.makedirs(path, exist_ok=True)
        return path

    def get_backup_folder(self):
        # Using ProgramData for more secure backup location
        print("Using ProgramData for more secure backup location")
        path = os.path.join('C:\\ProgramData', 'FadCrypt', 'Backup')
        os.makedirs(path, exist_ok=True)
        return path
    
    def set_files_to_monitor(self):
        # Set the files to monitor in the correct directory
        fadcrypt_folder = self.get_fadcrypt_folder()
        self.files_to_monitor = [
            os.path.join(fadcrypt_folder, 'config.json'),
            os.path.join(fadcrypt_folder, 'encrypted_password.bin')
        ]
        self.backup_folder = self.get_backup_folder()

    def start_monitoring(self):
        self.set_files_to_monitor()
        event_handler = self.FileChangeHandler(self.files_to_monitor, self.backup_folder)
        self.observer.schedule(event_handler, os.path.dirname(self.files_to_monitor[0]), recursive=False)
        self.observer.start()
        print("Started monitoring files...")

    class FileChangeHandler(FileSystemEventHandler):
        def __init__(self, files_to_monitor, backup_folder):
            super().__init__()
            self.files_to_monitor = files_to_monitor
            self.backup_folder = backup_folder
            self.initial_restore()  # Restore any missing files from the backup folder
            print("Initial file recovery completed.")

        def on_modified(self, event):
            if event.src_path in self.files_to_monitor:
                print(f"File modified: {event.src_path}")
                self.backup_files()

        def on_deleted(self, event):
            if event.src_path in self.files_to_monitor:
                print(f"File deleted: {event.src_path}")
                self.restore_files()

        def backup_files(self):
            # Ensure backup directory exists
            if not os.path.exists(self.backup_folder):
                os.makedirs(self.backup_folder)
                print(f"Backup folder created: {self.backup_folder}")

            for file_path in self.files_to_monitor:
                if os.path.exists(file_path):
                    backup_path = os.path.join(self.backup_folder, os.path.basename(file_path))
                    try:
                        shutil.copy(file_path, backup_path)
                        print(f"Backed up {file_path} to {backup_path}")
                    except Exception as e:
                        print(f"Error backing up {file_path}: {e}")
                else:
                    print(f"File {file_path} does not exist, cannot back up.")


        def restore_files(self):
            for file_path in self.files_to_monitor:
                backup_path = os.path.join(self.backup_folder, os.path.basename(file_path))
                if not os.path.exists(file_path) and os.path.exists(backup_path):
                    # Ensure the target directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    try:
                        shutil.copy(backup_path, file_path)
                        print(f"Restored {file_path} from {backup_path}")
                    except Exception as e:
                        print(f"Error restoring {file_path}: {e}")
                else:
                    print(f"Could not restore {file_path}; either it already exists or no backup found.")


        def initial_restore(self):
            for file_path in self.files_to_monitor:
                if not os.path.exists(file_path):
                    backup_path = os.path.join(self.backup_folder, os.path.basename(file_path))
                    if os.path.exists(backup_path):
                        # Ensure the target directory exists
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        try:
                            shutil.copy(backup_path, file_path)
                            print(f"Initial restore: {file_path} restored from {backup_path}")
                        except Exception as e:
                            print(f"Error during initial restore of {file_path}: {e}")
                    else:
                        print(f"Backup for {file_path} not found for initial restore.")




def start_monitoring_thread(monitor):
    monitor.start_monitoring()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.observer.stop()
    monitor.observer.join()




def main():
    root = TkinterDnD.Tk()
    style = Style(theme='darkly')  # Apply dark theme, pulse, cyborg, darkly, simplex(red)


    # Customize window borders (not directly supported in ttkbootstrap, but can be done with custom themes)
    style.configure('TNotebook.Tab',
                    background='#333333',  # Dark gray for tabs
                    foreground='#FFFFFF')  # White text for tabs
    

    # Customize button color
    style.configure('TButton',
                    background='#333333',  # Dark gray color
                    foreground='#FFFFFF',  # White text
                    borderwidth=3,  # Border width
                    relief='solid',  # Solid border
                    highlightbackground='#222222',  # Darker border color
                    highlightthickness=2)  # Thickness of the border

    style.map('TButton',
            foreground=[('hover', '#D3D3D3')],  # Black text color on hover
            background=[('active', '#000000')])  # Red color on hover

    # Customize the window frame color (e.g., the title bar)
    style.configure('TFrame',
                    background='#333333')  # Dark gray color
    

    # Style the Checkbutton
    style.configure('TCheckbutton', background='#181818', foreground='#ffffff', padding=10)

    app = AppLockerGUI(root)
    # root.protocol("WM_DELETE_WINDOW", root.iconify)  # Minimize instead of close
    root.mainloop()

if __name__ == "__main__":
    monitor = FileMonitor()
    monitoring_thread = threading.Thread(target=start_monitoring_thread, args=(monitor,))
    monitoring_thread.daemon = True
    monitoring_thread.start()
    main()