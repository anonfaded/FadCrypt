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

class AppLocker:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.password_file = "encrypted_password.bin"
        self.load_config()
        self.monitoring = False

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

            password = password.encode()
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
            key = kdf.derive(password)
            cipher = Cipher(algorithms.AES(key), modes.GCM(salt, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_hash = decryptor.update(encrypted_hash) + decryptor.finalize()

            # Ensure the password matches the decrypted hash
            return password == decrypted_hash
        except InvalidTag:
            print("Incorrect password or data tampering detected.")
        except Exception as e:
            print(f"Error verifying password: {e}")
        return False

    def block_application(self, app_name, app_path):
        """ Block the specified application and prompt for password """
        while self.monitoring:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == app_name.lower():
                    proc.terminate()
                    if self.verify_password(getpass.getpass("Enter your password to unlock: ")):
                        if app_path:
                            subprocess.Popen(app_path)  # Relaunch the app after password verification
                    break  # Exit the loop after handling the detected instance
            time.sleep(1)  # Check every 1 second

    def add_application(self):
        """ Add a new application to the config """
        app_name = input("Enter the name of the application (e.g., brave.exe): ")
        app_path = input("Enter the full path to the application (or leave blank if unknown): ")
        app_path = app_path.replace('\"', '').replace(' ', '')  # Remove quotes and spaces from path
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
        """ Stop monitoring, only if the correct password is provided """
        password = getpass.getpass("Enter your password to stop monitoring: ")
        if self.verify_password(password):
            self.monitoring = False
            print("Monitoring stopped.")
        else:
            print("Incorrect password. Monitoring continues.")

    def monitoring_loop(self):
        """ Keep the monitoring loop running """
        while self.monitoring:
            command = input()
            if command.lower() == 'quit':
                self.stop_monitoring()
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