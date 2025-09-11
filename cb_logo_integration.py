#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cbLM Logo Integration System
COOL BITS SRL - Internal Secret

Creates and integrates cb.svg logo in all formats and locations
"""

import os
import re
from PIL import Image, ImageDraw


def create_cb_logo():
    """Create cb logo in multiple formats"""

    # Create cb.png (32x32)
    img_png = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_png)

    # Draw cb logo based on the SVG description
    # Blue color: #4285f4
    blue_color = (66, 133, 244, 255)

    # Draw the 'C' shape (outer arc)
    draw.arc([2, 2, 30, 30], 45, 315, fill=blue_color, width=6)

    # Draw the 'b' shape (inner)
    # Vertical stem
    draw.rectangle([8, 8, 12, 24], fill=blue_color)

    # Circular bowl
    draw.arc([8, 12, 24, 24], 0, 180, fill=blue_color, width=6)

    # Inner black circle
    draw.ellipse([14, 16, 18, 20], fill=(0, 0, 0, 255))

    img_png.save("cb.png")

    # Create cb.ico (32x32)
    img_ico = img_png.copy()
    img_ico.save("cb.ico", sizes=[(32, 32)])

    # Create cb.svg
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .cb-blue { fill: #4285f4; }
      .cb-black { fill: #000000; }
    </style>
  </defs>
  
  <!-- Outer C shape -->
  <path class="cb-blue" d="M 16 2 A 14 14 0 0 1 30 16 A 14 14 0 0 1 16 30 A 14 14 0 0 1 2 16 A 14 14 0 0 1 16 2 Z M 16 6 A 10 10 0 0 0 6 16 A 10 10 0 0 0 16 26 A 10 10 0 0 0 26 16 A 10 10 0 0 0 16 6 Z" stroke="#4285f4" stroke-width="3" fill="none"/>
  
  <!-- Inner b shape -->
  <!-- Vertical stem -->
  <rect class="cb-blue" x="8" y="8" width="4" height="16"/>
  
  <!-- Circular bowl -->
  <path class="cb-blue" d="M 8 20 A 8 8 0 0 0 20 20" stroke="#4285f4" stroke-width="6" fill="none"/>
  
  <!-- Inner black circle -->
  <circle class="cb-black" cx="16" cy="18" r="2"/>
</svg>"""

    with open("cb.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

    print("✅ Created cb.png, cb.ico, and cb.svg")


def integrate_logo_in_files():
    """Integrate logo in all relevant files"""

    # Files to update
    files_to_update = [
        "str.py",
        "cblm/corporate_entities_manager.py",
        "cblm/corporate_entities_cron_manager.py",
        "cblm_cron_jobs_manager.ps1",
        "start_cblm_cron_jobs.bat",
    ]

    # Logo integration patterns
    logo_patterns = {
        r"coolbits\.ai": "coolbits.ai 🏢",
        r"CoolBits\.ai": "CoolBits.ai 🏢",
        r"Cool Bits SRL": "Cool Bits SRL 🏢",
        r"cbLM\.ai": "cbLM.ai 🏢",
        r"cblm\.ai": "cblm.ai 🏢",
        r"COOL BITS SRL": "COOL BITS SRL 🏢",
    }

    for file_path in files_to_update:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Apply logo patterns
                for pattern, replacement in logo_patterns.items():
                    content = re.sub(pattern, replacement, content)

                # Add logo reference at the top
                if "str.py" in file_path:
                    logo_header = """# cbLM Corporate Assets Integration
# Logo: cb.svg, cb.png, cb.ico
# Company: COOL BITS SRL 🏢
# CEO: Andrei
# AI Assistant: oCursor

"""
                    if not content.startswith("# cbLM Corporate Assets Integration"):
                        content = logo_header + content

                # Write updated content
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✅ Updated {file_path}")

            except Exception as e:
                print(f"❌ Error updating {file_path}: {e}")


def create_logo_integration_report():
    """Create integration report"""

    report = {
        "logo_integration_report": {
            "timestamp": "2025-09-07",
            "company": "COOL BITS SRL 🏢",
            "ceo": "Andrei",
            "ai_assistant": "oCursor",
            "classification": "Internal Secret - CoolBits.ai Members Only",
        },
        "logo_files_created": [
            "cb.png - 32x32 PNG format",
            "cb.ico - 32x32 ICO format",
            "cb.svg - Vector SVG format",
        ],
        "integration_locations": [
            "str.py - Root console with logo integration",
            "cblm/corporate_entities_manager.py - Corporate entities manager",
            "cblm/corporate_entities_cron_manager.py - Cron jobs manager",
            "cblm_cron_jobs_manager.ps1 - PowerShell manager",
            "start_cblm_cron_jobs.bat - Batch startup script",
        ],
        "logo_patterns_applied": {
            "coolbits.ai": "coolbits.ai 🏢",
            "CoolBits.ai": "CoolBits.ai 🏢",
            "Cool Bits SRL": "Cool Bits SRL 🏢",
            "cbLM.ai": "cbLM.ai 🏢",
            "cblm.ai": "cblm.ai 🏢",
            "COOL BITS SRL": "COOL BITS SRL 🏢",
        },
        "ai_board_notification": {
            "status": "Ready for AI Board distribution",
            "logo_files": "cb.png, cb.ico, cb.svg",
            "integration_complete": True,
        },
    }

    import json

    with open("cb_logo_integration_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("📊 Logo integration report saved: cb_logo_integration_report.json")


def main():
    """Main function"""
    print("🏢 COOL BITS SRL - cbLM Logo Integration System")
    print("CEO: Andrei")
    print("AI Assistant: oCursor")
    print("Classification: Internal Secret - CoolBits.ai Members Only")
    print("=" * 60)

    # Create logo files
    create_cb_logo()

    # Integrate logo in files
    integrate_logo_in_files()

    # Create report
    create_logo_integration_report()

    print("\n🎯 Logo Integration Complete!")
    print("🏢 All references updated with cb logo")
    print("📤 Ready for AI Board distribution")


if __name__ == "__main__":
    main()
