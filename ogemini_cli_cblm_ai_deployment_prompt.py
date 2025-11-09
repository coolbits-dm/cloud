#!/usr/bin/env python3
"""
oGeminiCLI - cblm.ai Google Cloud Deployment Prompt
Complete console message for deploying cblm.ai official registration to Google Cloud
"""

from datetime import datetime


def generate_gemini_cli_prompt():
    """Generate complete oGeminiCLI prompt for cblm.ai Google Cloud deployment"""

    print("=" * 80)
    print("🤖 OGEMINICLI - CBLM.AI GOOGLE CLOUD DEPLOYMENT PROMPT")
    print("=" * 80)
    print("Company: COOL BITS SRL")
    print("CEO: Andrei")
    print("Date: 2025-09-07")
    print("=" * 80)

    prompt = f"""
🤖 oGeminiCLI - Deploy cblm.ai Official Registration to Google Cloud

Company: COOL BITS SRL
CEO: Andrei
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Project: coolbits-ai
Region: europe-west3

📝 CBLM.AI OFFICIAL REGISTRATION - DEPLOY TO GOOGLE CLOUD

✅ OFFICIAL DEFINITION REGISTERED:
• Acronym: cblm.ai
• Full Name: Code Based Language Model
• Internal Name: cool bits Language Model
• Internal Acronym: cb
• Classification: Internal Secret - CoolBits.ai Members Only
• Registration Date: 2025-09-07
• Status: Officially Registered

🔐 GOOGLE CLOUD SECRETS TO CREATE:

1. cblm-ai-definition
   Value: "cblm.ai - Code Based Language Model"
   Description: "cblm.ai official definition"
   Classification: "Internal Secret - CoolBits.ai Members Only"
   
   Command:
   echo "cblm.ai - Code Based Language Model" | gcloud secrets create cblm-ai-definition --data-file=- --project=coolbits-ai --labels="owner=andrei_cip,platform=cblm_ai,status=official"

2. cblm-ai-internal
   Value: "cool bits Language Model (cb)"
   Description: "cblm.ai internal definition"
   Classification: "Internal Secret - CoolBits.ai Members Only"
   
   Command:
   echo "cool bits Language Model (cb)" | gcloud secrets create cblm-ai-internal --data-file=- --project=coolbits-ai --labels="owner=andrei_cip,platform=cblm_ai,status=internal"

3. cblm-ai-classification
   Value: "Internal Secret - CoolBits.ai Members Only"
   Description: "cblm.ai security classification"
   Classification: "Internal Secret - CoolBits.ai Members Only"
   
   Command:
   echo "Internal Secret - CoolBits.ai Members Only" | gcloud secrets create cblm-ai-classification --data-file=- --project=coolbits-ai --labels="owner=andrei_cip,platform=cblm_ai,status=classification"

👥 IAM ROLES TO CREATE:

1. cblm_ai_admin
   Role Name: "cblm.ai Administrator"
   Description: "cblm.ai - cblm.ai Administrator - Code Based Language Model (Internal: cool bits Language Model)"
   Permissions: ["cblm.ai.admin", "cblm.ai.read", "cblm.ai.write"]
   
   Command:
   gcloud iam roles create cblm_ai_admin --project=coolbits-ai --title="cblm.ai Administrator" --description="cblm.ai - cblm.ai Administrator - Code Based Language Model (Internal: cool bits Language Model)" --permissions="cblm.ai.admin,cblm.ai.read,cblm.ai.write"

2. cblm_ai_operator
   Role Name: "cblm.ai Operator"
   Description: "cblm.ai - cblm.ai Operator - Code Based Language Model (Internal: cool bits Language Model)"
   Permissions: ["cblm.ai.operator", "cblm.ai.read", "cblm.ai.write"]
   
   Command:
   gcloud iam roles create cblm_ai_operator --project=coolbits-ai --title="cblm.ai Operator" --description="cblm.ai - cblm.ai Operator - Code Based Language Model (Internal: cool bits Language Model)" --permissions="cblm.ai.operator,cblm.ai.read,cblm.ai.write"

3. cblm_ai_viewer
   Role Name: "cblm.ai Viewer"
   Description: "cblm.ai - cblm.ai Viewer - Code Based Language Model (Internal: cool bits Language Model)"
   Permissions: ["cblm.ai.viewer", "cblm.ai.read"]
   
   Command:
   gcloud iam roles create cblm_ai_viewer --project=coolbits-ai --title="cblm.ai Viewer" --description="cblm.ai - cblm.ai Viewer - Code Based Language Model (Internal: cool bits Language Model)" --permissions="cblm.ai.viewer,cblm.ai.read"

🔐 IAM PERMISSIONS TO ASSIGN:

Assign cblm.ai roles to existing users:

1. Assign cblm_ai_admin to bogdan.boureanu@gmail.com:
   gcloud projects add-iam-policy-binding coolbits-ai --member="user:bogdan.boureanu@gmail.com" --role="projects/coolbits-ai/roles/cblm_ai_admin"

2. Assign cblm_ai_operator to bogdan.boureanu@gmail.com:
   gcloud projects add-iam-policy-binding coolbits-ai --member="user:bogdan.boureanu@gmail.com" --role="projects/coolbits-ai/roles/cblm_ai_operator"

3. Assign cblm_ai_viewer to bogdan.boureanu@gmail.com:
   gcloud projects add-iam-policy-binding coolbits-ai --member="user:bogdan.boureanu@gmail.com" --role="projects/coolbits-ai/roles/cblm_ai_viewer"

📜 ORGANIZATION POLICIES TO UPDATE:

1. Update coolbits.ai/policy with cblm.ai definition:
   Policy: coolbits.ai/policy
   Content: Include "cblm.ai - Code Based Language Model (Internal: cool bits Language Model)"
   Classification: Internal Secret - CoolBits.ai Members Only

2. Update coolbits.ai/policy-manager with cblm.ai definition:
   Policy: coolbits.ai/policy-manager
   Content: Include "cblm.ai - Code Based Language Model (Internal: cool bits Language Model)"
   Classification: Internal Secret - CoolBits.ai Members Only

3. Update cblm.ai/policy with cblm.ai definition:
   Policy: cblm.ai/policy
   Content: Include "cblm.ai - Code Based Language Model (Internal: cool bits Language Model)"
   Classification: Internal Secret - CoolBits.ai Members Only

4. Update cblm.ai/policy-manager with cblm.ai definition:
   Policy: cblm.ai/policy-manager
   Content: Include "cblm.ai - Code Based Language Model (Internal: cool bits Language Model)"
   Classification: Internal Secret - CoolBits.ai Members Only

🔒 SECURITY CLASSIFICATION:

• Access Level: Internal Secret - CoolBits.ai Members Only
• Restrictions: 
  - Do not share outside CoolBits.ai ecosystem
  - Access restricted to CoolBits.ai members only
  - Policy Division responsible for access control
• Policy Division: oGrok08 (CISO) + oGrok09 (CAIO)

📋 DEPLOYMENT CHECKLIST:

✅ Create Google Cloud secrets (3 secrets)
✅ Create IAM roles (3 roles)
✅ Assign IAM permissions to existing users
✅ Update organization policies (4 policies)
✅ Verify security classification
✅ Test access controls
✅ Document deployment results

🎯 EXPECTED RESULTS:

After deployment, the following should be available in Google Cloud:
• 3 cblm.ai secrets in Secret Manager
• 3 cblm.ai IAM roles
• IAM permissions assigned to existing users
• 4 updated organization policies
• Complete cblm.ai official registration in Google Cloud

📁 REFERENCE FILES:

• cblm_ai_official_registration.json - Complete registration data
• CBLM_AI_OFFICIAL_REGISTRATION_COMPLETE.md - Full documentation
• str.py - Updated with cblm_ai_info() function

🔐 SECURITY NOTICE:

This deployment involves Internal Secret classification.
All cblm.ai information is restricted to CoolBits.ai members only.
Do not share outside CoolBits.ai ecosystem.
Policy Division (oGrok08 CISO + oGrok09 CAIO) responsible for access control.

🤖 oGeminiCLI - Execute this deployment to Google Cloud for cblm.ai official registration.

Company: COOL BITS SRL | CEO: Andrei | Date: {datetime.now().strftime("%Y-%m-%d")}
"""

    return prompt


def save_prompt_to_file():
    """Save the prompt to a file for easy access"""

    prompt = generate_gemini_cli_prompt()

    # Save to file
    with open("ogemini_cli_cblm_ai_deployment_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print("📁 Prompt saved to: ogemini_cli_cblm_ai_deployment_prompt.txt")
    print("🤖 Ready for oGeminiCLI deployment!")


def main():
    """Main function to generate oGeminiCLI prompt"""

    print("🤖 GENERATING OGEMINICLI DEPLOYMENT PROMPT")
    print("=" * 60)

    # Generate and display prompt
    prompt = generate_gemini_cli_prompt()
    print(prompt)

    # Save to file
    save_prompt_to_file()

    print("\n🎯 PROMPT READY FOR OGEMINICLI!")
    print("Copy the prompt above and send to oGeminiCLI for Google Cloud deployment")


if __name__ == "__main__":
    main()
