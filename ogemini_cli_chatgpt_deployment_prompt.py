#!/usr/bin/env python3
"""
oGeminiCLI - ChatGPT Integration Deployment Prompt
Complete console message for deploying ChatGPT integration to Google Cloud
"""

from datetime import datetime


def generate_gemini_cli_chatgpt_prompt():
    """Generate complete oGeminiCLI prompt for ChatGPT integration deployment"""

    print("=" * 80)
    print("🤖 OGEMINICLI - CHATGPT INTEGRATION DEPLOYMENT PROMPT")
    print("=" * 80)
    print("Company: COOL BITS SRL")
    print("CEO: Andrei")
    print("Date: 2025-09-07")
    print("=" * 80)

    prompt = f"""
🤖 oGeminiCLI - Deploy ChatGPT Integration to Google Cloud

Company: COOL BITS SRL
CEO: Andrei
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Project: coolbits-ai
Region: europe-west3

🤖 CHATGPT INTEGRATION - DEPLOY TO GOOGLE CLOUD

✅ INTEGRATION DETAILS REGISTERED:
• Platform: ChatGPT
• Provider: OpenAI
• Repository: coolbits-dm/cloud
• Environment: coolbits-dm/cloud
• Installation Status: Installed
• Git Status: On Git
• Classification: Internal Secret - CoolBits.ai Members Only
• Integration Date: 2025-09-07
• Status: Officially Integrated

🔐 GOOGLE CLOUD SECRETS TO CREATE:

1. chatgpt-integration-status
   Value: "ChatGPT - OpenAI integration for coolbits-dm/cloud"
   Description: "ChatGPT integration status"
   Classification: "Internal Secret - CoolBits.ai Members Only"
   
   Command:
   echo "ChatGPT - OpenAI integration for coolbits-dm/cloud" | gcloud secrets create chatgpt-integration-status --data-file=- --project=coolbits-ai --labels="owner=andrei_cip,platform=chatgpt,status=integrated"

2. chatgpt-repository-info
   Value: "coolbits-dm/cloud - ChatGPT installed and on Git"
   Description: "ChatGPT repository information"
   Classification: "Internal Secret - CoolBits.ai Members Only"
   
   Command:
   echo "coolbits-dm/cloud - ChatGPT installed and on Git" | gcloud secrets create chatgpt-repository-info --data-file=- --project=coolbits-ai --labels="owner=andrei_cip,platform=chatgpt,status=repository"

3. chatgpt-environment-config
   Value: "coolbits-dm/cloud environment configuration"
   Description: "ChatGPT environment configuration"
   Classification: "Internal Secret - CoolBits.ai Members Only"
   
   Command:
   echo "coolbits-dm/cloud environment configuration" | gcloud secrets create chatgpt-environment-config --data-file=- --project=coolbits-ai --labels="owner=andrei_cip,platform=chatgpt,status=environment"

4. chatgpt-classification
   Value: "Internal Secret - CoolBits.ai Members Only"
   Description: "ChatGPT security classification"
   Classification: "Internal Secret - CoolBits.ai Members Only"
   
   Command:
   echo "Internal Secret - CoolBits.ai Members Only" | gcloud secrets create chatgpt-classification --data-file=- --project=coolbits-ai --labels="owner=andrei_cip,platform=chatgpt,status=classification"

👥 IAM ROLES TO CREATE:

1. chatgpt_admin
   Role Name: "ChatGPT Administrator"
   Description: "ChatGPT - ChatGPT Administrator - OpenAI integration for coolbits-dm/cloud"
   Permissions: ["chatgpt.admin", "chatgpt.read", "chatgpt.write"]
   
   Command:
   gcloud iam roles create chatgpt_admin --project=coolbits-ai --title="ChatGPT Administrator" --description="ChatGPT - ChatGPT Administrator - OpenAI integration for coolbits-dm/cloud" --permissions="chatgpt.admin,chatgpt.read,chatgpt.write"

2. chatgpt_operator
   Role Name: "ChatGPT Operator"
   Description: "ChatGPT - ChatGPT Operator - OpenAI integration for coolbits-dm/cloud"
   Permissions: ["chatgpt.operator", "chatgpt.read", "chatgpt.write"]
   
   Command:
   gcloud iam roles create chatgpt_operator --project=coolbits-ai --title="ChatGPT Operator" --description="ChatGPT - ChatGPT Operator - OpenAI integration for coolbits-dm/cloud" --permissions="chatgpt.operator,chatgpt.read,chatgpt.write"

3. chatgpt_viewer
   Role Name: "ChatGPT Viewer"
   Description: "ChatGPT - ChatGPT Viewer - OpenAI integration for coolbits-dm/cloud"
   Permissions: ["chatgpt.viewer", "chatgpt.read"]
   
   Command:
   gcloud iam roles create chatgpt_viewer --project=coolbits-ai --title="ChatGPT Viewer" --description="ChatGPT - ChatGPT Viewer - OpenAI integration for coolbits-dm/cloud" --permissions="chatgpt.viewer,chatgpt.read"

🔐 IAM PERMISSIONS TO ASSIGN:

Assign ChatGPT roles to existing users:

1. Assign chatgpt_admin to bogdan.boureanu@gmail.com:
   gcloud projects add-iam-policy-binding coolbits-ai --member="user:bogdan.boureanu@gmail.com" --role="projects/coolbits-ai/roles/chatgpt_admin"

2. Assign chatgpt_operator to bogdan.boureanu@gmail.com:
   gcloud projects add-iam-policy-binding coolbits-ai --member="user:bogdan.boureanu@gmail.com" --role="projects/coolbits-ai/roles/chatgpt_operator"

3. Assign chatgpt_viewer to bogdan.boureanu@gmail.com:
   gcloud projects add-iam-policy-binding coolbits-ai --member="user:bogdan.boureanu@gmail.com" --role="projects/coolbits-ai/roles/chatgpt_viewer"

📜 ORGANIZATION POLICIES TO UPDATE:

1. Update coolbits-dm/cloud/policy with ChatGPT integration:
   Policy: coolbits-dm/cloud/policy
   Content: Include "ChatGPT - OpenAI integration for coolbits-dm/cloud (Internal Secret)"
   Classification: Internal Secret - CoolBits.ai Members Only

2. Update coolbits-dm/cloud/policy-manager with ChatGPT integration:
   Policy: coolbits-dm/cloud/policy-manager
   Content: Include "ChatGPT - OpenAI integration for coolbits-dm/cloud (Internal Secret)"
   Classification: Internal Secret - CoolBits.ai Members Only

3. Update coolbits.ai/policy with ChatGPT integration:
   Policy: coolbits.ai/policy
   Content: Include "ChatGPT - OpenAI integration for coolbits-dm/cloud (Internal Secret)"
   Classification: Internal Secret - CoolBits.ai Members Only

4. Update coolbits.ai/policy-manager with ChatGPT integration:
   Policy: coolbits.ai/policy-manager
   Content: Include "ChatGPT - OpenAI integration for coolbits-dm/cloud (Internal Secret)"
   Classification: Internal Secret - CoolBits.ai Members Only

🔒 SECURITY CLASSIFICATION:

• Access Level: Internal Secret - CoolBits.ai Members Only
• Restrictions: 
  - Do not share outside CoolBits.ai ecosystem
  - Access restricted to CoolBits.ai members only
  - Policy Division responsible for access control
• Policy Division: oGrok08 (CISO) + oGrok09 (CAIO)

📋 DEPLOYMENT CHECKLIST:

✅ Create Google Cloud secrets (4 secrets)
✅ Create IAM roles (3 roles)
✅ Assign IAM permissions to existing users
✅ Update organization policies (4 policies)
✅ Verify security classification
✅ Test access controls
✅ Document deployment results

🎯 EXPECTED RESULTS:

After deployment, the following should be available in Google Cloud:
• 4 ChatGPT secrets in Secret Manager
• 3 ChatGPT IAM roles
• IAM permissions assigned to existing users
• 4 updated organization policies
• Complete ChatGPT integration in Google Cloud

📁 REFERENCE FILES:

• chatgpt_integration_complete.json - Complete integration data
• str.py - Updated with chatgpt_info() function

🔐 SECURITY NOTICE:

This deployment involves Internal Secret classification.
All ChatGPT information is restricted to CoolBits.ai members only.
Do not share outside CoolBits.ai ecosystem.
Policy Division (oGrok08 CISO + oGrok09 CAIO) responsible for access control.

🤖 oGeminiCLI - Execute this deployment to Google Cloud for ChatGPT integration.

Company: COOL BITS SRL | CEO: Andrei | Date: {datetime.now().strftime("%Y-%m-%d")}
"""

    return prompt


def save_prompt_to_file():
    """Save the prompt to a file for easy access"""

    prompt = generate_gemini_cli_chatgpt_prompt()

    # Save to file
    with open("ogemini_cli_chatgpt_deployment_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print("📁 Prompt saved to: ogemini_cli_chatgpt_deployment_prompt.txt")
    print("🤖 Ready for oGeminiCLI deployment!")


def main():
    """Main function to generate oGeminiCLI prompt"""

    print("🤖 GENERATING OGEMINICLI CHATGPT DEPLOYMENT PROMPT")
    print("=" * 60)

    # Generate and display prompt
    prompt = generate_gemini_cli_chatgpt_prompt()
    print(prompt)

    # Save to file
    save_prompt_to_file()

    print("\n🎯 PROMPT READY FOR OGEMINICLI!")
    print("Copy the prompt above and send to oGeminiCLI for Google Cloud deployment")


if __name__ == "__main__":
    main()
