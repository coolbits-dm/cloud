#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@oEmail Footer Management System
Professional email footers for CoolBits.ai with best practices
"""

import sys
import json
import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ContactInfo:
    """Contact information structure"""

    name: str
    title: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None


@dataclass
class SocialMedia:
    """Social media links structure"""

    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


class CoolBitsEmailFooterManager:
    """
    Professional email footer management system for CoolBits.ai
    """

    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.project_domain = "coolbits.ai"
        self.cblm_domain = "cblm.ai"

        # Contact information for different roles
        self.contact_info = {
            "andrei@coolbits.ai": ContactInfo(
                name="Andrei",
                title="CEO & Founder",
                email="andrei@coolbits.ai",
                phone="+40 749 956 945",
                website="https://coolbits.ai",
                address="Iași, Romania",
            ),
            "office@coolbits.ai": ContactInfo(
                name="CoolBits.ai Office",
                title="Administrative Office",
                email="office@coolbits.ai",
                phone="+40 749 956 945",
                website="https://coolbits.ai",
                address="Iași, Romania",
            ),
        }

        # Social media links
        self.social_media = SocialMedia(
            linkedin="https://linkedin.com/company/coolbits-ai",
            twitter="https://twitter.com/coolbits_ai",
            github="https://github.com/coolbits-ai",
            website="https://coolbits.ai",
        )

        # Legal and compliance information
        self.legal_info = {
            "company_registration": "COOL BITS S.R.L.",
            "cui": "42331573",
            "registration": "ROONRC.J22/676/2020",
            "classification": "Internal Secret - CoolBits.ai Members Only",
            "gdpr_compliance": "GDPR Compliant",
            "data_protection": "Data Protection Policy Available",
        }

    def generate_html_footer(self, email_address: str, style: str = "modern") -> str:
        """Generate HTML email footer"""
        if email_address not in self.contact_info:
            raise ValueError(f"Email address {email_address} not configured")

        contact = self.contact_info[email_address]

        if style == "modern":
            return self._generate_modern_html_footer(contact)
        elif style == "minimal":
            return self._generate_minimal_html_footer(contact)
        elif style == "corporate":
            return self._generate_corporate_html_footer(contact)
        else:
            return self._generate_modern_html_footer(contact)

    def _generate_modern_html_footer(self, contact: ContactInfo) -> str:
        """Generate modern HTML footer"""
        return f"""
<div style="font-family: Arial, sans-serif; font-size: 12px; color: #666666; line-height: 1.4; margin-top: 20px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
    <table style="width: 100%; max-width: 600px;">
        <tr>
            <td style="vertical-align: top; padding-right: 20px;">
                <div style="margin-bottom: 10px;">
                    <strong style="color: #333333; font-size: 14px;">{contact.name}</strong><br>
                    <span style="color: #888888;">{contact.title}</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>{self.company}</strong><br>
                    <span style="color: #888888;">{contact.address}</span>
                </div>
            </td>
            <td style="vertical-align: top; padding-left: 20px;">
                <div style="margin-bottom: 8px;">
                    <strong>📧 Email:</strong> <a href="mailto:{contact.email}" style="color: #0066cc; text-decoration: none;">{contact.email}</a>
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>📱 Phone:</strong> <a href="tel:{contact.phone}" style="color: #0066cc; text-decoration: none;">{contact.phone}</a>
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>🌐 Website:</strong> <a href="{contact.website}" style="color: #0066cc; text-decoration: none;">{contact.website}</a>
                </div>
            </td>
        </tr>
    </table>
    
    <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #f0f0f0;">
        <div style="margin-bottom: 8px;">
            <strong>🔗 Connect with us:</strong>
            <a href="{self.social_media.linkedin}" style="color: #0066cc; text-decoration: none; margin-right: 10px;">LinkedIn</a>
            <a href="{self.social_media.twitter}" style="color: #0066cc; text-decoration: none; margin-right: 10px;">Twitter</a>
            <a href="{self.social_media.github}" style="color: #0066cc; text-decoration: none; margin-right: 10px;">GitHub</a>
        </div>
        
        <div style="font-size: 10px; color: #999999; margin-top: 10px;">
            <strong>Legal Information:</strong><br>
            {self.legal_info["company_registration"]} | CUI: {self.legal_info["cui"]} | Reg. No: {self.legal_info["registration"]}<br>
            <strong>Classification:</strong> {self.legal_info["classification"]}<br>
            <strong>Compliance:</strong> {self.legal_info["gdpr_compliance"]} | {self.legal_info["data_protection"]}
        </div>
        
        <div style="font-size: 10px; color: #cccccc; margin-top: 8px; text-align: center;">
            © {datetime.now().year} {self.company}. All rights reserved. | Powered by @oOutlook Email Management System
        </div>
    </div>
</div>
"""

    def _generate_minimal_html_footer(self, contact: ContactInfo) -> str:
        """Generate minimal HTML footer"""
        return f"""
<div style="font-family: Arial, sans-serif; font-size: 11px; color: #666666; line-height: 1.3; margin-top: 20px; padding-top: 10px; border-top: 1px solid #e0e0e0;">
    <div style="margin-bottom: 5px;">
        <strong>{contact.name}</strong> | {contact.title} | {self.company}
    </div>
    <div style="margin-bottom: 5px;">
        📧 <a href="mailto:{contact.email}" style="color: #0066cc;">{contact.email}</a> | 
        📱 <a href="tel:{contact.phone}" style="color: #0066cc;">{contact.phone}</a> | 
        🌐 <a href="{contact.website}" style="color: #0066cc;">{contact.website}</a>
    </div>
    <div style="font-size: 9px; color: #999999; margin-top: 8px;">
        {self.legal_info["company_registration"]} | CUI: {self.legal_info["cui"]} | 
        Classification: {self.legal_info["classification"]} | 
        © {datetime.now().year} {self.company}
    </div>
</div>
"""

    def _generate_corporate_html_footer(self, contact: ContactInfo) -> str:
        """Generate corporate HTML footer"""
        return f"""
<div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; color: #333333; line-height: 1.5; margin-top: 25px; padding: 20px; background-color: #f8f9fa; border-left: 4px solid #0066cc;">
    <table style="width: 100%; max-width: 600px;">
        <tr>
            <td style="vertical-align: top; width: 60%;">
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 16px; font-weight: bold; color: #0066cc; margin-bottom: 4px;">{contact.name}</div>
                    <div style="color: #666666; font-weight: 500;">{contact.title}</div>
                </div>
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 14px; font-weight: bold; color: #333333;">{self.company}</div>
                    <div style="color: #666666;">{contact.address}</div>
                </div>
            </td>
            <td style="vertical-align: top; width: 40%;">
                <div style="margin-bottom: 8px;">
                    <span style="font-weight: bold;">Email:</span> <a href="mailto:{contact.email}" style="color: #0066cc; text-decoration: none;">{contact.email}</a>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="font-weight: bold;">Phone:</span> <a href="tel:{contact.phone}" style="color: #0066cc; text-decoration: none;">{contact.phone}</a>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="font-weight: bold;">Web:</span> <a href="{contact.website}" style="color: #0066cc; text-decoration: none;">{contact.website}</a>
                </div>
            </td>
        </tr>
    </table>
    
    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
        <div style="margin-bottom: 10px;">
            <span style="font-weight: bold;">Connect:</span>
            <a href="{self.social_media.linkedin}" style="color: #0066cc; text-decoration: none; margin-right: 15px;">LinkedIn</a>
            <a href="{self.social_media.twitter}" style="color: #0066cc; text-decoration: none; margin-right: 15px;">Twitter</a>
            <a href="{self.social_media.github}" style="color: #0066cc; text-decoration: none;">GitHub</a>
        </div>
        
        <div style="font-size: 10px; color: #666666; line-height: 1.4;">
            <div style="margin-bottom: 4px;">
                <strong>Company:</strong> {self.legal_info["company_registration"]} | 
                <strong>CUI:</strong> {self.legal_info["cui"]} | 
                <strong>Registration:</strong> {self.legal_info["registration"]}
            </div>
            <div style="margin-bottom: 4px;">
                <strong>Classification:</strong> {self.legal_info["classification"]}
            </div>
            <div>
                <strong>Compliance:</strong> {self.legal_info["gdpr_compliance"]} | {self.legal_info["data_protection"]}
            </div>
        </div>
        
        <div style="font-size: 9px; color: #999999; margin-top: 10px; text-align: center; font-style: italic;">
            © {datetime.now().year} {self.company}. All rights reserved. | Powered by @oOutlook Email Management System
        </div>
    </div>
</div>
"""

    def generate_text_footer(self, email_address: str) -> str:
        """Generate plain text email footer"""
        if email_address not in self.contact_info:
            raise ValueError(f"Email address {email_address} not configured")

        contact = self.contact_info[email_address]

        return f"""
---
{contact.name} | {contact.title}
{self.company}
{contact.address}

📧 Email: {contact.email}
📱 Phone: {contact.phone}
🌐 Website: {contact.website}

🔗 Connect with us:
LinkedIn: {self.social_media.linkedin}
Twitter: {self.social_media.twitter}
GitHub: {self.social_media.github}

Legal Information:
{self.legal_info["company_registration"]} | CUI: {self.legal_info["cui"]} | Reg. No: {self.legal_info["registration"]}
Classification: {self.legal_info["classification"]}
Compliance: {self.legal_info["gdpr_compliance"]} | {self.legal_info["data_protection"]}

© {datetime.now().year} {self.company}. All rights reserved.
Powered by @oOutlook Email Management System
"""

    def generate_signature_block(self, email_address: str) -> str:
        """Generate email signature block"""
        if email_address not in self.contact_info:
            raise ValueError(f"Email address {email_address} not configured")

        contact = self.contact_info[email_address]

        return f"""
Best regards,

{contact.name}
{contact.title}
{self.company}

📧 {contact.email} | 📱 {contact.phone}
🌐 {contact.website}
"""

    def create_footer_templates(self):
        """Create all footer templates"""
        logger.info("Creating email footer templates...")

        templates = {}

        for email_address in self.contact_info.keys():
            templates[email_address] = {
                "html_footers": {
                    "modern": self.generate_html_footer(email_address, "modern"),
                    "minimal": self.generate_html_footer(email_address, "minimal"),
                    "corporate": self.generate_html_footer(email_address, "corporate"),
                },
                "text_footer": self.generate_text_footer(email_address),
                "signature_block": self.generate_signature_block(email_address),
            }

        # Save templates to file
        with open("email_footer_templates.json", "w") as f:
            json.dump(templates, f, indent=2)

        logger.info("Email footer templates created: email_footer_templates.json")
        return templates

    def generate_footer_css(self) -> str:
        """Generate CSS styles for email footers"""
        css_content = """
/* CoolBits.ai Email Footer Styles */

.coolbits-footer {
    font-family: Arial, sans-serif;
    font-size: 12px;
    color: #666666;
    line-height: 1.4;
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #e0e0e0;
}

.coolbits-footer-modern {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.coolbits-footer-minimal {
    background-color: #f8f9fa;
    padding: 15px;
    border-left: 3px solid #0066cc;
}

.coolbits-footer-corporate {
    background-color: #f8f9fa;
    padding: 20px;
    border-left: 4px solid #0066cc;
    border-radius: 3px;
}

.coolbits-contact-name {
    font-size: 14px;
    font-weight: bold;
    color: #333333;
    margin-bottom: 4px;
}

.coolbits-contact-title {
    color: #888888;
    font-weight: 500;
}

.coolbits-company-name {
    font-size: 14px;
    font-weight: bold;
    color: #333333;
    margin-bottom: 4px;
}

.coolbits-contact-info {
    margin-bottom: 8px;
}

.coolbits-contact-info a {
    color: #0066cc;
    text-decoration: none;
}

.coolbits-contact-info a:hover {
    text-decoration: underline;
}

.coolbits-social-links {
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px solid #f0f0f0;
}

.coolbits-social-links a {
    color: #0066cc;
    text-decoration: none;
    margin-right: 10px;
}

.coolbits-legal-info {
    font-size: 10px;
    color: #999999;
    margin-top: 10px;
    line-height: 1.3;
}

.coolbits-copyright {
    font-size: 10px;
    color: #cccccc;
    margin-top: 8px;
    text-align: center;
    font-style: italic;
}

/* Responsive design */
@media only screen and (max-width: 600px) {
    .coolbits-footer {
        font-size: 11px;
        padding: 15px;
    }
    
    .coolbits-contact-name {
        font-size: 13px;
    }
    
    .coolbits-company-name {
        font-size: 13px;
    }
}
"""

        with open("email_footer_styles.css", "w") as f:
            f.write(css_content)

        logger.info("Email footer CSS created: email_footer_styles.css")
        return css_content

    def create_footer_implementation_script(self):
        """Create implementation script for email footers"""
        script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@oEmail Footer Implementation Script
Implementation script for CoolBits.ai email footers
"""

import json
import logging
from datetime import datetime
from email_footer_manager import CoolBitsEmailFooterManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailFooterImplementation:
    """
    Email footer implementation for CoolBits.ai
    """
    
    def __init__(self):
        self.footer_manager = CoolBitsEmailFooterManager()
        self.company = "{self.company}"
        self.ceo = "{self.ceo}"
    
    def implement_footers(self):
        """Implement email footers for all configured addresses"""
        logger.info("Implementing email footers...")
        
        print("=" * 80)
        print("EMAIL FOOTER IMPLEMENTATION - COOLBITS.AI")
        print("=" * 80)
        print(f"Company: {{self.company}}")
        print(f"CEO: {{self.ceo}}")
        print("=" * 80)
        
        # Create templates
        templates = self.footer_manager.create_footer_templates()
        
        # Generate CSS
        self.footer_manager.generate_footer_css()
        
        # Display implementation status
        for email_address in templates.keys():
            print(f"\\n📧 {{email_address}}:")
            print(f"   ✅ HTML Footer (Modern) - Generated")
            print(f"   ✅ HTML Footer (Minimal) - Generated")
            print(f"   ✅ HTML Footer (Corporate) - Generated")
            print(f"   ✅ Text Footer - Generated")
            print(f"   ✅ Signature Block - Generated")
        
        print("=" * 80)
        print("🎉 EMAIL FOOTER IMPLEMENTATION COMPLETED")
        print("=" * 80)
        print("📁 Generated Files:")
        print("• email_footer_templates.json")
        print("• email_footer_styles.css")
        print("• email_footer_manager.py")
        print("=" * 80)
        print("🚀 Next Steps:")
        print("1. Integrate footers into email system")
        print("2. Configure email clients with templates")
        print("3. Test footer rendering")
        print("4. Deploy to production")
        print("=" * 80)
        
        logger.info("Email footer implementation completed successfully")
    
    def test_footer_rendering(self):
        """Test footer rendering for all styles"""
        logger.info("Testing footer rendering...")
        
        print("🧪 Testing footer rendering...")
        
        for email_address in self.footer_manager.contact_info.keys():
            print(f"\\n📧 Testing {{email_address}}:")
            
            # Test HTML footers
            for style in ["modern", "minimal", "corporate"]:
                try:
                    html_footer = self.footer_manager.generate_html_footer(email_address, style)
                    print(f"   ✅ HTML Footer ({{style}}) - Rendered successfully")
                except Exception as e:
                    print(f"   ❌ HTML Footer ({{style}}) - Error: {{e}}")
            
            # Test text footer
            try:
                text_footer = self.footer_manager.generate_text_footer(email_address)
                print(f"   ✅ Text Footer - Rendered successfully")
            except Exception as e:
                print(f"   ❌ Text Footer - Error: {{e}}")
            
            # Test signature block
            try:
                signature = self.footer_manager.generate_signature_block(email_address)
                print(f"   ✅ Signature Block - Rendered successfully")
            except Exception as e:
                print(f"   ❌ Signature Block - Error: {{e}}")
        
        print("\\n🎉 Footer rendering tests completed!")

def main():
    """Main entry point"""
    print("🚀 Starting Email Footer Implementation...")
    
    try:
        implementation = EmailFooterImplementation()
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "implement":
                implementation.implement_footers()
            elif command == "test":
                implementation.test_footer_rendering()
            else:
                print(f"❌ Unknown command: {{command}}")
        else:
            # Default: implement footers
            implementation.implement_footers()
            
    except Exception as e:
        logger.error(f"Implementation error: {{e}}")
        print(f"❌ Implementation failed: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        with open("implement_email_footers.py", "w") as f:
            f.write(script_content)

        logger.info(
            "Email footer implementation script created: implement_email_footers.py"
        )
        return script_content

    def display_footer_preview(self):
        """Display footer preview for all configured addresses"""
        logger.info("Displaying footer preview...")

        print("=" * 80)
        print("EMAIL FOOTER PREVIEW - COOLBITS.AI")
        print("=" * 80)
        print(f"Company: {self.company}")
        print(f"CEO: {self.ceo}")
        print("=" * 80)

        for email_address in self.contact_info.keys():
            contact = self.contact_info[email_address]

            print(f"\n📧 {email_address} - {contact.title}")
            print("-" * 60)

            # Display signature block
            signature = self.generate_signature_block(email_address)
            print("📝 Signature Block:")
            print(signature)

            # Display text footer (truncated)
            text_footer = self.generate_text_footer(email_address)
            print("📄 Text Footer (Preview):")
            print(text_footer[:200] + "..." if len(text_footer) > 200 else text_footer)

            print("-" * 60)

        print("=" * 80)
        print("✅ Footer preview completed")
        print("=" * 80)

    def run_complete_setup(self):
        """Run complete email footer setup"""
        logger.info("Running complete email footer setup...")

        print("=" * 80)
        print("🚀 COOLBITS.AI EMAIL FOOTER COMPLETE SETUP")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"🌐 Domain: {self.project_domain}")
        print(f"🤖 AI Domain: {self.cblm_domain}")
        print("=" * 80)

        # Display footer preview
        self.display_footer_preview()

        # Create templates
        self.create_footer_templates()

        # Generate CSS
        self.generate_footer_css()

        # Create implementation script
        self.create_footer_implementation_script()

        print("=" * 80)
        print("🎉 EMAIL FOOTER SETUP COMPLETED")
        print("=" * 80)
        print("📁 Generated Files:")
        print("• email_footer_templates.json")
        print("• email_footer_styles.css")
        print("• implement_email_footers.py")
        print("=" * 80)
        print("🚀 Next Steps:")
        print("1. Run: python implement_email_footers.py")
        print("2. Test footer rendering")
        print("3. Integrate with email system")
        print("4. Deploy to production")
        print("=" * 80)

        logger.info("Complete email footer setup finished successfully")


def main():
    """Main entry point"""
    print("🚀 Starting Email Footer Manager...")

    try:
        manager = CoolBitsEmailFooterManager()

        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == "preview":
                manager.display_footer_preview()
            elif command == "templates":
                manager.create_footer_templates()
            elif command == "css":
                manager.generate_footer_css()
            elif command == "script":
                manager.create_footer_implementation_script()
            else:
                print(f"❌ Unknown command: {command}")
        else:
            # Default: run complete setup
            manager.run_complete_setup()

    except Exception as e:
        logger.error(f"Setup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
