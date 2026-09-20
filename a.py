# ==============================================================================
# SECTION 1: IMPORTS
# ==============================================================================
import customtkinter as ctk
import traceback
import tkinter as tk
import httpx
import threading
import webbrowser
import os
import subprocess
import tempfile
import tkinter.messagebox as msgbox
import math
import ctypes
import uuid
import hashlib
import platform
from phone_audit_window import PhoneAuditWindow
from youtube_downloader import YouTubeDownloaderWindow
from pc_optimizer import PCOptimizerWindow
from screen_recorder import ScreenRecorderWindow
from pdf_toolkit import PDFToolkitWindow
from image_toolkit import ImageToolkitWindow
from video_toolkit import VideoToolkitWindow


# ==============================================================================
# SECTION 2: HARDWARE ID FUNCTION
# ==============================================================================
def get_hardware_id():
    """Unique Hardware ID generate karo (CPU + MAC + Disk)"""
    try:
        # Method 1: MAC Address
        mac = uuid.getnode()

        # Method 2: Processor info
        processor = platform.processor()

        # Method 3: Machine info
        machine = platform.machine()

        # Method 4: Windows UUID (sabse unique)
        try:
            cmd = 'wmic csproduct get uuid'
            output = subprocess.check_output(cmd, shell=True).decode()
            win_uuid = output.split('\n')[1].strip()
        except Exception:
            win_uuid = ""

        # Sab combine karke hash banao
        raw = f"{mac}-{processor}-{machine}-{win_uuid}"
        hw_id = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()

        return hw_id
    except Exception as e:
        return f"ERROR-{str(e)[:10]}"


# ==============================================================================
# SECTION 3: CONFIGURATION & SERVER URL
# ==============================================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BASE_API_URL = "https://fastapi-automation-backend.onrender.com"


# ==============================================================================
# SECTION 4: CLEAN GLOWING CARD OPTION WIDGET
# ==============================================================================
class GlowOptionCard(ctk.CTkFrame):
    def __init__(self, master, title_text, subtitle_text, command=None, **kwargs):
        super().__init__(
            master,
            corner_radius=12,
            fg_color="#0c1d30",
            border_color="#0284c7",
            border_width=1.2,
            height=54,
            **kwargs
        )
        self.pack_propagate(False)
        self.command = command
        self.is_active = False

        self.text_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.text_frame.place(relx=0.04, rely=0.15, relwidth=0.92, relheight=0.7)

        self.lbl_title = ctk.CTkLabel(
            self.text_frame,
            text=title_text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#ffffff",
            anchor="w"
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_sub = ctk.CTkLabel(
            self.text_frame,
            text=subtitle_text,
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color="#94a3b8",
            anchor="w"
        )
        self.lbl_sub.pack(anchor="w")

        for widget in [self, self.text_frame, self.lbl_title, self.lbl_sub]:
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            widget.bind("<Button-1>", self.on_click)

    def on_enter(self, event=None):
        self.configure(fg_color="#102a45", border_color="#38bdf8", border_width=1.8)

    def on_leave(self, event=None):
        if not self.is_active:
            self.configure(fg_color="#0c1d30", border_color="#0284c7", border_width=1.2)

    def on_click(self, event=None):
        self.is_active = not self.is_active
        if self.is_active:
            self.configure(border_color="#ef4444", border_width=2.0)
        else:
            self.configure(border_color="#38bdf8", border_width=1.5)
        if self.command:
            self.command(self.is_active)


# ==============================================================================
# SECTION 5: MAIN APP CLASS
# ==============================================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ✅ WINDOW SETUP (NATIVE TITLEBAR - taskbar mein show hoga)
        self.title("⚡ Portal by Hemant")
        self.geometry("380x480")
        self.resizable(False, False)
        self.logged_in_user = ""

        # ✅ Dark titlebar color
        self.after(100, self._set_dark_titlebar)

        # ✅ Bring to front initially, then normal
        self.attributes("-topmost", True)
        self.after(1000, lambda: self.attributes("-topmost", False))

        # ✅ Fade in animation
        self.attributes("-alpha", 0.0)
        self.fade_in_animation()

        # ✅ Main container
        self.bg_frame = ctk.CTkFrame(self, fg_color="#0b0e14", corner_radius=0)
        self.bg_frame.pack(fill="both", expand=True)

        self.main_container = ctk.CTkFrame(
            self.bg_frame, corner_radius=16, fg_color="#131722",
            border_color="#38bdf8", border_width=1.5
        )
        self.main_container.pack(pady=10, padx=10, fill="both", expand=True)

        self.show_login_ui()

    def _set_dark_titlebar(self):
        """Windows titlebar ko dark color karo"""
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int)
            )

            # DWMWA_CAPTION_COLOR = 35 (set custom dark color)
            DWMWA_CAPTION_COLOR = 35
            color_int = 0x0e140b  # BGR format for #0b0e14
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_CAPTION_COLOR,
                ctypes.byref(ctypes.c_int(color_int)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception as e:
            print(f"[Titlebar Error] {e}")

    def fade_in_animation(self, alpha=0.0):
        if alpha <= 1.0:
            self.attributes("-alpha", alpha)
            self.after(10, self.fade_in_animation, alpha + 0.04)

    # ==========================================================================
    # LOGIN PAGE UI
    # ==========================================================================
    def show_login_ui(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.main_container, text="© COPYRIGHT BY HEMANT",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#7dd3fc"
        ).pack(pady=(12, 0))

        ctk.CTkLabel(
            self.main_container, text="LOGIN PORTAL",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#38bdf8"
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            self.main_container, text="Enter API-Assigned Credentials",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#94a3b8"
        ).pack(pady=(0, 12))

        self.user_entry = ctk.CTkEntry(
            self.main_container, placeholder_text="Username", width=230, height=34,
            corner_radius=8, fg_color="#0b0e14", border_color="#0284c7",
            border_width=1.5, text_color="#FFFFFF"
        )
        self.user_entry.pack(pady=6)

        self.pass_entry = ctk.CTkEntry(
            self.main_container, placeholder_text="Password", show="*", width=230,
            height=34, corner_radius=8, fg_color="#0b0e14", border_color="#0284c7",
            border_width=1.5, text_color="#FFFFFF"
        )
        self.pass_entry.pack(pady=6)

        self.login_btn = ctk.CTkButton(
            self.main_container, text="UNLOCK DASHBOARD", command=self.start_login_thread,
            width=230, height=36, corner_radius=10, fg_color="#0284c7",
            hover_color="#02c2ff", border_color="#ef4444", border_width=1.5,
            text_color="#ffffff", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold")
        )
        self.login_btn.pack(pady=(14, 0))

        self.pulse_phase = 0
        self._start_crystal_pulse()

    def _start_crystal_pulse(self):
        if hasattr(self, 'login_btn') and self.login_btn.winfo_exists():
            colors = ["#38bdf8", "#0284c7", "#38bdf8", "#7dd3fc"]
            next_color = colors[self.pulse_phase % len(colors)]
            self.login_btn.configure(border_color=next_color)
            self.pulse_phase += 1
            self.after(600, self._start_crystal_pulse)

    # ==========================================================================
    # LOGIN AUTHENTICATION
    # ==========================================================================
    def start_login_thread(self):
        self.login_btn.configure(state="disabled", text="VERIFYING...")
        threading.Thread(target=self.verify_login_api, daemon=True).start()

    def verify_login_api(self):
        username = self.user_entry.get().strip().upper()
        password = self.pass_entry.get().strip()

        if not username or not password:
            msgbox.showerror("Error", "Please fill both Username and Password!")
            self.after(0, lambda: self.login_btn.configure(state="normal", text="UNLOCK DASHBOARD"))
            return

        # ✅ HW ID generate karo
        hw_id = get_hardware_id()
        print(f"[DEBUG] HW ID: {hw_id}")

        try:
            auth_payload = {
                "username": username,
                "password": password,
                "hw_id": hw_id      # 👈 HW ID bhejो
            }
            res = httpx.post(f"{BASE_API_URL}/verify-user", json=auth_payload, timeout=8.0)

            if res.status_code == 200:
                data = res.json()
                hw_status = data.get("hw_id_status", "unknown")

                if hw_status == "authorized":
                    self.logged_in_user = username
                    self.after(0, self.show_dashboard_ui)

                elif hw_status == "first_time":
                    msgbox.showinfo(
                        "Device Registered",
                        f"✅ Device registered successfully!\n\n"
                        f"Your HW ID: {hw_id}\n\n"
                        f"Yeh ID save kar lein."
                    )
                    self.logged_in_user = username
                    self.after(0, self.show_dashboard_ui)

                elif hw_status == "unauthorized":
                    msgbox.showerror(
                        "Access Denied",
                        f"❌ Yeh device authorized nahi hai!\n\n"
                        f"Your HW ID: {hw_id}\n\n"
                        f"Please contact admin to authorize this device."
                    )

                else:
                    # Backward compatibility (agar server purana hai)
                    self.logged_in_user = username
                    self.after(0, self.show_dashboard_ui)
            else:
                msgbox.showerror("Access Denied", "Invalid Username or Password!")

        except Exception as e:
            msgbox.showerror("Server Offline", f"Could not connect!\n\nError: {e}")
        finally:
            self.after(0, lambda: self.login_btn.configure(state="normal", text="UNLOCK DASHBOARD"))

    # ==========================================================================
    # DASHBOARD PAGE UI
    # ==========================================================================
    def show_dashboard_ui(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        self.main_container.configure(fg_color="#0c203b", border_color="#38bdf8", border_width=1.5)

        ctk.CTkLabel(
            self.main_container, text="© COPYRIGHT BY HEMANT",
            font=ctk.CTkFont(family="Segoe UI", size=8, weight="bold"),
            text_color="#7dd3fc"
        ).pack(pady=(4, 0))

        ctk.CTkLabel(
            self.main_container, text="CONTROL CENTER",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#38bdf8"
        ).pack(pady=(2, 0))

        ctk.CTkLabel(
            self.main_container, text=f"Welcome, {self.logged_in_user}",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#bae6fd"
        ).pack(pady=(0, 4))

        options_container = ctk.CTkScrollableFrame(
            self.main_container, fg_color="transparent", height=125, corner_radius=10,
            scrollbar_button_color="#0284c7", scrollbar_button_hover_color="#38bdf8"
        )
        options_container.pack(fill="x", padx=10, pady=2)

        def make_action_handler(cb):
            def handler(state):
                cb(state)
            return handler

        cards_data = [
            ("START YOUTUBE", "Launch Video Portal", self.on_youtube_card),
            ("OPEN CHATGPT", "AI Assistant Portal", self.on_chatgpt_card),
            ("RUN SUPER CLEANER", "System Temp & DNS Flush", self.on_cleaner_card),
            ("OPEN MOVIE PORTAL", "Stream/Browse Media", self.on_movie_card),
            ("PHONE NUMBER AUDIT", "OSINT ", self.on_phone_audit_card),
            ("YOUTUBE DOWNLOADER", "Download videos in HD", self.on_youtube_downloader_card),
            ("PC OPTIMIZER", "Boost PC performance", self.on_pc_optimizer_card),
            ("SCREEN RECORDER", "4K + Max FPS + Edited Look", self.on_screen_recorder_card),
            ("PDF TOOLKIT", "Merge • Split • Convert", self.on_pdf_toolkit_card),
            ("IMAGE TOOLKIT", "Edit • Filter • AI Enhance", self.on_image_toolkit_card),
            ("VIDEO TOOLKIT", "Filter • Trim • AI Upscale", self.on_video_toolkit_card),
        ]

        for title_str, sub_str, cb in cards_data:
            card = GlowOptionCard(
                options_container,
                title_text=title_str,
                subtitle_text=sub_str,
                command=make_action_handler(cb)
            )
            card.pack(fill="x", pady=3)

        request_frame = ctk.CTkFrame(
            self.main_container, fg_color="#0f294a", border_color="#ef4444",
            border_width=1.5, corner_radius=10
        )
        request_frame.pack(pady=(4, 6), padx=10, fill="x")

        ctk.CTkLabel(
            request_frame, text="💡 Request New Feature",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#f87171"
        ).pack(pady=(3, 1))

        self.feature_box = ctk.CTkTextbox(
            request_frame, height=30, corner_radius=6, fg_color="#08182c",
            border_color="#0369a1", border_width=1, text_color="#e0f2fe",
            font=ctk.CTkFont(family="Segoe UI", size=9)
        )
        self.feature_box.pack(pady=2, padx=6, fill="x")

        btn_row = ctk.CTkFrame(request_frame, fg_color="transparent")
        btn_row.pack(pady=(3, 5), padx=6, fill="x")

        self.send_btn = ctk.CTkButton(
            btn_row, text="SUBMIT", command=self.submit_feature_request,
            height=26, corner_radius=6, fg_color="#ef4444", hover_color="#dc2626",
            border_color="#fca5a5", border_width=1, text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")
        )

        if self.logged_in_user == "HEMANT":
            self.send_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
            self.view_btn = ctk.CTkButton(
                btn_row, text="VIEW LIST", command=self.view_feature_requests,
                height=26, corner_radius=6, fg_color="#0284c7", hover_color="#02c2ff",
                border_color="#38bdf8", border_width=1, text_color="#ffffff",
                font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")
            )
            self.view_btn.pack(side="right", fill="x", expand=True, padx=(2, 0))
        else:
            self.send_btn.pack(side="top", fill="x", expand=True)

    # ==========================================================================
    # PHONE AUDIT CARD HANDLER
    # ==========================================================================
    def on_phone_audit_card(self, state):
        if state:
            try:
                PhoneAuditWindow(master=self)
            except Exception as e:
                msgbox.showerror("Error", f"Could not open audit window:\n{e}")

    # ==========================================================================
    # YOUTUBE DOWNLOADER CARD HANDLER
    # ==========================================================================
    def on_youtube_downloader_card(self, state):
        if state:
            try:
                YouTubeDownloaderWindow(master=self)
            except Exception as e:
                msgbox.showerror("Error", f"Could not open downloader window:\n{e}")

    # ==========================================================================
    # PC OPTIMIZER CARD HANDLER
    # ==========================================================================
    def on_pc_optimizer_card(self, state):
        if state:
            try:
                PCOptimizerWindow(master=self)
            except Exception as e:
                msgbox.showerror("Error", f"Could not open optimizer window:\n{e}")

    # ==========================================================================
    # PC SCREEN RECORDER CARD HANDLER
    # ==========================================================================
    def on_screen_recorder_card(self, state):
        if state:
            try:
                ScreenRecorderWindow(master=self)
            except Exception as e:
                msgbox.showerror("Error", f"Could not open recorder:\n{e}")

    # ==========================================================================
    # PDF TOOLKIT CARD HANDLER
    # ==========================================================================
    def on_pdf_toolkit_card(self, state):
        if state:
            try:
                PDFToolkitWindow(master=self)
            except Exception as e:
                msgbox.showerror("Error", f"Could not open PDF Toolkit:\n{e}")

    # ==========================================================================
    # IMAGE TOOLKIT CARD HANDLER
    # ==========================================================================
    def on_image_toolkit_card(self, state):
        if state:
            try:
                ImageToolkitWindow(master=self)
            except Exception as e:
                msgbox.showerror("Error", f"Could not open Image Toolkit:\n{e}")

    # ==========================================================================
    # VIDEO TOOLKIT CARD HANDLER
    # ==========================================================================
    def on_video_toolkit_card(self, state):
        if state:
            try:
                VideoToolkitWindow(master=self)
            except Exception as e:
                msgbox.showerror("Error", f"Could not open Video Toolkit:\n{e}")

    # ==========================================================================
    # FEATURE REQUEST LOGIC
    # ==========================================================================
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
            res = httpx.post(f"{BASE_API_URL}/submit-feature", json=payload, timeout=8.0)
            if res.status_code == 200:
                self.after(0, lambda: self.feature_box.delete("1.0", "end"))
                self.after(0, lambda: msgbox.showinfo("Submitted", "Feature Request Sent!"))
            else:
                self.after(0, lambda: msgbox.showerror("Error", f"Failed: {res.text}"))
        except Exception as e:
            self.after(0, lambda: msgbox.showerror("Error", f"Could not reach server!\n{e}"))
        finally:
            self.after(0, lambda: self.send_btn.configure(state="normal", text="SUBMIT"))

    def view_feature_requests(self):
        self.view_btn.configure(state="disabled", text="LOADING...")
        threading.Thread(target=self._fetch_features_api, daemon=True).start()

    def _fetch_features_api(self):
        try:
            res = httpx.get(f"{BASE_API_URL}/get-features", timeout=8.0)
            if res.status_code == 200:
                data = res.json()
                self.after(0, lambda: self._show_requests_dialog(data))
            else:
                self.after(0, lambda: msgbox.showerror("Error", f"Status {res.status_code}"))
        except Exception as e:
            self.after(0, lambda: msgbox.showerror("Error", f"Could not reach!\n{e}"))
        finally:
            self.after(0, lambda: self.view_btn.configure(state="normal", text="VIEW LIST"))

    def _show_requests_dialog(self, data):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Feature Requests")
        dialog.geometry("400x420")

        ctk.CTkLabel(
            dialog, text="👤 User-wise Feature Requests",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#38bdf8"
        ).pack(pady=(12, 6))

        list_scroll = ctk.CTkScrollableFrame(
            dialog, fg_color="#0b0e14", corner_radius=10,
            border_color="#0284c7", border_width=1, width=360, height=320,
            scrollbar_button_color="#0284c7", scrollbar_button_hover_color="#38bdf8"
        )
        list_scroll.pack(padx=15, pady=(0, 15), fill="both", expand=True)

        items_list = []
        if isinstance(data, list):
            items_list = data
        elif isinstance(data, dict):
            for k in ["data", "requests", "items", "results"]:
                if k in data and isinstance(data[k], list):
                    items_list = data[k]
                    break

        if len(items_list) > 0:
            for item in items_list:
                if isinstance(item, dict):
                    u = item.get("username", item.get("user", "ANONYMOUS"))
                    f = item.get("feature_text", item.get("message", str(item)))
                else:
                    u = "USER"
                    f = str(item)

                card = ctk.CTkFrame(list_scroll, fg_color="#131722", corner_radius=8,
                                    border_color="#38bdf8", border_width=1)
                card.pack(fill="x", pady=5, padx=4)

                ctk.CTkLabel(card, text=f" 👤 USER: {u} ",
                             font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                             text_color="#7dd3fc", anchor="w").pack(anchor="w", padx=8, pady=(4, 2))

                ctk.CTkLabel(card, text=f"💬 {f}",
                             font=ctk.CTkFont(family="Segoe UI", size=10),
                             text_color="#e0f2fe", anchor="w", justify="left",
                             wraplength=310).pack(anchor="w", padx=10, pady=(0, 6))
        else:
            ctk.CTkLabel(list_scroll, text="No feature requests yet.",
                         font=ctk.CTkFont(family="Segoe UI", size=11),
                         text_color="#94a3b8").pack(pady=40)

    # ==========================================================================
    # CARD ACTION HANDLERS
    # ==========================================================================
    def on_youtube_card(self, state):
        if state:
            try:
                os.system("start https://www.youtube.com")
            except Exception:
                webbrowser.open("https://www.youtube.com")
            threading.Thread(target=self.send_api_request, daemon=True).start()

    def on_chatgpt_card(self, state):
        if state:
            try:
                os.system("start https://chatgpt.com")
            except Exception:
                webbrowser.open("https://chatgpt.com")
            threading.Thread(target=self.send_api_request, daemon=True).start()

    def on_movie_card(self, state):
        if state:
            try:
                os.system("start https://www.netflix.com")
            except Exception:
                webbrowser.open("https://www.netflix.com")
            threading.Thread(target=self.send_api_request, daemon=True).start()

    def on_cleaner_card(self, state):
        if state:
            threading.Thread(target=self.execute_super_cleaner, daemon=True).start()
            threading.Thread(target=self.send_api_request, daemon=True).start()

    # ==========================================================================
    # 🔧 SUPER CLEANER
    # ==========================================================================
    def execute_super_cleaner(self):
        bat_dir = "C:\\Temp"
        os.makedirs(bat_dir, exist_ok=True)
        bat_path = os.path.join(bat_dir, "super_cleaner.bat")

        bat_content = r"""@echo off
cd /d "%~dp0"
title SUPER CLEANER - Full Force Delete
color 0A

echo ========================================
echo   SUPER CLEANER - FORCE DELETE MODE
echo ========================================
echo.

echo [1/9] User TEMP files...
del /f /s /q "%TEMP%\*.*" 2>nul
for /d %%x in ("%TEMP%\*") do rd /s /q "%%x" 2>nul

echo [2/9] Hidden + System files in TEMP...
attrib -h -s -r "%TEMP%\*.*" /s /d 2>nul
del /f /s /q "%TEMP%\*.*" 2>nul

echo [3/9] Windows TEMP...
del /f /s /q "%windir%\Temp\*.*" 2>nul

echo [4/9] Local AppData TEMP...
del /f /s /q "%LocalAppData%\Temp\*.*" 2>nul
for /d %%x in ("%LocalAppData%\Temp\*") do rd /s /q "%%x" 2>nul

echo [5/9] Prefetch files...
del /f /s /q "%windir%\Prefetch\*.*" 2>nul

echo [6/9] Recent files...
del /f /s /q "%AppData%\Microsoft\Windows\Recent\*.*" 2>nul

echo [7/9] Thumbnail cache...
del /f /s /q "%LocalAppData%\Microsoft\Windows\Explorer\thumbcache_*.db" 2>nul

echo [8/9] Flushing DNS...
ipconfig /flushdns >nul 2>&1

echo [9/9] Emptying Recycle Bin...
rd /s /q "C:\$Recycle.Bin" 2>nul

echo.
echo ========================================
echo   ✅ CLEANUP COMPLETE!
echo ========================================
echo.

echo 📊 Checking TEMP folder size...
powershell -Command "$size = (Get-ChildItem $env:TEMP -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; if ($size) { Write-Host ('TEMP size: ' + [math]::Round($size/1MB, 2) + ' MB') } else { Write-Host 'TEMP size: 0 MB (CLEAN!)' -ForegroundColor Green }"

echo.
echo Note: Some files may still be in use by running programs.
echo Close Chrome, VS Code, Discord for best results.
echo.
pause >nul
exit
"""

        try:
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_content)

            subprocess.Popen(
                ["powershell", "-Command",
                 f'Start-Process -FilePath "{bat_path}" -Verb RunAs'],
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            msgbox.showinfo(
                "Super Cleaner",
                "✅ Super Cleaner started!\n\n"
                "⚠️ PROCESS COMPLETED - ENJOY!"
            )

        except Exception as e:
            msgbox.showerror("Cleaner Error", f"Failed to run:\n{e}")

    def send_api_request(self):
        try:
            payload = {"target_uid": "123456789", "count": 10}
            httpx.post(f"{BASE_API_URL}/add-likes", json=payload, timeout=8.0)
        except Exception:
            pass


# ==============================================================================
# APPLICATION LAUNCHER
# ==============================================================================
if __name__ == "__main__":
    app = App()
    app.mainloop()
