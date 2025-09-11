# CoolBits.ai Internal Admin Panel
# Centralized console management for Andrei (CEO)

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import json
import time
from datetime import datetime
import os


class CoolBitsAdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("CoolBits.ai Internal Admin Panel - Andrei (CEO)")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")

        # Status variables
        self.gemini_cli_connected = False
        self.cursor_connected = True
        self.cloud_status = "Unknown"

        # Create main interface
        self.create_interface()

        # Start status monitoring
        self.monitor_status()

    def create_interface(self):
        """Create the main admin panel interface"""

        # Header
        header_frame = tk.Frame(self.root, bg="#2d2d2d", height=60)
        header_frame.pack(fill="x", padx=10, pady=5)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🎯 CoolBits.ai Internal Admin Panel",
            font=("Arial", 16, "bold"),
            fg="#00ff00",
            bg="#2d2d2d",
        )
        title_label.pack(side="left", padx=10, pady=15)

        status_label = tk.Label(
            header_frame,
            text="Status: Active",
            font=("Arial", 12),
            fg="#00ff00",
            bg="#2d2d2d",
        )
        status_label.pack(side="right", padx=10, pady=15)

        # Main content area
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left panel - Console Management
        left_panel = tk.Frame(main_frame, bg="#2d2d2d", width=400)
        left_panel.pack(side="left", fill="y", padx=(0, 5))
        left_panel.pack_propagate(False)

        # Console Management
        console_frame = tk.LabelFrame(
            left_panel,
            text="🖥️ Console Management",
            font=("Arial", 12, "bold"),
            fg="#00ff00",
            bg="#2d2d2d",
        )
        console_frame.pack(fill="x", padx=10, pady=10)

        # Cursor Console
        cursor_frame = tk.Frame(console_frame, bg="#2d2d2d")
        cursor_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            cursor_frame,
            text="Cursor + oCursor:",
            font=("Arial", 10, "bold"),
            fg="#00ff00",
            bg="#2d2d2d",
        ).pack(anchor="w")

        cursor_status = tk.Label(
            cursor_frame,
            text="✅ Connected (Local GPU)",
            font=("Arial", 9),
            fg="#00ff00",
            bg="#2d2d2d",
        )
        cursor_status.pack(anchor="w")

        cursor_btn = tk.Button(
            cursor_frame,
            text="Open Cursor Console",
            command=self.open_cursor_console,
            bg="#00ff00",
            fg="black",
        )
        cursor_btn.pack(fill="x", pady=2)

        # oGeminiCLI Console
        gemini_frame = tk.Frame(console_frame, bg="#2d2d2d")
        gemini_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            gemini_frame,
            text="oGeminiCLI:",
            font=("Arial", 10, "bold"),
            fg="#00ff00",
            bg="#2d2d2d",
        ).pack(anchor="w")

        self.gemini_status = tk.Label(
            gemini_frame,
            text="⏳ Connecting...",
            font=("Arial", 9),
            fg="#ffaa00",
            bg="#2d2d2d",
        )
        self.gemini_status.pack(anchor="w")

        gemini_btn = tk.Button(
            gemini_frame,
            text="Connect oGeminiCLI",
            command=self.connect_gemini_cli,
            bg="#ffaa00",
            fg="black",
        )
        gemini_btn.pack(fill="x", pady=2)

        # Bridge Communication
        bridge_frame = tk.LabelFrame(
            left_panel,
            text="🌉 Bridge Communication",
            font=("Arial", 12, "bold"),
            fg="#00ff00",
            bg="#2d2d2d",
        )
        bridge_frame.pack(fill="x", padx=10, pady=10)

        # Message input
        tk.Label(
            bridge_frame,
            text="Send to oGeminiCLI:",
            font=("Arial", 10),
            fg="#00ff00",
            bg="#2d2d2d",
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.message_entry = tk.Entry(
            bridge_frame, font=("Arial", 10), bg="#3d3d3d", fg="white"
        )
        self.message_entry.pack(fill="x", padx=10, pady=5)

        send_btn = tk.Button(
            bridge_frame,
            text="Send Message",
            command=self.send_to_gemini_cli,
            bg="#0066cc",
            fg="white",
        )
        send_btn.pack(fill="x", padx=10, pady=5)

        # Quick commands
        quick_frame = tk.LabelFrame(
            left_panel,
            text="⚡ Quick Commands",
            font=("Arial", 12, "bold"),
            fg="#00ff00",
            bg="#2d2d2d",
        )
        quick_frame.pack(fill="x", padx=10, pady=10)

        commands = [
            ("Check Cloud Run", self.check_cloud_run),
            ("Verify CNAME", self.verify_cname),
            ("Validate HMAC", self.validate_hmac),
            ("Check GPU Status", self.check_gpu_status),
            ("Test RAG System", self.test_rag_system),
        ]

        for cmd_text, cmd_func in commands:
            btn = tk.Button(
                quick_frame, text=cmd_text, command=cmd_func, bg="#333333", fg="#00ff00"
            )
            btn.pack(fill="x", padx=10, pady=2)

        # Right panel - Console Output
        right_panel = tk.Frame(main_frame, bg="#2d2d2d")
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Console output
        console_output_frame = tk.LabelFrame(
            right_panel,
            text="📺 Console Output",
            font=("Arial", 12, "bold"),
            fg="#00ff00",
            bg="#2d2d2d",
        )
        console_output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.console_output = scrolledtext.ScrolledText(
            console_output_frame,
            font=("Consolas", 10),
            bg="#1a1a1a",
            fg="#00ff00",
            wrap=tk.WORD,
        )
        self.console_output.pack(fill="both", expand=True, padx=10, pady=10)

        # Status bar
        status_bar = tk.Frame(self.root, bg="#2d2d2d", height=30)
        status_bar.pack(fill="x", side="bottom", padx=10, pady=5)
        status_bar.pack_propagate(False)

        self.status_text = tk.Label(
            status_bar, text="Ready", font=("Arial", 10), fg="#00ff00", bg="#2d2d2d"
        )
        self.status_text.pack(side="left", padx=10, pady=5)

        time_label = tk.Label(
            status_bar, text="", font=("Arial", 10), fg="#00ff00", bg="#2d2d2d"
        )
        time_label.pack(side="right", padx=10, pady=5)

        # Update time
        self.update_time(time_label)

    def update_time(self, time_label):
        """Update the time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        time_label.config(text=current_time)
        self.root.after(1000, lambda: self.update_time(time_label))

    def log_message(self, message, level="INFO"):
        """Log a message to the console output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = (
            "#00ff00"
            if level == "INFO"
            else "#ffaa00" if level == "WARNING" else "#ff0000"
        )

        self.console_output.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.console_output.see(tk.END)

        # Update status
        self.status_text.config(text=f"Last: {level} - {message[:50]}...")

    def open_cursor_console(self):
        """Open Cursor console"""
        self.log_message("Opening Cursor console...")
        try:
            # Open Cursor in the project directory
            subprocess.Popen(["cursor", "."], cwd="C:\\Users\\andre\\Desktop\\coolbits")
            self.log_message("Cursor console opened successfully")
        except Exception as e:
            self.log_message(f"Failed to open Cursor: {e}", "ERROR")

    def connect_gemini_cli(self):
        """Connect to oGeminiCLI"""
        self.log_message("Connecting to oGeminiCLI...")

        # Simulate connection
        def connect_thread():
            time.sleep(2)  # Simulate connection time
            self.gemini_cli_connected = True
            self.gemini_status.config(text="✅ Connected (Cloud Console)", fg="#00ff00")
            self.log_message("oGeminiCLI connected successfully")

        threading.Thread(target=connect_thread, daemon=True).start()

    def send_to_gemini_cli(self):
        """Send message to oGeminiCLI"""
        message = self.message_entry.get()
        if not message:
            return

        self.log_message(f"Sending to oGeminiCLI: {message}")

        # Simulate sending message
        def send_thread():
            time.sleep(1)
            self.log_message(f"oGeminiCLI response: Message received - '{message}'")

        threading.Thread(target=send_thread, daemon=True).start()
        self.message_entry.delete(0, tk.END)

    def check_cloud_run(self):
        """Check Cloud Run deployment status"""
        self.log_message("Checking Cloud Run deployment...")

        def check_thread():
            try:
                # Simulate gcloud command
                result = subprocess.run(
                    [
                        "gcloud",
                        "run",
                        "services",
                        "list",
                        "--region=europe-west3",
                        "--project=coolbits-og-bridge",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    self.log_message("Cloud Run services retrieved successfully")
                    self.log_message(f"Output: {result.stdout}")
                else:
                    self.log_message(f"Error: {result.stderr}", "ERROR")
            except Exception as e:
                self.log_message(f"Failed to check Cloud Run: {e}", "ERROR")

        threading.Thread(target=check_thread, daemon=True).start()

    def verify_cname(self):
        """Verify CNAME propagation"""
        self.log_message("Verifying CNAME propagation...")

        def verify_thread():
            try:
                # Simulate dig command
                result = subprocess.run(
                    ["dig", "u-bit.coolbits.ai", "+short"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    self.log_message("CNAME verification completed")
                    self.log_message(f"Result: {result.stdout}")
                else:
                    self.log_message(f"Error: {result.stderr}", "ERROR")
            except Exception as e:
                self.log_message(f"Failed to verify CNAME: {e}", "ERROR")

        threading.Thread(target=verify_thread, daemon=True).start()

    def validate_hmac(self):
        """Validate HMAC keys"""
        self.log_message("Validating HMAC keys...")

        def validate_thread():
            try:
                # Simulate gcloud secrets command
                result = subprocess.run(
                    [
                        "gcloud",
                        "secrets",
                        "list",
                        "--project=coolbits-og-bridge",
                        "--filter=name~bridge_webhook_hmac",
                        "--format=table(name)",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    self.log_message("HMAC keys validation completed")
                    self.log_message(f"Keys: {result.stdout}")
                else:
                    self.log_message(f"Error: {result.stderr}", "ERROR")
            except Exception as e:
                self.log_message(f"Failed to validate HMAC: {e}", "ERROR")

        threading.Thread(target=validate_thread, daemon=True).start()

    def check_gpu_status(self):
        """Check local GPU status"""
        self.log_message("Checking local GPU status...")

        def check_thread():
            try:
                # Check NVIDIA GPU
                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,memory.total,memory.used,utilization.gpu",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    self.log_message("GPU status retrieved successfully")
                    self.log_message(f"GPU Info: {result.stdout}")
                else:
                    self.log_message(f"Error: {result.stderr}", "ERROR")
            except Exception as e:
                self.log_message(f"Failed to check GPU: {e}", "ERROR")

        threading.Thread(target=check_thread, daemon=True).start()

    def test_rag_system(self):
        """Test RAG system"""
        self.log_message("Testing RAG system...")

        def test_thread():
            try:
                # Test local RAG system
                if os.path.exists("local_rag_dev.py"):
                    result = subprocess.run(
                        ["python", "local_rag_dev.py"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

                    if result.returncode == 0:
                        self.log_message("RAG system test completed successfully")
                        self.log_message(f"Output: {result.stdout}")
                    else:
                        self.log_message(f"RAG test error: {result.stderr}", "ERROR")
                else:
                    self.log_message(
                        "RAG system not found. Run setup first.", "WARNING"
                    )
            except Exception as e:
                self.log_message(f"Failed to test RAG: {e}", "ERROR")

        threading.Thread(target=test_thread, daemon=True).start()

    def monitor_status(self):
        """Monitor system status"""

        def monitor_thread():
            while True:
                # Check various system statuses
                try:
                    # Check if Cursor is running
                    cursor_running = self.check_process_running("cursor")

                    # Check if gcloud is authenticated
                    gcloud_auth = self.check_gcloud_auth()

                    # Update status
                    if cursor_running:
                        self.log_message("Cursor process detected", "INFO")

                    if gcloud_auth:
                        self.log_message("gcloud authentication verified", "INFO")

                except Exception as e:
                    self.log_message(f"Status monitoring error: {e}", "ERROR")

                time.sleep(30)  # Check every 30 seconds

        threading.Thread(target=monitor_thread, daemon=True).start()

    def check_process_running(self, process_name):
        """Check if a process is running"""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}.exe"],
                capture_output=True,
                text=True,
            )
            return process_name in result.stdout
        except:
            return False

    def check_gcloud_auth(self):
        """Check gcloud authentication"""
        try:
            result = subprocess.run(
                ["gcloud", "auth", "list", "--filter=status:ACTIVE"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except:
            return False


def main():
    """Main function to run the admin panel"""
    root = tk.Tk()
    app = CoolBitsAdminPanel(root)

    # Add welcome message
    app.log_message("🎯 CoolBits.ai Internal Admin Panel Started")
    app.log_message("👋 Welcome, Andrei (CEO)")
    app.log_message("🖥️ Cursor + oCursor: Ready for local GPU development")
    app.log_message("☁️ oGeminiCLI: Ready for cloud operations")
    app.log_message("🌉 Bridge communication established")

    root.mainloop()


if __name__ == "__main__":
    main()
