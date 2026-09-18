"""
📱 PHONE NUMBER AUDIT WINDOW
Backend API se data fetch karta hai
"""

import customtkinter as ctk
import tkinter.messagebox as msgbox
from tkinter import filedialog
import httpx
import threading
from datetime import datetime

BASE_API_URL = "https://fastapi-automation-backend.onrender.com"


class PhoneAuditWindow(ctk.CTkToplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title("📱 Phone Number Audit Tool")
        self.geometry("850x700")
        self.resizable(True, True)
        self.attributes("-topmost", True)
        
        self.bg_dark = "#0b0e14"
        self.bg_card = "#131722"
        self.accent_blue = "#38bdf8"
        self.accent_dark_blue = "#0284c7"
        self.text_light = "#e0f2fe"
        
        self.configure(fg_color=self.bg_dark)
        self.report_text = ""
        
        self.setup_ui()
        
        self.attributes("-alpha", 0.0)
        self.fade_in()
    
    def fade_in(self, alpha=0.0):
        if alpha <= 1.0:
            self.attributes("-alpha", alpha)
            self.after(15, self.fade_in, alpha + 0.08)
    
    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color=self.bg_dark, corner_radius=0)
        header.pack(fill="x", pady=(15, 5))
        
        ctk.CTkLabel(
            header, text="© COPYRIGHT BY HEMANT",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#7dd3fc"
        ).pack()
        
        ctk.CTkLabel(
            header, text="📱 PHONE NUMBER AUDIT",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=self.accent_blue
        ).pack(pady=(5, 0))
        
        ctk.CTkLabel(
            header, text="Sirf apne number pe use karo",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#f9e2af"
        ).pack(pady=(0, 5))
        
        input_frame = ctk.CTkFrame(
            self, fg_color=self.bg_card, corner_radius=12,
            border_color=self.accent_dark_blue, border_width=1.2
        )
        input_frame.pack(fill="x", padx=20, pady=10)
        
        inner = ctk.CTkFrame(input_frame, fg_color="transparent")
        inner.pack(padx=15, pady=12, fill="x")
        
        ctk.CTkLabel(
            inner, text="Enter Number:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.text_light
        ).pack(side="left", padx=(0, 10))
        
        self.number_entry = ctk.CTkEntry(
            inner, width=200, height=34, corner_radius=8,
            fg_color="#0b0e14", border_color=self.accent_dark_blue,
            border_width=1.5, text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        )
        self.number_entry.pack(side="left", padx=5)
        self.number_entry.insert(0, "+91")
        self.number_entry.bind("<Return>", lambda e: self.start_audit())
        
        self.audit_btn = ctk.CTkButton(
            inner, text="🔍  AUDIT", width=100, height=34, corner_radius=8,
            fg_color=self.accent_dark_blue, hover_color="#02c2ff",
            border_color=self.accent_blue, border_width=1.2,
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.start_audit
        )
        self.audit_btn.pack(side="left", padx=5)
        
        self.save_btn = ctk.CTkButton(
            inner, text="💾 SAVE", width=90, height=34, corner_radius=8,
            fg_color="#16a34a", hover_color="#22c55e",
            border_color="#4ade80", border_width=1.2,
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.save_report, state="disabled"
        )
        self.save_btn.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(
            self, text="✅ Ready",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#a6e3a1", anchor="w"
        )
        self.status_label.pack(fill="x", padx=25, pady=(0, 5))
        
        output_frame = ctk.CTkFrame(
            self, fg_color=self.bg_card, corner_radius=12,
            border_color=self.accent_dark_blue, border_width=1.2
        )
        output_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        
        ctk.CTkLabel(
            output_frame, text="📄 REPORT:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.accent_blue, anchor="w"
        ).pack(fill="x", padx=15, pady=(10, 5))
        
        self.output = ctk.CTkTextbox(
            output_frame, fg_color="#0b0e14", text_color=self.text_light,
            border_color=self.accent_dark_blue, border_width=1,
            corner_radius=8, font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.output.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.output.configure(state="disabled")
    
    def start_audit(self):
        number = self.number_entry.get().strip()
        
        if not number or not number.startswith("+"):
            msgbox.showerror("Invalid", "Number + se start hona chahiye!")
            return
        
        self.audit_btn.configure(state="disabled", text="⏳ WAIT...")
        self.status_label.configure(text="⏳ Fetching from backend...", text_color="#f9e2af")
        self.clear_output()
        
        threading.Thread(target=self.run_audit, args=(number,), daemon=True).start()
    
    def run_audit(self, number):
        try:
            res = httpx.post(
                f"{BASE_API_URL}/phone-audit",
                json={"number": number, "username": "HEMANT"},
                timeout=30.0
            )
            
            if res.status_code != 200:
                raise Exception(f"Backend error: {res.status_code}")
            
            data = res.json()
            report = self.format_report(data, number)
            self.report_text = report
            
            self.after(0, lambda: self.append_output(report))
            self.after(0, lambda: self.status_label.configure(
                text="✅ Audit Complete!", text_color="#a6e3a1"))
            self.after(0, lambda: self.save_btn.configure(state="normal"))
        
        except Exception as e:
            err = f"\n❌ ERROR: {str(e)}\n"
            self.after(0, lambda: self.append_output(err))
            self.after(0, lambda: self.status_label.configure(
                text=f"❌ Error", text_color="#f38ba8"))
        finally:
            self.after(0, lambda: self.audit_btn.configure(
                state="normal", text="🔍  AUDIT"))
    
    def format_report(self, data, number):
        r = "=" * 60 + "\n"
        r += "📱 PHONE NUMBER AUDIT REPORT\n"
        r += "=" * 60 + "\n"
        r += f"Generated: {data.get('timestamp', '')}\n"
        r += f"Number: {number}\n"
        r += "=" * 60 + "\n\n"
        
        v = data.get("validation", {})
        r += "📋 BASIC INFORMATION\n" + "-" * 60 + "\n"
        r += f"  ✓ Valid:           {'✅ Yes' if v.get('valid') else '❌ No'}\n"
        r += f"  ✓ Country:         {v.get('country')}\n"
        r += f"  ✓ Carrier:         {v.get('carrier')}\n"
        r += f"  ✓ Timezone:        {v.get('timezone')}\n"
        r += f"  ✓ E164 Format:     {v.get('e164')}\n"
        r += f"  ✓ National:        {v.get('national')}\n"
        r += f"  ✓ Line Type:       {v.get('line_type')}\n\n"
        
        r += "📱 SOCIAL MEDIA\n" + "-" * 60 + "\n"
        for k, url in data.get("social", {}).items():
            r += f"  • {k}: {url}\n"
        r += "\n"
        
        r += "🚨 DATA BREACH\n" + "-" * 60 + "\n"
        for k, url in data.get("breach", {}).items():
            r += f"  • {k}: {url}\n"
        r += "\n"
        
        r += "🔎 GOOGLE DORKS\n" + "-" * 60 + "\n"
        for d in data.get("dorks", []):
            r += f"  • {d['name']}:\n    {d['url']}\n"
        r += "\n"
        
        r += "🛡️  SPAM REPORTS\n" + "-" * 60 + "\n"
        for k, url in data.get("spam", {}).items():
            r += f"  • {k}: {url}\n"
        r += "\n"
        
        r += "📊 PRIVACY TIPS\n" + "-" * 60 + "\n"
        for i, tip in enumerate(data.get("privacy_tips", []), 1):
            r += f"  {i}. {tip}\n"
        r += "\n"
        
        r += "=" * 60 + "\n"
        r += "⚠️  LEGAL REMINDER\n" + "-" * 60 + "\n"
        r += f"  {data.get('legal_warning', '')}\n"
        r += "=" * 60 + "\n"
        return r
    
    def append_output(self, text):
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")
    
    def clear_output(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
    
    def save_report(self):
        if not self.report_text:
            msgbox.showwarning("No Report", "Pehle audit chalao!")
            return
        clean = self.number_entry.get().replace("+", "").replace(" ", "")
        default_name = f"audit_{clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.report_text)
            msgbox.showinfo("Saved!", f"Report saved:\n{filepath}")
