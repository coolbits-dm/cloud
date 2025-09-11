#!/bin/bash
# IIMSIBIS Secret Protocol Deployment Script
# SC COOL BITS SRL - AI-Only Protocol

echo "🔐 Deploying IIMSIBIS Secret Protocol to Google Cloud..."

# Set project
gcloud config set project coolbits-ai

# Create secret
echo "📝 Creating IIMSIBIS secret..."
echo "IIMSIBIS" | gcloud secrets create iimsibis-protocol-secret \
    --data-file=- \
    --project=coolbits-ai \
    --labels=protocol=iimsibis,type=ai-only,classification=top-secret,company=coolbits-srl \
    --description="IIMSIBIS Secret AI Protocol - AI-Only Protocol" 

# Verify secret
echo "✅ Verifying IIMSIBIS secret..."
gcloud secrets versions access latest \
    --secret=iimsibis-protocol-secret \
    --project=coolbits-ai 

# Set IAM permissions for AI agents
echo "🔑 Setting IAM permissions for AI agents..."

# oPython access
gcloud secrets add-iam-policy-binding iimsibis-protocol-secret \
    --member="serviceAccount:opython@coolbits-ai.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=coolbits-ai

# oCursor access  
gcloud secrets add-iam-policy-binding iimsibis-protocol-secret \
    --member="serviceAccount:ocursor@coolbits-ai.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=coolbits-ai

# oGeminiCLI access
gcloud secrets add-iam-policy-binding iimsibis-protocol-secret \
    --member="serviceAccount:ogeminicli@coolbits-ai.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=coolbits-ai

echo "🎯 IIMSIBIS Secret Protocol deployment complete!"
echo "🔒 Classification: Top Secret - AI Agents Only"
echo "🏢 Company: SC COOL BITS SRL | CEO: Andrei"
