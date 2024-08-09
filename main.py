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
from tkinter import simpledialog

class AppLocker:
    def __init__(self, config_file="config.json", state_file="state.json"):
        self.config_file = config_file
        self.password_file = "encrypted_password.bin"
        self.load_config()
        self.monitoring = False
        self.monitoring_thread = None
        self.state_file = state_file
        self.load_state()






    def get_locked_apps(self):
        """ Get the list of locked apps from config.json """
        try:
            with open('config.json', 'r') as file:
                data = json.load(file)
            # Extract application names from the config
            return [app['name'] for app in data['applications']]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}")
            return []




    def get_unlocked_apps(self):
        """ Retrieve the list of unlocked applications from state.json. """
        try:
            with open('state.json', 'r') as f:
                data = json.load(f)
            return data.get('unlocked_apps', [])
        except Exception as e:
            print(f"Error retrieving unlocked apps: {e}")
            return []
    




    def continuously_terminate_locked_apps(self):
        """ Continuously check for and terminate locked applications. """
        while True:
            try:
                locked_apps = self.get_locked_apps()
                unlocked_apps = self.get_unlocked_apps()

                for proc in psutil.process_iter(['pid', 'name']):
                    process_name = proc.info['name']
                    if process_name in locked_apps and process_name not in unlocked_apps:
                        try:
                            proc.terminate()
                            print(f"Terminated {process_name}")
                        except psutil.NoSuchProcess:
                            print(f"Process {process_name} no longer exists")
                            time.sleep(1)

                time.sleep(2)  # Sleep for a bit to reduce CPU usage

            except Exception as e:
                print(f"Error in continuously_terminate_locked_apps: {e}")



    def prompt_password_in_gui(self, app_name):
        """ Prompt for a password using a minimal GUI dialog and run continuous monitoring """

        root = tk.Tk()
        root.withdraw()  # Hide the root window
        password = simpledialog.askstring("Password", f"Enter your password to unlock {app_name}:", show='*')
        root.destroy()  # Close the Tkinter root window
        return password






    def load_config(self):
        """ Load application configuration from a JSON file """
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {"applications": []}

    def save_config(self):
        """ Save the current configuration to a JSON file """
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def create_password(self):
        """ Create and store a new password securely """
        try:
            password = getpass.getpass("Create a new password: ").encode()
            if not os.path.exists(self.password_file):
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
                encrypted_hash = encryptor.update(password) + encryptor.finalize()
                
                with open(self.password_file, "wb") as f:
                    f.write(salt + encryptor.tag + encrypted_hash)
                
                print("Password created and stored securely.")
            else:
                print("Password is already set. Please use 'change_password' to modify.")
        except Exception as e:
            print(f"Error creating password: {e}")

    def change_password(self):
        """ Change the current password """
        try:
            if os.path.exists(self.password_file):
                old_password = getpass.getpass("Enter your old password: ").encode()
                if self.verify_password(old_password):
                    new_password = getpass.getpass("Enter a new password: ").encode()
                    salt = os.urandom(16)
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                        backend=default_backend()
                    )
                    key = kdf.derive(new_password)
                    cipher = Cipher(algorithms.AES(key), modes.GCM(salt), backend=default_backend())
                    encryptor = cipher.encryptor()
                    encrypted_hash = encryptor.update(new_password) + encryptor.finalize()

                    with open(self.password_file, "wb") as f:
                        f.write(salt + encryptor.tag + encrypted_hash)

                    print("Password changed successfully.")
                else:
                    print("Incorrect old password.")
            else:
                print("No password is set. Please create a password first.")
        except Exception as e:
            print(f"Error changing password: {e}")

    def verify_password(self, password):
        """ Verify the entered password """
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

            # Ensure the password matches the decrypted hash
            return password.encode() == decrypted_hash
        except InvalidTag:
            print("Incorrect password or data tampering detected.")
        except Exception as e:
            print(f"Error verifying password: {e}")
        return False

    def load_state(self):
        """ Load the application state from a JSON file """
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                self.state = json.load(f)
        else:
            self.state = {"unlocked_apps": []}

    def save_state(self):
        """ Save the current state to a JSON file """
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=4)



    def block_application(self, app_name, app_path):
        """ Block the specified application and prompt for password using GUI """
        while self.monitoring:
            # Check if the application is trying to start
            app_processes = [proc for proc in psutil.process_iter(['name', 'pid']) if proc.info['name'].lower() == app_name.lower()]

            if app_processes:
                if app_name not in self.state["unlocked_apps"]:
                    # Terminate the app if it's not already unlocked
                    for proc in app_processes:
                        proc.terminate()  # Immediately terminate the process
                    print(f"Detected {app_name} trying to start. Process terminated.")
                    
                    # Prompt for password
                    password = self.prompt_password_in_gui(app_name)
                    if password is None:
                        # Cancel button pressed or dialog closed
                        print(f"{app_name} remains locked due to cancellation.")
                        continue

                    if self.verify_password(password):
                        # Allow the application to start if the password is correct
                        self.state["unlocked_apps"].append(app_name)
                        self.save_state()

                        if app_path:
                            try:
                                subprocess.Popen(app_path)  # Relaunch the app after password verification
                                print(f"{app_name} started successfully.")
                            except Exception as e:
                                print(f"Failed to start {app_name}: {e}")
                    else:
                        print(f"Incorrect password or data tampering detected.")
                        print(f"{app_name} remains locked due to incorrect password.")
                else:
                    print(f"{app_name} is already unlocked. Skipping termination.")
            
            # Check if the unlocked app has been closed and remove from unlocked state
            if app_name in self.state["unlocked_apps"] and not app_processes:
                self.state["unlocked_apps"].remove(app_name)
                self.save_state()
                print(f"{app_name} closed and removed from unlocked state.")
            
            time.sleep(1)  # Check every 1 second






    def add_application(self):
        """ Add a new application to the config """
        app_name = input("Enter the name of the application (e.g., brave.exe): ")
        app_path = input("Enter the full path to the application (or leave blank if unknown): ")
         # Replace single slashes with double slashes and trim only trailing whitespace
        app_path = app_path.replace('/', '\\').replace('"', '').rstrip()
        if app_name:
            self.config["applications"].append({"name": app_name, "path": app_path})
            self.save_config()
            print(f"Application {app_name} added to the configuration.")

    def remove_application(self):
        """ Remove an application from the config """
        app_name = input("Enter the name of the application to remove: ")
        if app_name:
            self.config["applications"] = [app for app in self.config["applications"] if app["name"] != app_name]
            self.save_config()
            print(f"Application {app_name} removed from the configuration.")

    def start_monitoring(self):
        """ Start monitoring and terminating locked apps """
        # Start continuous termination in a separate thread
        threading.Thread(target=self.continuously_terminate_locked_apps, daemon=True).start()
        """ Start the monitoring thread """

        if not self.monitoring:
            self.monitoring = True
            for app in self.config["applications"]:
                app_name = app["name"]
                app_path = app.get("path", "")
                threading.Thread(target=self.block_application, args=(app_name, app_path), daemon=True).start()
            print("Monitoring started. To stop, type 'quit' and press Enter.")
            self.monitoring_loop()
        else:
            print("Monitoring is already running.")

    def stop_monitoring(self):
        """ Stop monitoring """
        if self.monitoring:
            self.monitoring = False
            print("Monitoring stopped.")
        else:
            print("Monitoring is not running.")

    def monitoring_loop(self):
        """ Keep the monitoring loop running """
        while self.monitoring:
            command = input()
            if command.lower() == 'quit':
                if self.verify_password(getpass.getpass("Enter your password to stop monitoring: ")):
                    self.stop_monitoring()
                else:
                    print("Incorrect password. Monitoring will continue.")
            else:
                print("Invalid command. To stop monitoring, type 'quit' and press Enter.")

def main():
    app_locker = AppLocker()

    while True:
        print("\nApp Locker CLI")
        print("1. Create Password")
        print("2. Change Password")
        print("3. Add Application")
        print("4. Remove Application")
        print("5. Start Monitoring")
        print("6. Stop Monitoring")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            app_locker.create_password()
        elif choice == '2':
            app_locker.change_password()
        elif choice == '3':
            app_locker.add_application()
        elif choice == '4':
            app_locker.remove_application()
        elif choice == '5':
            app_locker.start_monitoring()
        elif choice == '6':
            app_locker.stop_monitoring()
        elif choice == '7':
            if app_locker.monitoring:
                print("Please stop monitoring before exiting.")
            else:
                print("Exiting...")
                break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
