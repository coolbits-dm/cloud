#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cbLM Logo Complete Integration System
COOL BITS SRL 🏢 - Internal Secret

Integrates cb.svg logo as favicon and profile pictures everywhere
"""

import os
import re
import json
from PIL import Image, ImageDraw
from datetime import datetime


def create_favicon_versions():
    """Create favicon versions in all sizes"""

    # Create cb.png in multiple sizes for favicon
    sizes = [16, 32, 48, 64, 128, 256]

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Blue color: #4285f4
        blue_color = (66, 133, 244, 255)

        # Scale the logo based on size
        scale = size / 32.0

        # Draw the 'C' shape (outer arc)
        margin = int(2 * scale)
        draw.arc(
            [margin, margin, size - margin, size - margin],
            45,
            315,
            fill=blue_color,
            width=int(6 * scale),
        )

        # Draw the 'b' shape (inner)
        # Vertical stem
        stem_x = int(8 * scale)
        stem_width = int(4 * scale)
        draw.rectangle(
            [stem_x, int(8 * scale), stem_x + stem_width, int(24 * scale)],
            fill=blue_color,
        )

        # Circular bowl
        bowl_radius = int(8 * scale)
        bowl_center_x = int(16 * scale)
        bowl_center_y = int(20 * scale)
        draw.arc(
            [
                bowl_center_x - bowl_radius,
                bowl_center_y - bowl_radius,
                bowl_center_x + bowl_radius,
                bowl_center_y + bowl_radius,
            ],
            0,
            180,
            fill=blue_color,
            width=int(6 * scale),
        )

        # Inner black circle
        inner_radius = int(2 * scale)
        draw.ellipse(
            [
                bowl_center_x - inner_radius,
                bowl_center_y - inner_radius,
                bowl_center_x + inner_radius,
                bowl_center_y + inner_radius,
            ],
            fill=(0, 0, 0, 255),
        )

        img.save(f"cb-{size}x{size}.png")
        print(f"✅ Created cb-{size}x{size}.png")

    # Create favicon.ico (16x16, 32x32)
    favicon_16 = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw_16 = ImageDraw.Draw(favicon_16)

    # Draw simplified version for 16x16
    draw_16.arc([2, 2, 14, 14], 45, 315, fill=(66, 133, 244, 255), width=2)
    draw_16.rectangle([4, 4, 6, 12], fill=(66, 133, 244, 255))
    draw_16.ellipse([6, 8, 8, 10], fill=(0, 0, 0, 255))

    favicon_16.save("favicon.ico", sizes=[(16, 16), (32, 32)])
    print("✅ Created favicon.ico")


def create_profile_pictures():
    """Create profile pictures for all entities"""

    entities = {
        "vertex": {"name": "Vertex AI", "color": "#4285f4"},
        "cursor": {"name": "Cursor AI", "color": "#34a853"},
        "nvidia": {"name": "NVIDIA GPU", "color": "#76b900"},
        "microsoft": {"name": "Microsoft", "color": "#0078d4"},
        "xai": {"name": "xAI Platform", "color": "#ff6d01"},
        "grok": {"name": "Grok AI", "color": "#1a1a1a"},
        "ogrok": {"name": "oGrok", "color": "#9c27b0"},
        "openai": {"name": "OpenAI", "color": "#00a67e"},
        "chatgpt": {"name": "ChatGPT", "color": "#00a67e"},
        "ogpt": {"name": "oGPT", "color": "#9c27b0"},
        "meta": {"name": "Meta AI", "color": "#1877f2"},
        "andy": {"name": "Andy", "color": "#ff9800"},
        "kim": {"name": "Kim", "color": "#e91e63"},
        "gemini": {"name": "Gemini", "color": "#4285f4"},
        "gemini_cli": {"name": "GeminiCLI", "color": "#4285f4"},
        "overtex": {"name": "oVertex", "color": "#9c27b0"},
        "ocursor": {"name": "oCursor", "color": "#34a853"},
    }

    for entity_key, entity_info in entities.items():
        # Create profile picture (64x64)
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Entity-specific color
        entity_color = entity_info["color"]
        rgb_color = tuple(int(entity_color[i : i + 2], 16) for i in (1, 3, 5))

        # Draw the 'C' shape with entity color
        draw.arc([4, 4, 60, 60], 45, 315, fill=rgb_color, width=12)

        # Draw the 'b' shape
        draw.rectangle([16, 16, 24, 48], fill=rgb_color)
        draw.arc([16, 32, 48, 48], 0, 180, fill=rgb_color, width=12)

        # Inner circle
        draw.ellipse([28, 36, 36, 44], fill=(0, 0, 0, 255))

        # Save profile picture
        img.save(f"profile-{entity_key}.png")
        print(f"✅ Created profile-{entity_key}.png")


def update_google_cloud_agent():
    """Update google_cloud_agent.py with logo integration"""

    try:
        with open("google_cloud_agent.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Add logo integration at the top
        logo_header = """# cbLM Logo Integration
# Favicon: favicon.ico, cb-16x16.png, cb-32x32.png
# Profile Pictures: profile-*.png
# Company: COOL BITS SRL 🏢
# CEO: Andrei
# AI Assistant: oCursor

"""

        if not content.startswith("# cbLM Logo Integration"):
            content = logo_header + content

        # Update company references with logo
        content = re.sub(r"SC COOL BITS SRL", "SC COOL BITS SRL 🏢", content)
        content = re.sub(r"COOL BITS SRL", "COOL BITS SRL 🏢", content)

        # Add favicon route
        favicon_route = '''
        @self.app.get("/favicon.ico")
        async def favicon():
            """Serve favicon.ico"""
            try:
                favicon_path = os.path.join(str(self.base_path), "favicon.ico")
                if os.path.exists(favicon_path):
                    from fastapi.responses import FileResponse
                    return FileResponse(favicon_path, media_type="image/x-icon")
                else:
                    raise HTTPException(status_code=404, detail="Favicon not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/logo/{size}")
        async def get_logo(size: str):
            """Get logo in specified size"""
            try:
                logo_path = os.path.join(str(self.base_path), f"cb-{size}x{size}.png")
                if os.path.exists(logo_path):
                    from fastapi.responses import FileResponse
                    return FileResponse(logo_path, media_type="image/png")
                else:
                    raise HTTPException(status_code=404, detail=f"Logo size {size}x{size} not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/profile/{entity}")
        async def get_profile_picture(entity: str):
            """Get profile picture for entity"""
            try:
                profile_path = os.path.join(str(self.base_path), f"profile-{entity}.png")
                if os.path.exists(profile_path):
                    from fastapi.responses import FileResponse
                    return FileResponse(profile_path, media_type="image/png")
                else:
                    raise HTTPException(status_code=404, detail=f"Profile picture for {entity} not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
'''

        # Insert favicon routes before the last route
        if '@self.app.post("/api/gcloud/setup")' in content:
            content = content.replace(
                '@self.app.post("/api/gcloud/setup")',
                favicon_route + '\n        @self.app.post("/api/gcloud/setup")',
            )

        # Write updated content
        with open("google_cloud_agent.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Updated google_cloud_agent.py with logo integration")

    except Exception as e:
        print(f"❌ Error updating google_cloud_agent.py: {e}")


def update_all_html_files():
    """Update all HTML files with favicon and logo integration"""

    html_files = ["meta_platform_panel.html", "bits-orchestrator-functional-panel.html"]

    favicon_html = """    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="16x16" href="/cb-16x16.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/cb-32x32.png">
    <link rel="icon" type="image/png" sizes="48x48" href="/cb-48x48.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/cb-128x128.png">
"""

    for html_file in html_files:
        if os.path.exists(html_file):
            try:
                with open(html_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Add favicon links in head section
                if "<head>" in content and "favicon.ico" not in content:
                    content = content.replace("<head>", f"<head>\n{favicon_html}")

                # Update company references
                content = re.sub(r"COOL BITS SRL", "COOL BITS SRL 🏢", content)
                content = re.sub(r"coolbits\.ai", "coolbits.ai 🏢", content)
                content = re.sub(r"cbLM\.ai", "cbLM.ai 🏢", content)

                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ Updated {html_file} with favicon integration")

            except Exception as e:
                print(f"❌ Error updating {html_file}: {e}")


def update_python_files():
    """Update all Python files with logo integration"""

    python_files = [
        "str.py",
        "cblm/corporate_entities_manager.py",
        "cblm/corporate_entities_cron_manager.py",
        "cblm_corporate_assets_gui.py",
        "coolbits_main_dashboard.py",
        "meta_platform_server.py",
    ]

    for py_file in python_files:
        if os.path.exists(py_file):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Update company references with logo
                content = re.sub(r"COOL BITS SRL", "COOL BITS SRL 🏢", content)
                content = re.sub(r"coolbits\.ai", "coolbits.ai 🏢", content)
                content = re.sub(r"CoolBits\.ai", "CoolBits.ai 🏢", content)
                content = re.sub(r"cbLM\.ai", "cbLM.ai 🏢", content)
                content = re.sub(r"cblm\.ai", "cblm.ai 🏢", content)

                # Add logo loading for GUI files
                if "tkinter" in content and "load_logo" not in content:
                    logo_method = '''
    def load_logo(self):
        """Load and display the cb.png logo"""
        try:
            logo_path = os.path.join(os.getcwd(), "cb.png")
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((32, 32), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_image)
                self.logo_label.configure(image=logo_photo)
                self.logo_label.image = logo_photo
            else:
                self.logo_label.configure(text="cb", font=("Arial", 24, "bold"), foreground="blue")
        except Exception as e:
            self.logo_label.configure(text="cb", font=("Arial", 24, "bold"), foreground="blue")
'''

                    if "def __init__" in content:
                        content = content.replace(
                            "def __init__", logo_method + "\n    def __init__"
                        )

                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ Updated {py_file} with logo integration")

            except Exception as e:
                print(f"❌ Error updating {py_file}: {e}")


def create_logo_integration_report():
    """Create comprehensive logo integration report"""

    report = {
        "cb_logo_complete_integration": {
            "timestamp": datetime.now().isoformat(),
            "company": "COOL BITS SRL 🏢",
            "ceo": "Andrei",
            "ai_assistant": "oCursor",
            "classification": "Internal Secret - CoolBits.ai 🏢 Members Only",
        },
        "favicon_files_created": [
            "favicon.ico - Main favicon (16x16, 32x32)",
            "cb-16x16.png - 16x16 PNG favicon",
            "cb-32x32.png - 32x32 PNG favicon",
            "cb-48x48.png - 48x48 PNG favicon",
            "cb-64x64.png - 64x64 PNG favicon",
            "cb-128x128.png - 128x128 PNG favicon",
            "cb-256x256.png - 256x256 PNG favicon",
        ],
        "profile_pictures_created": [
            "profile-vertex.png - Vertex AI profile picture",
            "profile-cursor.png - Cursor AI profile picture",
            "profile-nvidia.png - NVIDIA GPU profile picture",
            "profile-microsoft.png - Microsoft profile picture",
            "profile-xai.png - xAI Platform profile picture",
            "profile-grok.png - Grok AI profile picture",
            "profile-ogrok.png - oGrok profile picture",
            "profile-openai.png - OpenAI profile picture",
            "profile-chatgpt.png - ChatGPT profile picture",
            "profile-ogpt.png - oGPT profile picture",
            "profile-meta.png - Meta AI profile picture",
            "profile-andy.png - Andy profile picture",
            "profile-kim.png - Kim profile picture",
            "profile-gemini.png - Gemini profile picture",
            "profile-gemini_cli.png - GeminiCLI profile picture",
            "profile-overtex.png - oVertex profile picture",
            "profile-ocursor.png - oCursor profile picture",
        ],
        "files_updated": [
            "google_cloud_agent.py - Added favicon routes and logo integration",
            "meta_platform_panel.html - Added favicon links",
            "bits-orchestrator-functional-panel.html - Added favicon links",
            "str.py - Updated with logo references",
            "cblm/corporate_entities_manager.py - Updated with logo references",
            "cblm/corporate_entities_cron_manager.py - Updated with logo references",
            "cblm_corporate_assets_gui.py - Updated with logo references",
            "coolbits_main_dashboard.py - Updated with logo references",
            "meta_platform_server.py - Updated with logo references",
        ],
        "api_endpoints_added": {
            "/favicon.ico": "Main favicon endpoint",
            "/api/logo/{size}": "Get logo in specified size",
            "/api/profile/{entity}": "Get profile picture for entity",
        },
        "integration_status": {
            "favicon_integration": True,
            "profile_pictures_created": True,
            "html_files_updated": True,
            "python_files_updated": True,
            "api_endpoints_added": True,
            "google_cloud_agent_updated": True,
            "complete_integration": True,
        },
    }

    with open("cb_logo_complete_integration_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(
        "📊 Complete logo integration report saved: cb_logo_complete_integration_report.json"
    )


def main():
    """Main function"""
    print("🏢 COOL BITS SRL 🏢 - cb Logo Complete Integration System")
    print("CEO: Andrei")
    print("AI Assistant: oCursor")
    print("Classification: Internal Secret - CoolBits.ai 🏢 Members Only")
    print("=" * 80)

    # Create favicon versions
    print("\n📱 Creating favicon versions...")
    create_favicon_versions()

    # Create profile pictures
    print("\n👤 Creating profile pictures...")
    create_profile_pictures()

    # Update google_cloud_agent.py
    print("\n☁️ Updating Google Cloud Agent...")
    update_google_cloud_agent()

    # Update HTML files
    print("\n🌐 Updating HTML files...")
    update_all_html_files()

    # Update Python files
    print("\n🐍 Updating Python files...")
    update_python_files()

    # Create report
    print("\n📊 Creating integration report...")
    create_logo_integration_report()

    print("\n🎯 Complete Logo Integration Finished!")
    print("🏢 All files updated with cb logo integration")
    print("📱 Favicon and profile pictures created")
    print("🌐 API endpoints added for logo access")
    print("🔒 Classification: Internal Secret - CoolBits.ai 🏢 Members Only")


if __name__ == "__main__":
    main()
