'''
Glace APM

MIT License

Copyright (c) Vidyut Prabakaran

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

# Libraries

import customtkinter as ctk
import platform
import os
import sys
import ctypes
from tkinter import messagebox, PhotoImage
from cryptography.fernet import Fernet, InvalidToken
import security

def main():
    # Globals
    is_shown = 0
    length = 12

    if getattr(sys, 'frozen', False):  # Check if running as compiled EXE
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    # Security state — populated after master password authentication
    secure_state = {
        'fernet': None,        # Fernet instance derived from master password
        'fernet_key': None,    # Raw derived key bytes (for HMAC)
        'salt': None,          # PBKDF2 salt
        'master_pw': None,     # Kept in memory ONLY during session, never written to disk
        'authenticated': False,
    }

    #script_dir = os.path.dirname(os.path.abspath(__file__))  # Works on all OS

    # Paths

    #script_dir = os.path.dirname(os.path.abspath(__file__))

    passdir_init = os.path.expanduser('~')

    if sys.platform == "win32":
        local_appdata = os.getenv('LOCALAPPDATA')  # Windows
    elif sys.platform == "darwin":
        local_appdata = os.path.expanduser('~/Library/Application Support')  # macOS
    else:
        local_appdata = os.path.expanduser('~/.config')  # Linux

    config_fl_nme = 'config.txt'
    trans_fl_nme = 'trans.txt'
    mp_fl_nme = 'mp.mp'
    cred_fl_nme = 'credentials.pkl'

    home_directory_fr_cred = os.path.expanduser('~')

    usr_path_with_cnfg_fl = os.path.join(local_appdata, 'APM', config_fl_nme)
    usr_path_with_trns_fl = os.path.join(local_appdata, 'APM', trans_fl_nme)
    usr_path_with_mp_fl = os.path.join(local_appdata, 'APM', mp_fl_nme)
    cred_full_path = os.path.join(home_directory_fr_cred, cred_fl_nme)
    cred_json_path = os.path.join(home_directory_fr_cred, 'credentials.json')

    cred_file_name = 'credentials.json'
    cred_file_path = os.path.join(os.path.expanduser('~'), cred_file_name)

    # Secure credential file (new v2 format)
    secure_cred_path = os.path.join(local_appdata, 'APM', 'credentials_secure.json')

    cmn_pwds_path = os.path.join(script_dir, '_itnrl/misc', '10M.txt')
    apm_ico_full_path = os.path.join(script_dir, '_itnrl/icons', 'apm.png')
    fer_path = os.path.join(local_appdata, 'APM', 'fer.apm')

    acc_status_filepath = os.path.join(local_appdata, 'APM','acc_stat.txt')
    acc_usrnme_flpath = os.path.join(local_appdata, 'APM', 'acc_usrnme.apm')
    acc_pwd_flpath = os.path.join(local_appdata, 'APM', 'acc_pwd.apm')

    apm_logo_flpath = os.path.join(script_dir, '_itnrl/icons', 'apm_logo.png')

    license_flpath = os.path.join(script_dir, '_itnrl/docs', 'LICENSE.txt')
    credits_flpath = os.path.join(script_dir, '_itnrl/docs', 'CREDITS.txt')

    red_theme = os.path.join(os.path.dirname(__file__), "_itnrl/themes", "red_theme.json")
    orange_theme = os.path.join(os.path.dirname(__file__), "_itnrl/themes", "orange_theme.json")
    green_theme = os.path.join(os.path.dirname(__file__), "_itnrl/themes", "green_theme.json")
    blue_theme = os.path.join(os.path.dirname(__file__), "_itnrl/themes", "blue_theme.json")
    violet_theme = os.path.join(os.path.dirname(__file__), "_itnrl/themes", "violet_theme.json")

    pwd_model = os.path.join(script_dir, '_itnrl/models', 'pwd_model.json')
    usrnme_model = os.path.join(script_dir, '_itnrl/models', 'usernames.txt')

    # Functions

    def about():
        def license():
            system_name = platform.system()
        
            if system_name == "Windows":
                os.system(f'notepad "{license_flpath}"')
            elif system_name == "Darwin":  # macOS
                os.system(f'open -a TextEdit "{license_flpath}"')
            elif system_name == "Linux":
                os.system(f'xdg-open "{license_flpath}"')
            else:
                messagebox.showerror("Error", "Unable to open license file.")

        def credits():
            system_name = platform.system()

            if system_name == "Windows":
                os.system(f'notepad "{credits_flpath}"')
            elif system_name == "Darwin":  # macOS
                os.system(f'open -a TextEdit "{credits_flpath}"')
            elif system_name == "Linux":
                os.system(f'xdg-open "{credits_flpath}"')
            else:
                messagebox.showerror("Error", "Unable to open credits file.")

        about_win = ctk.CTkToplevel(win)
        about_win.title("Glace APM - About")
        about_win.geometry("370x250")
        about_win.resizable(False, False)
        about_win.lift()
        about_win.attributes("-topmost", True)
        set_window_icon(about_win)

        apm_lbl = ctk.CTkLabel(about_win, text="Glace APM", font=("Arial", 25, "bold"))
        apm_lbl.pack(pady=10, padx=40, anchor="nw")

        apm_ver_lbl = ctk.CTkLabel(about_win, text="Version 2.4", font=("Arial", 15))
        apm_ver_lbl.pack(pady=10, padx=40, anchor="nw")

        apm_dev_lbl = ctk.CTkLabel(about_win, text="Developed by Vidyut Prabakaran", font=("Arial", 15))
        apm_dev_lbl.pack(pady=10, padx=40, anchor="nw")

        apm_cnct = ctk.CTkLabel(about_win, text="Contact: vidyutprabakaran@gmail.com")
        apm_cnct.pack(pady=10, padx=40, anchor="nw")

        apm_btn_frame = ctk.CTkFrame(about_win)
        apm_btn_frame.pack(pady=10, padx=40, anchor="nw")

        apm_lcnse = ctk.CTkButton(apm_btn_frame, text="License", command=license, width=100, font=("Arial", 15))
        apm_lcnse.pack(side="left", padx=(0, 10))

        apm_crdts = ctk.CTkButton(apm_btn_frame, text="Credits", command=credits, width=100, font=("Arial", 15))
        apm_crdts.pack(side="left")

    def init_secure_session(master_password):
        """Initialize the secure session after master password authentication.

        Derives encryption key from master password and loads credentials.
        Handles migration from legacy format if needed.
        """
        nonlocal pwd_pwd, pwd_options

        # Check if we need to migrate from legacy format
        needs_migration = (
            not security.is_secure_format(secure_cred_path)
            and (
                os.path.exists(cred_full_path)
                or os.path.exists(cred_file_path)
                or os.path.exists(fer_path)
            )
        )

        if needs_migration:
            try:
                plaintext_creds, fernet, fernet_key, salt = security.migrate_legacy_to_secure(
                    master_password=master_password,
                    mp_filepath=usr_path_with_mp_fl,
                    fer_filepath=fer_path,
                    pickle_filepath=cred_full_path,
                    old_json_filepath=cred_file_path,
                    new_cred_filepath=secure_cred_path,
                )
                secure_state['fernet'] = fernet
                secure_state['fernet_key'] = fernet_key
                secure_state['salt'] = salt
                secure_state['master_pw'] = master_password
                secure_state['authenticated'] = True
                pwd_pwd = plaintext_creds
                pwd_options = list(pwd_pwd.keys())
                return True
            except Exception as e:
                messagebox.showerror("Migration Error", f"Failed to migrate credentials: {e}")
                return False

        # Load from secure format
        if os.path.exists(secure_cred_path):
            try:
                plaintext_creds, fernet, fernet_key, salt = security.load_credentials_secure(
                    secure_cred_path, master_password
                )
                secure_state['fernet'] = fernet
                secure_state['fernet_key'] = fernet_key
                secure_state['salt'] = salt
                secure_state['master_pw'] = master_password
                secure_state['authenticated'] = True
                pwd_pwd = plaintext_creds
                pwd_options = list(pwd_pwd.keys())
                return True
            except ValueError as e:
                messagebox.showerror("Integrity Error", str(e))
                return False
            except InvalidToken:
                messagebox.showerror("Decryption Error", "Incorrect master password or corrupted data.")
                return False
        else:
            # Fresh install — no credentials yet
            fernet, salt = security.make_fernet(master_password)
            fernet_key, _ = security.derive_key(master_password, salt)
            secure_state['fernet'] = fernet
            secure_state['fernet_key'] = fernet_key
            secure_state['salt'] = salt
            secure_state['master_pw'] = master_password
            secure_state['authenticated'] = True
            pwd_pwd = {}
            pwd_options = []
            return True

    def reset():
        def yes():
            def check_mp():
                entry_mp_get = entry_mp.get()
                # Verify master password using bcrypt if hashed, or plaintext for legacy
                mp_verified = False
                if security.is_mp_hashed(usr_path_with_mp_fl):
                    with open(usr_path_with_mp_fl, 'rb') as f:
                        stored_hash = f.read().strip()
                    mp_verified = security.verify_master_password(entry_mp_get, stored_hash)
                else:
                    # Legacy plaintext check
                    try:
                        with open(usr_path_with_mp_fl, 'r') as f:
                            mp_verified = (f.read().strip() == entry_mp_get)
                    except FileNotFoundError:
                        mp_verified = False

                if mp_verified:
                    # Remove entire APM config directory
                    apm_folder = os.path.join(local_appdata, 'APM')
                    if os.path.exists(apm_folder):
                        import shutil
                        try:
                            shutil.rmtree(apm_folder)
                        except Exception:
                            pass

                    # Remove old credential files
                    for cred_path in [cred_full_path, cred_file_path, secure_cred_path]:
                        try:
                            os.remove(cred_path)
                        except FileNotFoundError:
                            pass

                    messagebox.showinfo("Restart", "APM has been sucessfully reset, please restart the program.")
                    reset_win.destroy()
                    mp_fl_fnd.destroy()
                    quit()
                else:
                    messagebox.showerror("Master Password", "Incorrect Master Password.")

            if os.path.exists(usr_path_with_mp_fl):
                mp_fl_fnd = ctk.CTkToplevel(win)
                mp_fl_fnd.title("Master Password Required")
                mp_fl_fnd.geometry('350x160')
                mp_fl_fnd.resizable(False, False)

                mp_fl_fnd.lift()
                mp_fl_fnd.attributes("-topmost", True)
                set_window_icon(mp_fl_fnd)

                dropdown_menu.place_forget()
                pwd_sh_btn.place_forget()
                pwd_copy_btn.place_forget()
                delete_cred_btn.place_forget()
                pwd_entry.place_forget()

                title_mp = ctk.CTkLabel(mp_fl_fnd, text="Master Password Required", font=('Arial', 16, "bold"))
                title_mp.pack(pady=20)

                entry_mp = ctk.CTkEntry(mp_fl_fnd, width=200, placeholder_text="Enter Master Password", show="*")
                entry_mp.pack(pady=5)

                enter_btn = ctk.CTkButton(mp_fl_fnd, text="        Enter      ", command=check_mp)
                enter_btn.pack(pady=10)
            else:
                def set_mp():
                    entry_mp_cntnts = entry_mp.get()
                    if not entry_mp_cntnts:
                        messagebox.showerror("Master Password", "Master password cannot be empty.")
                        return
                    # Hash with bcrypt before saving
                    mp_hash = security.hash_master_password(entry_mp_cntnts)
                    os.makedirs(os.path.dirname(usr_path_with_mp_fl), exist_ok=True)
                    with open(usr_path_with_mp_fl, 'wb') as mp:
                        mp.write(mp_hash)
                    messagebox.showinfo("Master Password", "Master Password set successfully.")
                    mp_nt_fnd.destroy()

                mp_nt_fnd = ctk.CTkToplevel(win)
                mp_nt_fnd.title("Master Password Creation")
                mp_nt_fnd.geometry('350x160')
                mp_nt_fnd.resizable(False, False)
                mp_nt_fnd.configure(background='black')

                mp_nt_fnd.lift()
                mp_nt_fnd.attributes("-topmost", True)
                set_window_icon(mp_nt_fnd)

                title_mp = ctk.CTkLabel(mp_nt_fnd, text="Set Master Password", font=('Arial', 16, "bold"))
                title_mp.pack(pady=20)

                entry_mp = ctk.CTkEntry(mp_nt_fnd, width=200, placeholder_text="Enter a Master Password", show="*")
                entry_mp.pack(pady=5)

                enter_btn = ctk.CTkButton(mp_nt_fnd, text="        Set        ", command=set_mp)
                enter_btn.pack(pady=10)

        def no():
            reset_win.destroy()

        reset_win = ctk.CTkToplevel(win)
        reset_win.title("Reset APM")

        reset_win.geometry('350x160')
        reset_win.resizable(False, False)

        reset_win.lift()
        reset_win.attributes("-topmost", True)
        set_window_icon(reset_win)

        title = ctk.CTkLabel(reset_win, text="Are you sure you want to reset APM?", font=('Arial', 16, "bold"))
        title.pack(pady=20)
        
        no_btn = ctk.CTkButton(reset_win, text="No", command=no)
        no_btn.pack(side="left", padx=(50, 10), pady=10)

        yes_btn = ctk.CTkButton(reset_win, text="Yes", command=yes)
        yes_btn.pack(side="right", padx=(10, 50), pady=10)

    def chk_lclapdt_fldr():
        target_folder_path = os.path.join(local_appdata, 'APM')
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)
        else:
            pass

    def cmn_pwds_chk():
        try:
            with open (cmn_pwds_path, 'r') as file:
                cmn_pwds = file.read()
                
                usr_cmn_pwd = cmn_pwds_chk_etry.get()
                if usr_cmn_pwd == "":
                    cmn_pwds_result_text.configure(text="Please enter a password to check.")
                elif usr_cmn_pwd in cmn_pwds:
                    cmn_pwds_result_text.configure(text="Frequently Used. Unsafe Password.")
                else:
                    cmn_pwds_result_text.configure(text="Not Frequently Used.")

        except Exception as e:
            messagebox.showerror(f"Error", "Unable to check password.")
            print(e)

    def scrn_sz_chk():
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        if screen_width < 1280 or screen_height < 720:
            messagebox.showwarning("Low Resolution Warning", f"Your screen resolution is {screen_width}x{screen_height}, For comfortable usage, please use a resolution of atleast 1280x720.")
        else:
            pass

    def m_pwd_win_func():
        
        legacy_plaintext_mp = security.detect_legacy_mp(usr_path_with_mp_fl)
        mp_exists = os.path.exists(usr_path_with_mp_fl)

        if mp_exists:
            def check_mp():
                entry_mp_get = entry_mp.get()
                if not entry_mp_get:
                    messagebox.showerror("Master Password", "Please enter your master password.")
                    return

                verified = False

                if legacy_plaintext_mp is not None:
                    # Legacy plaintext verification + auto-migration
                    if entry_mp_get == legacy_plaintext_mp:
                        verified = True
                else:
                    # New bcrypt verification
                    with open(usr_path_with_mp_fl, 'rb') as f:
                        stored_hash = f.read().strip()
                    verified = security.verify_master_password(entry_mp_get, stored_hash)

                if verified:
                    # If legacy format, migrate the master password hash now
                    if legacy_plaintext_mp is not None:
                        mp_hash = security.hash_master_password(entry_mp_get)
                        with open(usr_path_with_mp_fl, 'wb') as f:
                            f.write(mp_hash)

                    # Initialise secure session (loads/migrates credentials)
                    if init_secure_session(entry_mp_get):
                        # Re-place the credential-related widgets
                        dropdown_menu.place(x=450, y=150)
                        pwd_entry.place(x=450, y=200)
                        pwd_copy_btn.place(x=450, y=250)
                        pwd_sh_btn.place(x=575, y=250)
                        delete_cred_btn.place(x=702, y=250)
                        update_dropdown()
                        mp_fl_fnd.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to load credentials.")
                else:
                    messagebox.showerror("Master Password", "Incorrect Master Password.")

            # Temporarily hide the credential-related widgets
            dropdown_menu.place_forget()
            pwd_entry.place_forget()
            pwd_copy_btn.place_forget()
            pwd_sh_btn.place_forget()
            delete_cred_btn.place_forget()

            # Create the master password prompt window
            mp_fl_fnd = ctk.CTkToplevel(win)
            mp_fl_fnd.title("Master Password Required")
            mp_fl_fnd.geometry('350x160')
            mp_fl_fnd.resizable(False, False)

            mp_fl_fnd.lift()
            mp_fl_fnd.attributes("-topmost", True)
            set_window_icon(mp_fl_fnd)

            title_mp = ctk.CTkLabel(mp_fl_fnd, text="Master Password Required", font=('Arial', 16, "bold"))
            title_mp.pack(pady=20)

            entry_mp = ctk.CTkEntry(mp_fl_fnd, width=200, placeholder_text="Enter Master Password", show="*")
            entry_mp.pack(pady=5)

            enter_btn = ctk.CTkButton(mp_fl_fnd, text="Enter", command=check_mp)
            enter_btn.pack(pady=10)

        else:
            # No master password set — first-time setup
            def set_mp():
                entry_mp_cntnts = entry_mp.get()
                if not entry_mp_cntnts:
                    messagebox.showerror("Master Password", "Master password cannot be empty.")
                    return
                if len(entry_mp_cntnts) < 6:
                    messagebox.showwarning("Weak Password", "Master password should be at least 6 characters long.")
                    return

                # Confirm password
                confirm_pw = entry_mp_confirm.get()
                if entry_mp_cntnts != confirm_pw:
                    messagebox.showerror("Master Password", "Passwords do not match.")
                    return

                # Hash with bcrypt and save
                mp_hash = security.hash_master_password(entry_mp_cntnts)
                os.makedirs(os.path.dirname(usr_path_with_mp_fl), exist_ok=True)
                with open(usr_path_with_mp_fl, 'wb') as mp:
                    mp.write(mp_hash)

                # Initialise secure session
                init_secure_session(entry_mp_cntnts)
                update_dropdown()

                messagebox.showinfo("Master Password", "Master Password set successfully.")
                mp_nt_fnd.destroy()

            # Create the master password setup window
            mp_nt_fnd = ctk.CTkToplevel(win)
            mp_nt_fnd.title("Master Password Creation")
            mp_nt_fnd.geometry('350x180')
            mp_nt_fnd.resizable(False, False)

            mp_nt_fnd.lift()
            mp_nt_fnd.attributes("-topmost", True)
            set_window_icon(mp_nt_fnd)

            title_mp = ctk.CTkLabel(mp_nt_fnd, text="Set Master Password", font=('Arial', 16, "bold"))
            title_mp.pack(pady=10)

            entry_mp = ctk.CTkEntry(mp_nt_fnd, width=200, placeholder_text="Enter a Master Password", show="*")
            entry_mp.pack(pady=5)

            entry_mp_confirm = ctk.CTkEntry(mp_nt_fnd, width=200, placeholder_text="Confirm Master Password", show="*")
            entry_mp_confirm.pack(pady=5)

            enter_btn = ctk.CTkButton(mp_nt_fnd, text="Set", command=set_mp)
            enter_btn.pack(pady=10)

    def check_updts():
        version_url = "https://apm-version.tiiny.site"
        import requests
        version = requests.get(version_url)
        if version.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(version.content, 'html.parser')
            version_no = soup.find('h1')
            if version_no:
                final_version = version_no.text.strip()
                if final_version == "v2.4" :
                    messagebox.showinfo("Updates", "No new updates available.")
                elif final_version == "[SERVER SIDE FAILURE - FALLBACK]":
                    if platform.system() == "Windows":
                        import webbrowser
                        messagebox.showinfo("Updates", "Unable to update APM. Click Ok to view to view the releases page to update manually.")
                        webbrowser.open("https://github.com/VidyutPrabakaran1/AI-Password-Manager/releases")
                    elif platform.system() == "Linux":
                        import webbrowser
                        messagebox.showinfo("Updates", f"A new release is available . Click Ok to view the releases page.")
                        webbrowser.open("https://github.com/VidyutPrabakaran1/AI-Password-Manager/releases")

                else:
                    if platform.system() == "Linux":
                        import webbrowser
                        messagebox.showinfo("Updates", f"A new release is available : {final_version} . Click Ok to view the releases page.")
                        webbrowser.open("https://github.com/VidyutPrabakaran1/AI-Password-Manager/releases")
                    elif platform.system() == "Windows":
                        import webbrowser
                        messagebox.showinfo("Updates", f"A new release is available : {final_version} . Click Ok to view the releases page.")
                        webbrowser.open("https://github.com/VidyutPrabakaran1/AI-Password-Manager/releases")
                    else:
                        import webbrowser
                        messagebox.showinfo("Updates", f"A new release is available : {final_version} . Click Ok to view the releases page.")
                        webbrowser.open("https://github.com/VidyutPrabakaran1/AI-Password-Manager/releases")
            else:
                messagebox.showerror("Updates", "Unable to check for updates.")

        else:
            messagebox.showerror("Updates", "Unable to check for updates.")

    def trans_check():
        try:
            with open (usr_path_with_trns_fl, 'r') as file:
                trans_cmd = file.read().strip()
                try:
                    trans_val = int(trans_cmd)
                    return trans_val
                except ValueError:
                    return 0
        except FileNotFoundError:
            with open (usr_path_with_trns_fl, 'w') as file:
                file.write('0')
        
    def trans_aply_fr():
        trans_val_agn = trans_check()
        if trans_val_agn == 1:
            win.attributes('-alpha', 0.7)
        else:
            win.attributes('-alpha', 1)

    def trans_act():
        trans_val_chk_agn = trans_check()
        if trans_val_chk_agn == 1:
            with open(usr_path_with_trns_fl, 'w') as file:
                file.write('0')
            messagebox.showinfo("Restart", "Restart the program for the changes to take effect.")
            sys.exit()

        elif trans_val_chk_agn == 0:
            with open(usr_path_with_trns_fl, 'w') as file:
                file.write('1')
            messagebox.showinfo("Restart", "Restart the program for the changes to take effect.")
            sys.exit()
        else:
            with open(usr_path_with_trns_fl, 'w') as file:
                file.write('1')
            messagebox.showinfo("Restart", "Restart the program for the changes to take effect.")
            sys.exit()

    def fdbk():
        url = 'https://forms.gle/gAvLGKMQPSQe3NyJ8'
        import webbrowser
        webbrowser.open(url)

    def usrnme_gen():
        import random

        with open (usrnme_model, 'r') as file:
            words = file.read().splitlines()

        def generate_usrnme():
            return random.choice(words) + str(random.randint(100, 9999))
        
        usrnme_gen_entry.delete(0, "end")
        usrnme_gen_entry.insert(0, generate_usrnme())

    def usrnme_clear():
        usrnme_gen_entry.delete(0, "end")

    def mode_dark():
        with open (usr_path_with_cnfg_fl, 'w') as file:
            file.write('1')
        messagebox.showinfo("Restart", "Restart the program for the changes to take effect.")
        sys.exit()

    def mode_light():
        with open (usr_path_with_cnfg_fl, 'w') as file:
            file.write('2')
        messagebox.showinfo("Restart", "Restart the program for the changes to take effect.")
        sys.exit()

    # Ensure mode_grab() retrieves the mode state correctly
    def mode_grab():
        try:
            with open(usr_path_with_cnfg_fl, 'r') as file:
                mode_val = file.read().strip()
                try:
                    val_cnv = int(mode_val)
                    return val_cnv
                except ValueError:
                    return 1  # Default to dark mode if the value is invalid
        except FileNotFoundError:
            os.makedirs(os.path.dirname(usr_path_with_cnfg_fl), exist_ok=True)
            with open(usr_path_with_cnfg_fl, 'w') as file:
                file.write('1')  # Default to dark mode
            return 1

    # Apply the appearance mode based on the mode state
    def app_mode():
        if mode_state == 1:
            ctk.set_appearance_mode("dark")
        elif mode_state == 2:
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")  # Default to dark mode

    # Call mode_grab() and app_mode() during initialization
    mode_state = mode_grab()
    app_mode()

    def internet_check():
        import requests
        try:
            check = requests.get("https://www.example.com", timeout = 5)
            if check.status_code == 200:
                pass
            else:
                messagebox.showwarning("Internet Connection", "You're not connected to the internet. Some features will not work.")

        except requests.ConnectionError:
            messagebox.showerror("Internet Connection", "Failed to connect to the internet. Restart the program to try again. Without internet some features won't work.")

    def update_dropdown():
        """Update the dropdown menu with the latest credentials."""
        dropdown_menu.configure(values=pwd_options)  # Update the dropdown options
        dropdown_var.set("")  # Reset the selected value to empty

    def delete_cred():
        """Delete the selected credential."""
        selected_option = dropdown_var.get()
        if selected_option and selected_option in pwd_pwd:
            del pwd_pwd[selected_option]  # Remove the credential from the dictionary
            pwd_options.remove(selected_option)  # Remove it from the options list
            dropdown_var.set("")  # Reset the dropdown selection
            pwd_entry.delete(0, ctk.END)  # Clear the password entry field
            save_credentials()  # Save the updated credentials
            update_dropdown()  # Update the dropdown menu
        else:
            messagebox.showerror("Error", "Please select a credential to delete.")

    def add_cred():
        """Add a new credential (stored as plaintext in memory, encrypted on save)."""
        if not secure_state['authenticated']:
            messagebox.showerror("Error", "Please authenticate with your master password first.")
            return

        new_cred = new_cred_entry.get()
        new_cred1 = new_cred_entry1.get()  # Plaintext password

        if new_cred in pwd_pwd:
            messagebox.showerror("Error", "This Credential already exists.")
            return

        if new_cred and new_cred1:
            pwd_options.append(new_cred)
            pwd_pwd[new_cred] = new_cred1  # Store plaintext in memory dict
            save_credentials()  # Encrypt and save to disk
            update_dropdown()
            new_cred_entry.delete(0, ctk.END)
            new_cred_entry1.delete(0, ctk.END)
        else:
            messagebox.showerror("Error", "Please enter both Account ID and Password.")


    def save_credentials():
        """Save credentials using the secure v2 format (JSON + HMAC)."""
        if not secure_state['authenticated']:
            messagebox.showerror("Glace APM", "Cannot save: not authenticated.")
            return
        try:
            security.save_credentials_secure(
                credentials=pwd_pwd,
                fernet=secure_state['fernet'],
                fernet_key=secure_state['fernet_key'],
                salt=secure_state['salt'],
                filepath=secure_cred_path,
            )
        except Exception as e:
            messagebox.showerror("Glace APM", f"Error saving credentials: {e}")

    def load_credentials():
        return {}

    '''
    def save_credentials():
        import json
        try:
            json_data = {k: v.decode() for k, v in pwd_pwd.items()}
            with open(cred_file_path, 'w') as f:
                json.dump(json_data, f)
        except Exception as e:
            messagebox.showerror("Glace APM", f"Error saving credentials: {e}")

    def load_credentials():
        import json
        try:
            if os.path.exists(cred_file_path):  # JSON already exists
                with open(cred_file_path, 'r') as f:
                    data = json.load(f)
                return {k: v.encode() for k, v in data.items()}

            elif os.path.exists(cred_full_path):  # Migrate from .pkl
                with open(cred_full_path, 'rb') as f:
                    import pickle
                    data = pickle.load(f)

                # Save as JSON
                try:
                    json_data = {k: v.decode() for k, v in data.items()}
                    with open(cred_file_path, 'w') as f:
                        json.dump(json_data, f)
                    os.remove(cred_full_path)  # only delete if save worked
                except Exception as save_error:
                    messagebox.showerror("APM", f"Failed to migrate credentials to JSON: {save_error}")
                    return data  # fallback to in-memory usage

                return data

            else:
                return {}

        except Exception as e:
            messagebox.showerror("Glace APM", f"Error loading credentials: {e}")
            return {}
    '''

    def pwd_hide():
        nonlocal is_shown  # Access the nonlocal variable
        pwd_entry.delete(0, 'end')
        is_shown = 0

    def pwd_show():
        nonlocal is_shown
        selected_option = dropdown_var.get()

        if selected_option in pwd_pwd:
            pwd_entry.delete(0, 'end')
            pwd_entry.insert(0, pwd_pwd[selected_option])
            is_shown = 1
        else:
            messagebox.showerror("Error", "No password found for the selected credential.")

    def pwd_sh_clicked():
        nonlocal is_shown  # Access the nonlocal variable
        if is_shown == 0:
            pwd_show()
            pwd_sh_btn.configure(text=" Hide Password")
        else:
            pwd_hide()
            pwd_sh_btn.configure(text="Show Password")

    def pwd_copy_clicked():
        selected_option = dropdown_var.get()
        if selected_option in pwd_pwd:
            win.clipboard_clear()
            win.clipboard_append(pwd_pwd[selected_option])
            win.update()
            messagebox.showinfo("Glace APM", "Password copied to clipboard.")
        else:
            messagebox.showerror("Error", "No password found for the selected credential.")

    def pwd_check_clicked():
        password=pwd_check.get()
        if password == "":
            pwd_check_result_text.configure(text="Please enter a password to check.")
        else:
            def get_password_strength(password):
                import zxcvbn
                result = zxcvbn.zxcvbn(password)
                return result['score']
            strength_score = get_password_strength(password)
            if strength_score == 4:
                pwd_check_result_text.configure(text=f"Strength : Strong | Score : {strength_score}/4")
            elif strength_score == 3 :
                pwd_check_result_text.configure(text=f"Strength : Moderate | Score : {strength_score}/4")
            elif strength_score == 2 :
                pwd_check_result_text.configure(text=f"Strength : Ok | Score : {strength_score}/4")
            elif strength_score == 1 :
                pwd_check_result_text.configure(text=f"Strength : Low | Score : {strength_score}/4")
            elif strength_score == 0 :
                pwd_check_result_text.configure(text=f"Strength : Very Low | Score : {strength_score}/4")
            else:
                pwd_check_result_text.configure(text="Unable to obtain score.")

    def l_12():
        nonlocal length
        length = 12
        btn_12 = 12
        temp_var = length
        length = btn_12

    def l_16():
        nonlocal length
        length = 12
        btn_16 = 16
        temp_var_2 = length
        length = btn_16

    def gen_l12():
        try:
            import json
            import random

            with open(pwd_model) as f:
                model = json.load(f)

            def generate_password(length=12, n=3):
                prefix = random.choice(list(model.keys()))
                result = prefix
                while len(result) < length:
                    next_chars = model.get(prefix)
                    if not next_chars:
                        prefix = random.choice(list(model.keys()))
                        continue
                    next_char = random.choice(next_chars)
                    result += next_char
                    prefix = result[-n:]
                return result
            
            pwd_gen.delete(0, 'end')
            pwd_gen.insert(0, generate_password(length=12, n=3))
        except FileNotFoundError:
            pwd_gen.delete(0, 'end')
            pwd_gen.insert(0, "Unable to generate password. Try again.")

    def gen_l16():
        try:
            import json
            import random

            with open(pwd_model) as f:
                model = json.load(f)

            def generate_password(length=16, n=3):
                prefix = random.choice(list(model.keys()))
                result = prefix
                while len(result) < length:
                    next_chars = model.get(prefix)
                    if not next_chars:
                        prefix = random.choice(list(model.keys()))
                        continue
                    next_char = random.choice(next_chars)
                    result += next_char
                    prefix = result[-n:]
                return result
            
            pwd_gen.delete(0, 'end')
            pwd_gen.insert(0, generate_password(length=16, n=3))
        except FileNotFoundError:
            pwd_gen.delete(0, 'end')
            pwd_gen.insert(0, "Unable to generate password. Try again.")

    def pwd_gen_clicked():
        nonlocal length
        if length == 12:
            gen_l12()
        elif length == 16:
            gen_l16()
        else:
            gen_l12()
            
    def pwd_gen_clear():
        pwd_gen.delete(0, 'end')

    # UI

    win = ctk.CTk()
    win.title("Glace APM")

    # Theme Mode

    usr_path_with_thm_fl = os.path.join(local_appdata, 'APM', 'theme_mode.txt')

    themes_dict = {
        "Default (Dark Blue)": "dark-blue",
        "Red": red_theme,
        "Orange": orange_theme,
        "Green": green_theme,
        "Blue": blue_theme,
        "Violet": violet_theme
    }

    def change_theme(choice):
        with open(usr_path_with_thm_fl, 'w') as file:
            file.write(choice)
        messagebox.showinfo("Restart", "Restart the program for the theme changes to take effect.")
        sys.exit()

    def theme_apply():
        try:
            with open(usr_path_with_thm_fl, 'r') as file:
                thm_choice = file.read().strip()
                if thm_choice in themes_dict:
                    if thm_choice == "Default (Dark Blue)":
                        ctk.set_default_color_theme("dark-blue")
                    else:
                        ctk.set_default_color_theme(themes_dict[thm_choice])
                else:
                    ctk.set_default_color_theme("dark-blue")
        except FileNotFoundError:
            ctk.set_default_color_theme("dark-blue")

    # Center the window manually
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    window_width = 1290
    window_height = 620
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    win.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    win.resizable(False, False)

    # Set the icon

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS  # This is used in the PyInstaller bundle
        except AttributeError:
            base_path = os.path.abspath(os.path.dirname(__file__))

        return os.path.join(base_path, relative_path)

    icon_path_ico = resource_path("_itnrl/icons/apm.ico")
    icon_sizes = ['16x16', '32x32', '48x48', '64x64', '128x128', '256x256']
    photo_icons = []
    for sz in icon_sizes:
        png_p = resource_path(f"_itnrl/icons/apm-{sz}.png")
        if os.path.exists(png_p):
            try:
                photo_icons.append(PhotoImage(file=png_p))
            except Exception:
                pass
    if not photo_icons:
        fallback_png = resource_path("_itnrl/icons/apm-128x128.png")
        if os.path.exists(fallback_png):
            try:
                photo_icons.append(PhotoImage(file=fallback_png))
            except Exception:
                pass

    def set_window_icon(window):
        # 1. Tkinter 32-bit ARGB iconphoto (cross-platform & smooth scaling)
        if photo_icons:
            try:
                window.iconphoto(False, *photo_icons)
            except Exception:
                pass

        # 2. Windows Native Win32 DPI-aware icon loading for pixel-perfect titlebars
        if platform.system() == "Windows":
            try:
                window._iconbitmap_method_called = True
                window.update_idletasks()
                hwnd = ctypes.windll.user32.GetParent(window.winfo_id()) or window.winfo_id()

                # Get exact DPI-scaled metrics for titlebar (small) and taskbar (big)
                cx_sm = ctypes.windll.user32.GetSystemMetrics(49)  # SM_CXSMICON
                cy_sm = ctypes.windll.user32.GetSystemMetrics(50)  # SM_CYSMICON
                cx_lg = ctypes.windll.user32.GetSystemMetrics(11)  # SM_CXICON
                cy_lg = ctypes.windll.user32.GetSystemMetrics(12)  # SM_CYICON

                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x00000010

                hicon_sm = ctypes.windll.user32.LoadImageW(0, icon_path_ico, IMAGE_ICON, cx_sm, cy_sm, LR_LOADFROMFILE)
                hicon_lg = ctypes.windll.user32.LoadImageW(0, icon_path_ico, IMAGE_ICON, cx_lg, cy_lg, LR_LOADFROMFILE)

                WM_SETICON = 0x0080
                if hicon_sm:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon_sm)  # ICON_SMALL (Titlebar)
                if hicon_lg:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon_lg)  # ICON_BIG (Taskbar / Alt+Tab)
            except Exception:
                try:
                    window.iconbitmap(icon_path_ico)
                except Exception:
                    pass

    set_window_icon(win)

    chk_lclapdt_fldr()

    theme_apply()

    mode_change_init = 1

    internet_check()

    trans_aply_fr()

    scrn_sz_chk()

    title = ctk.CTkLabel(win, text="Glace APM", font=("Arial", 25, "bold"))
    title.pack(pady=30, padx=40, anchor="nw")

    # Password Manager Frame

    pwd_gen_text = ctk.CTkLabel(win, text="Password Generator  ", font=("Arial", 20, "bold"))
    pwd_gen_text.pack(pady=10, padx=40, anchor="nw")

    pwd_gen = ctk.CTkEntry(win, placeholder_text="Default password length is 12.", width=310, font=("Arial", 15))
    pwd_gen.pack(pady=10, padx=40, anchor="nw")

    pwd_gen_frame = ctk.CTkFrame(win)
    pwd_gen_frame.pack(pady=10, padx=40, anchor="nw")

    pwd_gen_btn = ctk.CTkButton(pwd_gen_frame, text="Generate Password", command=pwd_gen_clicked, width=150, font=("Arial", 15))
    pwd_gen_btn.pack(side="left", padx=(0, 10))

    pwd_gen_clear = ctk.CTkButton(pwd_gen_frame, text="Clear", command=pwd_gen_clear, width=60, font=("Arial", 15))
    pwd_gen_clear.pack(side="left", padx=(0, 10))

    pwd_gen_l_12 = ctk.CTkButton(pwd_gen_frame, text="12", command=l_12, width=20, font=("Arial", 15))
    pwd_gen_l_12.pack(side="left", padx=(0, 10))

    pwd_gen_l_16 = ctk.CTkButton(pwd_gen_frame, text="16", command=l_16, width=20, font=("Arial", 15))
    pwd_gen_l_16.pack(side="left")

    # Password Strength Checker Frame

    pwd_check_text = ctk.CTkLabel(win, text="Password Strength Checker  ", font=("Arial", 20, "bold"))
    pwd_check_text.pack(pady=10, padx=40, anchor="nw")

    pwd_check = ctk.CTkEntry(win, placeholder_text="Enter password to check strength.", width=310, font=("Arial", 15))
    pwd_check.pack(pady=10, padx=40, anchor="nw")

    pwd_check_frame = ctk.CTkFrame(win)
    pwd_check_frame.pack(pady=10, padx=40, anchor="nw")

    pwd_check_result_text = ctk.CTkLabel(pwd_check_frame, text="Password strength will be displayed here.", width=290, font=("Arial", 15))
    pwd_check_result_text.pack(pady=0, padx=10)

    pwd_check_btn = ctk.CTkButton(win, text="Check Password", command=pwd_check_clicked, width=150, font=("Arial", 15))
    pwd_check_btn.pack(pady=10, padx=40, anchor="nw")

    # Username Generator Frame

    usrnme_gen_text = ctk.CTkLabel(win, text="Username Generator  ", font=("Arial", 20, "bold"))
    usrnme_gen_text.pack(pady=10, padx=40, anchor="nw")

    usrnme_gen_entry = ctk.CTkEntry(win, placeholder_text="Generated Username will appear here.", width=310, font=("Arial", 15))
    usrnme_gen_entry.pack(pady=10, padx=40, anchor="nw")

    usrnme_gen_btn = ctk.CTkButton(win, text="Generate Username", command=usrnme_gen, width=150, font=("Arial", 15))
    usrnme_gen_btn.pack(side="left", pady=10, padx=(40, 10), anchor="nw")

    usrnme_gen_clear = ctk.CTkButton(win, text="Clear", command=usrnme_clear, width=60, font=("Arial", 15))
    usrnme_gen_clear.pack(side="left", pady=10, padx=(0, 40), anchor="nw")

    # Your Credentials Dropdown Frame

    creds_txt = ctk.CTkLabel(win, text="Your Credentials  ", font=("Arial", 20, "bold"))
    creds_txt.place(x=450, y=99)

    # Load credentials from file
    pwd_pwd = load_credentials()  # Dictionary to hold credentials (loaded from file)
    #print("Loaded credentials:", pwd_pwd) 

    # Populate the dropdown options from the loaded credentials
    pwd_options = list(pwd_pwd.keys())  # Extract the keys (account names) from the dictionary

    # Initialize the dropdown menu
    dropdown_var = ctk.StringVar(value="Select a Credential")  # Variable to hold the selected dropdown value
    dropdown_menu = ctk.CTkOptionMenu(win, variable=dropdown_var, values=pwd_options, width=382, font=("Arial", 15),command=None)
    dropdown_menu.place(x=450, y=150)

    pwd_entry = ctk.CTkEntry(win, placeholder_text="Password will appear here.", width=382, font=("Arial", 15))
    pwd_entry.place(x=450, y=200)

    pwd_copy_btn = ctk.CTkButton(win, text="Copy Password", command=pwd_copy_clicked, width=100, font=("Arial", 15))
    pwd_copy_btn.place(x=450, y=250)

    pwd_sh_btn = ctk.CTkButton(win, text="Show Password", command=pwd_sh_clicked, width=100, font=("Arial", 15))
    pwd_sh_btn.place(x=575, y=250)

    delete_cred_btn = ctk.CTkButton(win, text="Delete Credential", command=delete_cred, width=100, font=("Arial", 15))
    delete_cred_btn.place(x=702, y=250)

    # Add Credentials Frame

    new_pwd_txt = ctk.CTkLabel(win, text="Add New Credentials  ", font=("Arial", 20, "bold"))
    new_pwd_txt.place(x=450, y=320)

    new_cred_entry = ctk.CTkEntry(win, placeholder_text="Enter Your Account ID/Name/Username", width=382, font=("Arial", 15))
    new_cred_entry.place(x=450, y=370)

    new_cred_entry1 = ctk.CTkEntry(win, placeholder_text="Enter Your Password", width=382, font=("Arial", 15))
    new_cred_entry1.place(x=450, y=420)

    add_cred_btn = ctk.CTkButton(win, text="Add Credential", command=add_cred, width=150, font=("Arial", 15))
    add_cred_btn.place(x=450, y=470)

    # Common Passwords Checker Frame

    cmn_pwds_chk_txt = ctk.CTkLabel(win, text="Common Passwords Check  ", font=("Arial", 20, "bold"))
    cmn_pwds_chk_txt.place(x=930, y=99)

    cmn_pwds_chk_etry = ctk.CTkEntry(win, placeholder_text="Enter password to check.", width=290, font=("Arial", 15))
    cmn_pwds_chk_etry.place(x=930, y=150)

    cmn_pwds_result_text_frame = ctk.CTkFrame(win)
    cmn_pwds_result_text_frame.place(x=930, y=200)

    cmn_pwds_result_text = ctk.CTkLabel(cmn_pwds_result_text_frame, text="Result will be displayed here.", width=270, font=("Arial", 15))
    cmn_pwds_result_text.pack(pady=0, padx=10)

    cmn_pwds_chk_btn = ctk.CTkButton(win, text="Check Password", command=cmn_pwds_chk, width=150, font=("Arial", 15))
    cmn_pwds_chk_btn.place(x=930, y=250)

    # App Mode

    app_mode_txt = ctk.CTkLabel(win, text="App Mode  ", font=("Arial", 20, "bold"))
    app_mode_txt.place(x=930, y=320)

    light_mode_btn = ctk.CTkButton(win, text="Light Mode", command=mode_light, width=100, font=("Arial", 15))
    light_mode_btn.place(x=930, y=370)

    dark_mode_btn = ctk.CTkButton(win, text="Dark Mode", command=mode_dark, width=100, font=("Arial", 15))
    dark_mode_btn.place(x=1050, y=370)

    if sys.platform == "win32":
        trans_btn = ctk.CTkButton(win, text="Transparency Mode", command=trans_act, width=150, font=("Arial", 15))
        trans_btn.place(x=930, y=420)
    else:
        trans_btn = ctk.CTkButton(win, text="Transparency Mode", command=None, width=150, font=("Arial", 15))

    # Themes UI

    theme_txt = ctk.CTkLabel(win, text="Theme  ", font=("Arial", 20, "bold"))
    theme_txt.place(x=930, y=470)

    current_theme = "Default (Dark Blue)"
    try:
        with open(usr_path_with_thm_fl, 'r') as file:
            saved_theme = file.read().strip()
            if saved_theme in themes_dict:
                current_theme = saved_theme
    except FileNotFoundError:
        pass

    theme_dropdown_var = ctk.StringVar(value=current_theme)
    theme_dropdown = ctk.CTkOptionMenu(win, variable=theme_dropdown_var, values=list(themes_dict.keys()), command=change_theme, width=150, font=("Arial", 15))
    theme_dropdown.place(x=930, y=520)

    # Bottom Bar Buttons

    about_btn = ctk.CTkButton(win, text="About", command=about, width=50, font=("Arial", 15))
    about_btn.place(x=1220, y=580)

    fdbk_btn = ctk.CTkButton(win, text="Feedback", command=fdbk, width=50, font=("Arial", 15))
    fdbk_btn.place(x=1135, y=580)

    updt_btn = ctk.CTkButton(win, text="Update", command=check_updts, width=50, font=("Arial", 15))
    updt_btn.place(x=1070, y=580)

    reset_btn = ctk.CTkButton(win, text="Reset", command=reset, width=50, font=("Arial", 15))
    reset_btn.place(x=1013, y=580)

    m_pwd_win_func()
    app_mode()
    update_dropdown()
    win.mainloop()


if __name__ == "__main__":
    main()