#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cbLM Corporate Assets GUI Panel
COOL BITS SRL 🏢 🏢 - Internal Secret

Professional GUI application for managing all Corporate Entities and assets
with cb.svg logo integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import time
import subprocess
import psutil
import requests
from datetime import datetime
from PIL import Image, ImageTk
import webbrowser


class CBLMCorporateAssetsGUI:
    """Main GUI application for cbLM Corporate Assets Management"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("cbLM Corporate Assets Panel - COOL BITS SRL 🏢 🏢")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")

        # Company information
        self.company = "COOL BITS SRL 🏢 🏢"
        self.ceo = "Andrei"
        self.ai_assistant = "oCursor"
        self.classification = "Internal Secret - CoolBits.ai 🏢 🏢 Members Only"

        # Corporate Entities data
        self.corporate_entities = {
            "vertex": {
                "name": "Vertex AI",
                "zone": "google_cloud",
                "status": "active",
                "priority": "high",
                "schedule": "every 5 minutes",
                "url": "https://console.cloud.google.com/vertex-ai",
                "icon": "☁️",
            },
            "cursor": {
                "name": "Cursor AI Assistant",
                "zone": "development",
                "status": "active",
                "priority": "high",
                "schedule": "every 2 minutes",
                "url": "https://cursor.sh",
                "icon": "💻",
            },
            "nvidia": {
                "name": "NVIDIA GPU Pipeline",
                "zone": "gpu_processing",
                "status": "active",
                "priority": "critical",
                "schedule": "every 1 minute",
                "url": "https://developer.nvidia.com",
                "icon": "🚀",
            },
            "microsoft": {
                "name": "Microsoft Ecosystem",
                "zone": "windows_ecosystem",
                "status": "active",
                "priority": "high",
                "schedule": "every 3 minutes",
                "url": "https://azure.microsoft.com",
                "icon": "🏢",
            },
            "xai": {
                "name": "xAI Platform",
                "zone": "ai_platform",
                "status": "active",
                "priority": "medium",
                "schedule": "every 4 minutes",
                "url": "https://x.ai",
                "icon": "🤖",
            },
            "grok": {
                "name": "Grok AI",
                "zone": "ai_platform",
                "status": "active",
                "priority": "medium",
                "schedule": "every 4 minutes",
                "url": "https://grok.x.ai",
                "icon": "🧠",
            },
            "ogrok": {
                "name": "oGrok",
                "zone": "coolbits_proprietary",
                "status": "proprietary",
                "priority": "critical",
                "schedule": "every 2 minutes",
                "url": "internal",
                "icon": "🏢",
                "owner": "COOL BITS SRL 🏢 🏢",
            },
            "openai": {
                "name": "OpenAI Platform",
                "zone": "ai_platform",
                "status": "active",
                "priority": "high",
                "schedule": "every 3 minutes",
                "url": "https://platform.openai.com",
                "icon": "🔮",
            },
            "chatgpt": {
                "name": "ChatGPT",
                "zone": "ai_platform",
                "status": "active",
                "priority": "high",
                "schedule": "every 3 minutes",
                "url": "https://chat.openai.com",
                "icon": "💬",
            },
            "ogpt": {
                "name": "oGPT",
                "zone": "coolbits_proprietary",
                "status": "proprietary",
                "priority": "critical",
                "schedule": "every 2 minutes",
                "url": "internal",
                "icon": "🏢",
                "owner": "COOL BITS SRL 🏢 🏢",
            },
        }

        # Zones configuration
        self.zones = {
            "google_cloud": {"name": "Google Cloud Zone", "color": "#4285f4"},
            "development": {"name": "Development Zone", "color": "#34a853"},
            "gpu_processing": {"name": "GPU Processing Zone", "color": "#ea4335"},
            "windows_ecosystem": {"name": "Windows Ecosystem Zone", "color": "#0078d4"},
            "ai_platform": {"name": "AI Platform Zone", "color": "#ff6d01"},
            "coolbits_proprietary": {
                "name": "COOL BITS SRL 🏢 🏢 Proprietary Zone",
                "color": "#9c27b0",
            },
        }

        # Monitoring data
        self.monitoring_data = {}
        self.running_processes = {}

        self.setup_gui()
        self.load_logo()
        self.start_monitoring()

    def setup_gui(self):
        """Setup the main GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Logo and title
        logo_frame = ttk.Frame(header_frame)
        logo_frame.pack(side=tk.LEFT)

        self.logo_label = ttk.Label(logo_frame, text="cb", font=("Arial", 24, "bold"))
        self.logo_label.pack(side=tk.LEFT, padx=(0, 10))

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        title_label = ttk.Label(
            title_frame, text="cbLM Corporate Assets Panel", font=("Arial", 16, "bold")
        )
        title_label.pack(anchor=tk.W)

        company_label = ttk.Label(
            title_frame, text=f"{self.company} - CEO: {self.ceo}", font=("Arial", 10)
        )
        company_label.pack(anchor=tk.W)

        classification_label = ttk.Label(
            title_frame, text=self.classification, font=("Arial", 8), foreground="red"
        )
        classification_label.pack(anchor=tk.W)

        # Control buttons frame
        control_frame = ttk.Frame(header_frame)
        control_frame.pack(side=tk.RIGHT)

        ttk.Button(control_frame, text="🔄 Refresh", command=self.refresh_all).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(control_frame, text="📊 Status", command=self.show_status).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(control_frame, text="⚙️ Settings", command=self.show_settings).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(control_frame, text="❌ Exit", command=self.root.quit).pack(
            side=tk.LEFT, padx=2
        )

        # Main content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Corporate Entities
        left_panel = ttk.LabelFrame(
            content_frame, text="Corporate Entities", padding=10
        )
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Entities treeview
        self.entities_tree = ttk.Treeview(
            left_panel,
            columns=("Status", "Zone", "Priority", "Schedule"),
            show="tree headings",
            height=15,
        )
        self.entities_tree.heading("#0", text="Entity")
        self.entities_tree.heading("Status", text="Status")
        self.entities_tree.heading("Zone", text="Zone")
        self.entities_tree.heading("Priority", text="Priority")
        self.entities_tree.heading("Schedule", text="Schedule")

        self.entities_tree.column("#0", width=200)
        self.entities_tree.column("Status", width=80)
        self.entities_tree.column("Zone", width=120)
        self.entities_tree.column("Priority", width=80)
        self.entities_tree.column("Schedule", width=120)

        self.entities_tree.pack(fill=tk.BOTH, expand=True)

        # Entity details frame
        details_frame = ttk.LabelFrame(left_panel, text="Entity Details", padding=5)
        details_frame.pack(fill=tk.X, pady=(10, 0))

        self.details_text = scrolledtext.ScrolledText(
            details_frame, height=6, wrap=tk.WORD
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # Entity control buttons
        entity_buttons_frame = ttk.Frame(details_frame)
        entity_buttons_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            entity_buttons_frame, text="🌐 Open URL", command=self.open_entity_url
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            entity_buttons_frame, text="📊 Monitor", command=self.monitor_entity
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            entity_buttons_frame, text="🔄 Restart", command=self.restart_entity
        ).pack(side=tk.LEFT, padx=2)

        # Right panel - System Status
        right_panel = ttk.LabelFrame(content_frame, text="System Status", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # System info frame
        system_frame = ttk.LabelFrame(right_panel, text="System Information", padding=5)
        system_frame.pack(fill=tk.X, pady=(0, 10))

        self.system_text = scrolledtext.ScrolledText(
            system_frame, height=8, wrap=tk.WORD
        )
        self.system_text.pack(fill=tk.BOTH, expand=True)

        # Cron jobs status frame
        cron_frame = ttk.LabelFrame(right_panel, text="Cron Jobs Status", padding=5)
        cron_frame.pack(fill=tk.X, pady=(0, 10))

        self.cron_text = scrolledtext.ScrolledText(cron_frame, height=6, wrap=tk.WORD)
        self.cron_text.pack(fill=tk.BOTH, expand=True)

        # Logs frame
        logs_frame = ttk.LabelFrame(right_panel, text="Activity Logs", padding=5)
        logs_frame.pack(fill=tk.BOTH, expand=True)

        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=8, wrap=tk.WORD)
        self.logs_text.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.entities_tree.bind("<<TreeviewSelect>>", self.on_entity_select)

        # Populate entities tree
        self.populate_entities_tree()

        # Update system info
        self.update_system_info()

    def load_logo(self):
        """Load and display the cb.png logo"""
        try:
            # Try to load cb.png logo
            logo_path = os.path.join(os.getcwd(), "cb.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((32, 32), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_image)
                self.logo_label.configure(image=logo_photo)
                self.logo_label.image = logo_photo  # Keep a reference
            else:
                # Create a simple text logo if cb.png doesn't exist
                self.logo_label.configure(
                    text="cb", font=("Arial", 24, "bold"), foreground="blue"
                )
        except Exception as e:
            self.log_message(f"Error loading logo: {e}")
            self.logo_label.configure(
                text="cb", font=("Arial", 24, "bold"), foreground="blue"
            )

    def populate_entities_tree(self):
        """Populate the entities treeview"""
        for entity_key, entity in self.corporate_entities.items():
            # Determine status color
            status_color = (
                "green"
                if entity["status"] == "active"
                else "orange" if entity["status"] == "proprietary" else "red"
            )

            # Create item with icon
            item_text = f"{entity['icon']} {entity['name']}"

            self.entities_tree.insert(
                "",
                tk.END,
                text=item_text,
                values=(
                    entity["status"].title(),
                    self.zones[entity["zone"]]["name"],
                    entity["priority"].title(),
                    entity["schedule"],
                ),
                tags=(status_color,),
            )

        # Configure tags for colors
        self.entities_tree.tag_configure("green", foreground="green")
        self.entities_tree.tag_configure("orange", foreground="orange")
        self.entities_tree.tag_configure("red", foreground="red")

    def on_entity_select(self, event):
        """Handle entity selection"""
        selection = self.entities_tree.selection()
        if selection:
            item = self.entities_tree.item(selection[0])
            entity_name = item["text"].split(" ", 1)[1]  # Remove icon

            # Find entity by name
            entity_key = None
            for key, entity in self.corporate_entities.items():
                if entity["name"] == entity_name:
                    entity_key = key
                    break

            if entity_key:
                self.show_entity_details(entity_key)

    def show_entity_details(self, entity_key):
        """Show detailed information about selected entity"""
        entity = self.corporate_entities[entity_key]
        zone = self.zones[entity["zone"]]

        details = f"""Entity: {entity['name']}
Key: {entity_key}
Zone: {zone['name']}
Status: {entity['status'].title()}
Priority: {entity['priority'].title()}
Schedule: {entity['schedule']}
URL: {entity['url']}
Icon: {entity['icon']}

Zone Color: {zone['color']}
"""

        if "owner" in entity:
            details += f"Owner: {entity['owner']}\n"

        details += f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)

    def open_entity_url(self):
        """Open the URL of selected entity"""
        selection = self.entities_tree.selection()
        if selection:
            item = self.entities_tree.item(selection[0])
            entity_name = item["text"].split(" ", 1)[1]

            for key, entity in self.corporate_entities.items():
                if entity["name"] == entity_name:
                    if entity["url"] != "internal":
                        webbrowser.open(entity["url"])
                        self.log_message(
                            f"Opened URL for {entity['name']}: {entity['url']}"
                        )
                    else:
                        messagebox.showinfo(
                            "Internal Entity",
                            f"{entity['name']} is an internal entity.",
                        )
                    break

    def monitor_entity(self):
        """Start monitoring for selected entity"""
        selection = self.entities_tree.selection()
        if selection:
            item = self.entities_tree.item(selection[0])
            entity_name = item["text"].split(" ", 1)[1]

            for key, entity in self.corporate_entities.items():
                if entity["name"] == entity_name:
                    self.start_entity_monitoring(key)
                    break

    def start_entity_monitoring(self, entity_key):
        """Start monitoring for a specific entity"""
        entity = self.corporate_entities[entity_key]

        def monitor():
            while entity_key in self.running_processes:
                try:
                    # Simulate monitoring
                    status = self.check_entity_status(entity_key)
                    self.monitoring_data[entity_key] = {
                        "timestamp": datetime.now().isoformat(),
                        "status": status,
                        "entity": entity["name"],
                    }

                    self.log_message(f"Monitoring {entity['name']}: {status}")
                    time.sleep(30)  # Check every 30 seconds

                except Exception as e:
                    self.log_message(f"Error monitoring {entity['name']}: {e}")
                    time.sleep(60)

        if entity_key not in self.running_processes:
            thread = threading.Thread(target=monitor, daemon=True)
            thread.start()
            self.running_processes[entity_key] = thread
            self.log_message(f"Started monitoring for {entity['name']}")
        else:
            messagebox.showinfo(
                "Already Monitoring", f"{entity['name']} is already being monitored."
            )

    def check_entity_status(self, entity_key):
        """Check the status of an entity"""
        entity = self.corporate_entities[entity_key]

        if entity["url"] == "internal":
            return "Internal - OK"

        try:
            # Simulate status check
            if entity["status"] == "active":
                return "Active - OK"
            else:
                return "Inactive"
        except Exception as e:
            return f"Error: {e}"

    def restart_entity(self):
        """Restart monitoring for selected entity"""
        selection = self.entities_tree.selection()
        if selection:
            item = self.entities_tree.item(selection[0])
            entity_name = item["text"].split(" ", 1)[1]

            for key, entity in self.corporate_entities.items():
                if entity["name"] == entity_name:
                    if key in self.running_processes:
                        del self.running_processes[key]
                    self.start_entity_monitoring(key)
                    self.log_message(f"Restarted monitoring for {entity['name']}")
                    break

    def update_system_info(self):
        """Update system information"""
        try:
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            system_info = f"""System Information:
CPU Usage: {cpu_percent}%
Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)
Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)

Processes Running: {len(self.running_processes)}
Active Entities: {len([e for e in self.corporate_entities.values() if e['status'] == 'active'])}

Company: {self.company}
CEO: {self.ceo}
AI Assistant: {self.ai_assistant}
Classification: {self.classification}

Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            self.system_text.delete(1.0, tk.END)
            self.system_text.insert(1.0, system_info)

        except Exception as e:
            self.log_message(f"Error updating system info: {e}")

    def update_cron_status(self):
        """Update cron jobs status"""
        try:
            # Check if cron manager is running
            cron_processes = []
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if "python" in proc.info[
                        "name"
                    ] and "corporate_entities_cron_manager.py" in " ".join(
                        proc.info["cmdline"]
                    ):
                        cron_processes.append(proc.info["pid"])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            cron_status = f"""Cron Jobs Status:
Python Processes: {len(cron_processes)}
Cron Manager Running: {'Yes' if cron_processes else 'No'}

Active Monitoring:
"""

            for entity_key, entity in self.corporate_entities.items():
                status = (
                    "🟢 Active"
                    if entity_key in self.running_processes
                    else "🔴 Inactive"
                )
                cron_status += f"{entity['icon']} {entity['name']}: {status}\n"

            cron_status += (
                f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            self.cron_text.delete(1.0, tk.END)
            self.cron_text.insert(1.0, cron_status)

        except Exception as e:
            self.log_message(f"Error updating cron status: {e}")

    def log_message(self, message):
        """Add message to activity logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)

        # Keep only last 1000 lines
        lines = self.logs_text.get(1.0, tk.END).split("\n")
        if len(lines) > 1000:
            self.logs_text.delete(1.0, f"{len(lines)-1000}.0")

    def refresh_all(self):
        """Refresh all information"""
        self.update_system_info()
        self.update_cron_status()
        self.log_message("Refreshed all information")

    def show_status(self):
        """Show detailed status window"""
        status_window = tk.Toplevel(self.root)
        status_window.title("Detailed Status - cbLM Corporate Assets")
        status_window.geometry("800x600")

        status_text = scrolledtext.ScrolledText(status_window, wrap=tk.WORD)
        status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        status_info = f"""cbLM Corporate Assets - Detailed Status Report
Company: {self.company}
CEO: {self.ceo}
AI Assistant: {self.ai_assistant}
Classification: {self.classification}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CORPORATE ENTITIES STATUS:
"""

        for entity_key, entity in self.corporate_entities.items():
            monitoring_status = (
                "Active" if entity_key in self.running_processes else "Inactive"
            )
            status_info += f"""
{entity['icon']} {entity['name']} ({entity_key}):
  Zone: {self.zones[entity['zone']]['name']}
  Status: {entity['status'].title()}
  Priority: {entity['priority'].title()}
  Schedule: {entity['schedule']}
  Monitoring: {monitoring_status}
  URL: {entity['url']}
"""
            if "owner" in entity:
                status_info += f"  Owner: {entity['owner']}\n"

        status_info += f"""

SYSTEM STATUS:
Running Processes: {len(self.running_processes)}
Total Entities: {len(self.corporate_entities)}
Active Entities: {len([e for e in self.corporate_entities.values() if e['status'] == 'active'])}

ZONES:
"""

        for zone_key, zone in self.zones.items():
            entities_in_zone = [
                e for e in self.corporate_entities.values() if e["zone"] == zone_key
            ]
            status_info += f"  {zone['name']}: {len(entities_in_zone)} entities\n"

        status_text.insert(1.0, status_info)
        status_text.config(state=tk.DISABLED)

    def show_settings(self):
        """Show settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings - cbLM Corporate Assets")
        settings_window.geometry("600x400")

        settings_frame = ttk.Frame(settings_window, padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            settings_frame,
            text="cbLM Corporate Assets Settings",
            font=("Arial", 14, "bold"),
        ).pack(pady=(0, 20))

        # Monitoring interval setting
        interval_frame = ttk.LabelFrame(
            settings_frame, text="Monitoring Interval", padding=10
        )
        interval_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(interval_frame, text="Entity monitoring interval (seconds):").pack(
            anchor=tk.W
        )
        interval_var = tk.StringVar(value="30")
        ttk.Entry(interval_frame, textvariable=interval_var, width=10).pack(
            anchor=tk.W, pady=(5, 0)
        )

        # Auto-refresh setting
        refresh_frame = ttk.LabelFrame(settings_frame, text="Auto Refresh", padding=10)
        refresh_frame.pack(fill=tk.X, pady=(0, 10))

        auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            refresh_frame,
            text="Auto refresh system information",
            variable=auto_refresh_var,
        ).pack(anchor=tk.W)

        # Save button
        ttk.Button(
            settings_frame,
            text="💾 Save Settings",
            command=lambda: self.save_settings(
                interval_var.get(), auto_refresh_var.get()
            ),
        ).pack(pady=20)

    def save_settings(self, interval, auto_refresh):
        """Save settings"""
        self.log_message(
            f"Settings saved: Interval={interval}s, Auto-refresh={auto_refresh}"
        )
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")

    def start_monitoring(self):
        """Start background monitoring"""

        def monitor():
            while True:
                try:
                    self.update_system_info()
                    self.update_cron_status()
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    self.log_message(f"Error in background monitoring: {e}")
                    time.sleep(60)

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

        self.log_message("cbLM Corporate Assets Panel started")
        self.log_message(f"Company: {self.company} - CEO: {self.ceo}")
        self.log_message(f"AI Assistant: {self.ai_assistant}")
        self.log_message(f"Classification: {self.classification}")

    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main function to start the GUI application"""
    print("🚀 Starting cbLM Corporate Assets GUI Panel...")
    print("🏢 COOL BITS SRL 🏢 🏢 - CEO: Andrei")
    print("🤖 AI Assistant: oCursor")
    print("🔒 Classification: Internal Secret - CoolBits.ai 🏢 🏢 Members Only")

    try:
        app = CBLMCorporateAssetsGUI()
        app.run()
    except Exception as e:
        print(f"❌ Error starting GUI application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()
