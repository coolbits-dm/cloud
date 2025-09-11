#!/bin/bash
# Complete Google & AI Services Setup Commands for CoolBits.ai
# Generated: 2025-09-07T13:04:29.631879

# PROJECT_SETUP
gcloud config set project coolbits-ai
gcloud config set compute/region europe-west3

# APIS_ENABLE
gcloud services enable gmail.googleapis.com
gcloud services enable admin.googleapis.com
gcloud services enable calendar.googleapis.com
gcloud services enable tasks.googleapis.com
gcloud services enable docs.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable generativelanguage.googleapis.com
gcloud services enable customsearch.googleapis.com
gcloud services enable youtube.googleapis.com
gcloud services enable androidpublisher.googleapis.com
gcloud services enable googleads.googleapis.com
gcloud services enable chromewebstore.googleapis.com
gcloud services enable content.googleapis.com
gcloud services enable maps.googleapis.com

# SERVICE_ACCOUNTS_CREATE
gcloud iam service-accounts create coolbits-gmail-service --display-name='CoolBits Gmail Service Account'
gcloud iam service-accounts create coolbits-workspace-service --display-name='CoolBits Workspace Service Account'
gcloud iam service-accounts create coolbits-calendar-service --display-name='CoolBits Calendar Service Account'
gcloud iam service-accounts create coolbits-tasks-service --display-name='CoolBits Tasks Service Account'
gcloud iam service-accounts create coolbits-docs-service --display-name='CoolBits Docs Service Account'
gcloud iam service-accounts create coolbits-sheets-service --display-name='CoolBits Sheets Service Account'
gcloud iam service-accounts create coolbits-gemini-service --display-name='CoolBits Gemini Service Account'
gcloud iam service-accounts create coolbits-ogemini-service --display-name='CoolBits oGemini Service Account'
gcloud iam service-accounts create coolbits-cblm-service --display-name='CoolBits cbLM Service Account'
gcloud iam service-accounts create coolbits-platform-service --display-name='CoolBits Platform Service Account'

# API_KEYS_CREATE
gcloud services api-keys create --display-name='CoolBits Gmail API Key' --api-target=service=gmail.googleapis.com
gcloud services api-keys create --display-name='CoolBits Calendar API Key' --api-target=service=calendar.googleapis.com
gcloud services api-keys create --display-name='CoolBits Gemini API Key' --api-target=service=generativelanguage.googleapis.com
gcloud services api-keys create --display-name='CoolBits Maps API Key' --api-target=service=maps.googleapis.com

