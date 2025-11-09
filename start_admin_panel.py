# CoolBits.ai Local Development Server
# Simple HTTP server for the admin panel

import http.server
import socketserver
import webbrowser
import os
import threading
import time
from datetime import datetime


class CoolBitsHTTPServer:
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.running = False

    def start_server(self):
        """Start the HTTP server"""
        try:
            # Change to the directory containing the HTML file
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

            # Create HTTP server
            handler = http.server.SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)

            print("🚀 CoolBits.ai Local Server Starting...")
            print(f"📡 Server running on http://localhost:{self.port}")
            print(f"📁 Serving files from: {os.getcwd()}")
            print(
                f"🌐 Admin Panel: http://localhost:{self.port}/coolbits_admin_panel.html"
            )
            print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
            print("🔄 Press Ctrl+C to stop the server")
            print("=" * 60)

            # Open browser automatically
            threading.Thread(target=self.open_browser, daemon=True).start()

            # Start server
            self.running = True
            self.server.serve_forever()

        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            self.stop_server()
        except Exception as e:
            print(f"❌ Error starting server: {e}")

    def open_browser(self):
        """Open browser automatically"""
        time.sleep(2)  # Wait for server to start
        try:
            webbrowser.open(f"http://localhost:{self.port}/coolbits_admin_panel.html")
            print("🌐 Browser opened automatically")
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
            print(
                f"🌐 Please open manually: http://localhost:{self.port}/coolbits_admin_panel.html"
            )

    def stop_server(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            print("✅ Server stopped successfully")


def main():
    """Main function"""
    print("🎯 CoolBits.ai Local Development Server")
    print("=" * 60)

    # Check if HTML file exists
    if not os.path.exists("coolbits_admin_panel.html"):
        print("❌ Error: coolbits_admin_panel.html not found!")
        print("📁 Please make sure the HTML file is in the same directory")
        return

    # Start server
    server = CoolBitsHTTPServer(8080)
    server.start_server()


if __name__ == "__main__":
    main()
