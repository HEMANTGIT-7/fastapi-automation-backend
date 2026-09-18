import customtkinter as ctk
import httpx
import threading
import webbrowser
import os
import subprocess
import tkinter.messagebox as msgbox
from phone_audit_window import PhoneAuditWindow

# Theme Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BASE_API_URL = "http://127.0.0.1:8000"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ Secure Automation Portal")
        self.geometry("450x680")  # Height adjustment for Text Box
        self.resizable(False, False)
        self.logged_in_user = ""

        # Container Frame
        self.main_container = ctk.CTkFrame(self, corner_radius=20, fg_color="#0d1117")
        self.main_container.pack(pady=15, padx=15, fill="both", expand=True)

        self.show_login_ui()

    def show_login_ui(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Copyright Label At The Top
        copyright_label = ctk.CTkLabel(
            self.main_container, 
            text="© COPYRIGHT BY HEMANT", 
            font=ctk.CTkFont(size=10, weight="bold"), 
            text_color="#8b949e"
        )
        copyright_label.pack(pady=(15, 0))

        # Login Heading
        title = ctk.CTkLabel(self.main_container, text="🔒 SECURITY PORTAL", font=ctk.CTkFont(size=22, weight="bold"), text_color="#58a6ff")
        title.pack(pady=(25, 10))

        subtitle = ctk.CTkLabel(self.main_container, text="Enter API-Assigned Credentials", font=ctk.CTkFont(size=12), text_color="#8b949e")
        subtitle.pack(pady=(0, 25))

        # Inputs
        self.user_entry = ctk.CTkEntry(self.main_container, placeholder_text="Username", width=280, height=45, corner_radius=25)
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self.main_container, placeholder_text="Password", show="*", width=280, height=45, corner_radius=25)
        self.pass_entry.pack(pady=10)

        # Login Button
        self.login_btn = ctk.CTkButton(
            self.main_container, 
            text="UNLOCK DASHBOARD", 
            command=self.start_login_thread, 
            width=280, 
            height=45, 
            corner_radius=25,
            fg_color="#8957e5", 
            hover_color="#6e40c9",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.login_btn.pack(pady=(25, 0))

    def start_login_thread(self):
        self.login_btn.configure(state="disabled", text="VERIFYING...")
        threading.Thread(target=self.verify_login_api, daemon=True).start()

    def verify_login_api(self):
        username = self.user_entry.get().strip().upper()
        password = self.pass_entry.get().strip()

        if not username or not password:
            msgbox.showerror("Error", "Please fill both Username and Password!")
            self.login_btn.configure(state="normal", text="UNLOCK DASHBOARD")
            return

        try:
            auth_payload = {"username": username, "password": password}
            res = httpx.post(f"{BASE_API_URL}/verify-user", json=auth_payload, timeout=5.0)

            if res.status_code == 200:
                self.logged_in_user = username
                self.after(0, self.show_dashboard_ui)
            else:
                msgbox.showerror("Access Denied", "Invalid Username or Password!")
        except Exception as e:
            msgbox.showerror("Server Offline", f"Could not connect to authentication API!\n\nError: {e}")
        finally:
            self.login_btn.configure(state="normal", text="UNLOCK DASHBOARD")

    def show_dashboard_ui(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Copyright Label At The Top
        copyright_label = ctk.CTkLabel(
            self.main_container, 
            text="© COPYRIGHT BY HEMANT", 
            font=ctk.CTkFont(size=10, weight="bold"), 
            text_color="#8b949e"
        )
        copyright_label.pack(pady=(10, 0))

        # Header
        header = ctk.CTkLabel(self.main_container, text="⚡ CONTROL CENTER", font=ctk.CTkFont(size=20, weight="bold"), text_color="#238636")
        header.pack(pady=(10, 2))

        user_info = ctk.CTkLabel(self.main_container, text=f"Welcome, {self.logged_in_user}", font=ctk.CTkFont(size=12), text_color="#8b949e")
        user_info.pack(pady=(0, 10))

        # Switches variables
        self.yt_var = ctk.BooleanVar(value=False)
        self.opt2_var = ctk.BooleanVar(value=False)
        self.cleaner_var = ctk.BooleanVar(value=False)
        self.opt4_var = ctk.BooleanVar(value=False)
        self.opt5_var = ctk.BooleanVar(value=False)
        self.phone_audit_var = ctk.BooleanVar(value=False)

       switches = [
    ("Option 1: START YOUTUBE", self.yt_var, self.on_youtube_toggle),
    ("Option 2: START CHATGPT", self.opt2_var, self.on_chatgpt_toggle),
    ("Option 3: RUN SUPER CLEANER", self.cleaner_var, self.on_cleaner_toggle),
    ("Option 4: OPEN FREE MOVIE SITE", self.opt4_var, self.on_filmywap_toggle),
    ("Option 5: Live Terminal Debug Logs", self.opt5_var, self.on_generic_toggle),
    ("Option 6: 📱 PHONE NUMBER AUDIT", self.phone_audit_var, self.on_phone_audit_toggle)
]

        switches_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        switches_frame.pack(pady=5, padx=20, fill="x")

        for text, var, callback in switches:
            switch = ctk.CTkSwitch(
                switches_frame, 
                text=text, 
                variable=var, 
                onvalue=True, 
                offvalue=False,
                command=callback,
                progress_color="#238636",
                button_color="#58a6ff",
                button_hover_color="#79c0ff",
                font=ctk.CTkFont(size=13)
            )
            switch.pack(pady=6, anchor="w", padx=20)

        # Bottom Feature Request Section
        request_frame = ctk.CTkFrame(self.main_container, fg_color="#161b22", corner_radius=15)
        request_frame.pack(pady=(15, 10), padx=15, fill="x")

        req_title = ctk.CTkLabel(request_frame, text="💡 Request New Feature", font=ctk.CTkFont(size=12, weight="bold"), text_color="#58a6ff")
        req_title.pack(pady=(8, 4))

        self.feature_box = ctk.CTkTextbox(request_frame, height=65, corner_radius=10, font=ctk.CTkFont(size=11))
        self.feature_box.pack(pady=5, padx=10, fill="x")

        self.send_btn = ctk.CTkButton(
            request_frame, 
            text="SEND REQUEST", 
            command=self.submit_feature_request, 
            height=32, 
            corner_radius=15,
            fg_color="#1f6feb", 
            hover_color="#388bfd",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.send_btn.pack(pady=(5, 8))

    def submit_feature_request(self):
        text_content = self.feature_box.get("1.0", "end-1c").strip()
        if not text_content:
            msgbox.showwarning("Warning", "Please write a feature request first!")
            return

        self.send_btn.configure(state="disabled", text="SENDING...")
        threading.Thread(target=self._send_feature_api, args=(text_content,), daemon=True).start()

    def _send_feature_api(self, text_content):
        try:
            payload = {"username": self.logged_in_user, "feature_text": text_content}
            res = httpx.post(f"{BASE_API_URL}/submit-feature", json=payload, timeout=5.0)
            if res.status_code == 200:
                self.feature_box.delete("1.0", "end")
                msgbox.showinfo("Submitted", "Feature Request Sent to Admin!")
            else:
                msgbox.showerror("Error", "Failed to submit request.")
        except Exception as e:
            msgbox.showerror("Error", f"Could not reach server!\n{e}")
        finally:
            self.send_btn.configure(state="normal", text="SEND REQUEST")

    # Event Actions
    def on_youtube_toggle(self):
        if self.yt_var.get():
            try:
                os.system("start https://www.youtube.com")
            except Exception:
                webbrowser.open("https://www.youtube.com")
            threading.Thread(target=self.send_api_request, daemon=True).start()

    def on_chatgpt_toggle(self):
        if self.opt2_var.get():
            try:
                os.system("start https://chatgpt.com")
            except Exception:
                webbrowser.open("https://chatgpt.com")
            threading.Thread(target=self.send_api_request, daemon=True).start()

    def on_cleaner_toggle(self):
        if self.cleaner_var.get():
            threading.Thread(target=self.execute_super_cleaner, daemon=True).start()
            threading.Thread(target=self.send_api_request, daemon=True).start()

    def execute_super_cleaner(self):
        bat_script = r"""@echo off
TITLE SYSTEM MAINTENANCE TOOL
del /s /f /q %temp%\*.* >nul 2>&1
rd /s /q %temp% >nul 2>&1
md %temp% >nul 2>&1
del /s /f /q %windir%\temp\*.* >nul 2>&1
rd /s /q %windir%\temp >nul 2>&1
md %windir%\temp >nul 2>&1
ipconfig /flushdns >nul 2>&1
exit
"""
        cleaner_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "super_cleaner.bat")
        try:
            with open(cleaner_file, "w") as f:
                f.write(bat_script)
            subprocess.run(f'powershell -Command "Start-Process \'{cleaner_file}\' -Verb RunAs"', shell=True)
        except Exception as e:
            msgbox.showerror("Cleaner Error", f"Failed to execute Super Cleaner:\n{e}")

    def on_filmywap_toggle(self):
        if self.opt4_var.get():
            try:
                os.system("start https://www.filmy4wap.tv.in/")
            except Exception:
                webbrowser.open("https://www.filmy4wap.tv.in/")
            threading.Thread(target=self.send_api_request, daemon=True).start()
     
   def on_phone_audit_toggle(self):
    if self.phone_audit_var.get():
        try:
            PhoneAuditWindow(master=self)
        except Exception as e:
            msgbox.showerror("Error", f"Could not open audit window:\n{e}")
        # Switch ko wapas off kar do
        self.after(500, lambda: self.phone_audit_var.set(False))
        
    def on_generic_toggle(self):
        threading.Thread(target=self.send_api_request, daemon=True).start()

    def send_api_request(self):
        try:
            payload = {"target_uid": "123456789", "count": 10}
            httpx.post(f"{BASE_API_URL}/add-likes", json=payload, timeout=5.0)
        except Exception as e:
            msgbox.showerror("Connection Error", f"Server not reachable!\n\nError: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
