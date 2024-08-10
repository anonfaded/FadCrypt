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
from tkinter import ttk, simpledialog, messagebox, filedialog
import winreg
import signal
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
import sys

class AppLockerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("App Locker")
        self.master.geometry("500x400") # Adjusted size to accommodate new tabs
        self.app_locker = AppLocker(self)
        
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both")

        # Main Tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main")

        ttk.Button(self.main_frame, text="Create Password", command=self.create_password).pack(pady=5)
        ttk.Button(self.main_frame, text="Change Password", command=self.change_password).pack(pady=5)
        ttk.Button(self.main_frame, text="Start Monitoring", command=self.start_monitoring).pack(pady=5)
        ttk.Button(self.main_frame, text="Stop Monitoring", command=self.stop_monitoring).pack(pady=5)

        # Applications Tab
        self.apps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_frame, text="Applications")

        self.apps_listbox = tk.Listbox(self.apps_frame, width=50)
        self.apps_listbox.pack(pady=5)
        self.update_apps_listbox()

        ttk.Button(self.apps_frame, text="Add Application", command=self.add_application).pack(pady=5)
        ttk.Button(self.apps_frame, text="Remove Application", command=self.remove_application).pack(pady=5)

        # Config Tab
        # self.config_frame = ttk.Frame(self.notebook)
        # self.notebook.add(self.config_frame, text="Config")

        # self.config_text = tk.Text(self.config_frame, width=60, height=10)
        # self.config_text.pack(pady=5)
        # self.update_config_display()

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

    def update_config_textbox(self):
        # Update the content of the config text box with the latest config data
        config_json = json.dumps(self.app_locker.config, indent=4)
        self.config_textbox.config(state=tk.NORMAL)
        self.config_textbox.delete(1.0, tk.END)
        self.config_textbox.insert(tk.END, config_json)
        self.config_textbox.config(state=tk.DISABLED)



    def update_apps_listbox(self):
        self.apps_listbox.delete(0, tk.END)
        for app in self.app_locker.config["applications"]:
            self.apps_listbox.insert(tk.END, app["name"])
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
                self.update_config_textbox()  # Update config tab
                messagebox.showinfo("Success", f"Application {app_name} added successfully.")


    def remove_application(self):
        selection = self.apps_listbox.curselection()
        if selection:
            app_name = self.apps_listbox.get(selection[0]).split(" - ")[0]
            self.app_locker.remove_application(app_name)
            self.update_apps_listbox()
            self.update_config_textbox()  # Update config tab
            messagebox.showinfo("Success", f"Application {app_name} removed successfully.")
        else:
            messagebox.showerror("Error", "Please select an application to remove.")

    def start_monitoring(self):
        threading.Thread(target=self.app_locker.start_monitoring, daemon=True).start()
        messagebox.showinfo("Info", "Monitoring started. Use the system tray icon to stop.")
        self.master.withdraw()  # Hide the main window

    def stop_monitoring(self):
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

class AppLocker:
    # def __init__(self, gui, config_file="config.json", state_file="state.json"):
    def __init__(self, gui):
        self.gui = gui
        # self.config_file = {"applications": []}  # In-memory config
        self.password_file = "encrypted_password.bin"
        self.load_config()
        self.monitoring = False
        self.monitoring_thread = None
        # self.state_file = {"unlocked_apps": []}  # In-memory state
        self.load_state()
        self.icon = None
        self.config = {"applications": []}  # In-memory configuration
        self.state = {"unlocked_apps": []}  # In-memory state

    def load_config(self):
        # No file operation, use in-memory config
        pass

    def save_config(self):
        # No file operation, use in-memory config
        pass

    def load_state(self):
        # No file operation, use in-memory state
        pass

    def save_state(self):
        # No file operation, use in-memory state
        pass
    
    def export_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)

    def export_state(self):
        with open("state.json", "w") as f:
            json.dump(self.state, f, indent=4)



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
        except InvalidTag:
            return False
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

        self.icon = Icon("AppLocker", image, "App Locker", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def _password_prompt_and_stop(self):
        password = simpledialog.askstring("Password", "Enter your password to stop monitoring:", show='*', parent=self.gui.master)
        if password is not None and self.verify_password(password):
            self.stop_monitoring()
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

def main():
    root = tk.Tk()
    app = AppLockerGUI(root)
    # root.protocol("WM_DELETE_WINDOW", root.iconify)  # Minimize instead of close
    root.mainloop()

if __name__ == "__main__":
    main()