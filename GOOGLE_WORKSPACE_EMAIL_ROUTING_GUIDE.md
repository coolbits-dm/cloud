# Google Workspace Email Routing Setup - CoolBits.ai

## 📧 Overview

This guide provides step-by-step instructions to configure Google Workspace email routing for CoolBits.ai, redirecting all emails to `andrei@coolbits.ai`.

**Reference**: [Google Workspace Admin Help - Redirect or forward Gmail messages](https://support.google.com/a/answer/4524505?hl=en)

## 🏢 Company Information

- **Company**: COOL BITS SRL 🏢 🏢
- **CEO**: Andrei
- **Primary Email**: andrei@coolbits.ai
- **Customer ID**: C00tzrczu
- **Setup Date**: September 7, 2025

## 📋 Email Addresses to Route

### High Priority (Redirect)
- **andrei@coolbits.ro** → andrei@coolbits.ai (Primary CEO Email)

### High Priority (Forward)
- **coolbits.dm@gmail.com** → andrei@coolbits.ai (Official Administration Email)
- **coolbits.ro@gmail.com** → andrei@coolbits.ai (RO Headquarters Email)
- **coolbits.ai@gmail.com** → andrei@coolbits.ai (Brand Email)

## 🔧 Step-by-Step Configuration

### Step 1: Access Google Workspace Admin Console

1. Go to [https://admin.google.com](https://admin.google.com)
2. Sign in with `andrei@coolbits.ai`
3. Ensure you have **Super Admin** privileges

### Step 2: Navigate to Gmail Routing Settings

1. Click on **"Menu"** in the Admin Console
2. Go to **"Apps"** > **"Google Workspace"** > **"Gmail"**
3. Click on **"Routing"** (not "Default routing")
4. Select the **top-level organizational unit**

### Step 3: Configure Email Forwarding

1. Scroll down to **"Email forwarding using recipient address map"**
2. Click **"Configure"** or **"Add Another Rule"**
3. Enter descriptive name: **"CoolBits Email Routing"**

### Step 4: Add Address Mappings

For each email address, add the following mappings:

#### Mapping 1: andrei@coolbits.ro
- **Original Address**: `andrei@coolbits.ro`
- **Map To Address**: `andrei@coolbits.ai`
- **Action**: Redirect (exclude original recipient)

#### Mapping 2: coolbits.dm@gmail.com
- **Original Address**: `coolbits.dm@gmail.com`
- **Map To Address**: `andrei@coolbits.ai`
- **Action**: Forward (include original recipient)

#### Mapping 3: coolbits.ro@gmail.com
- **Original Address**: `coolbits.ro@gmail.com`
- **Map To Address**: `andrei@coolbits.ai`
- **Action**: Forward (include original recipient)

#### Mapping 4: coolbits.ai@gmail.com
- **Original Address**: `coolbits.ai@gmail.com`
- **Map To Address**: `andrei@coolbits.ai`
- **Action**: Forward (include original recipient)

### Step 5: Configure Routing Settings

Set the following options:

- **Messages to affect**: ✅ **All incoming messages**
- **Also route to original destination**: ✅ **Checked** (for forward actions)
- **Add X-Gm-Original-To header**: ✅ **Checked**
- **Apply to external only**: ❌ **Unchecked**

### Step 6: Save Configuration

1. Review all address mappings
2. Click **"Save"** at the bottom of the configuration
3. Wait for changes to propagate (up to 24 hours)

## 📊 Bulk Configuration (Alternative)

If you prefer bulk configuration, you can use the generated CSV file:

1. Download `email_routing_bulk_mapping.csv`
2. In Admin Console, click **"Bulk Add"**
3. Copy and paste the CSV content
4. Click **"Add aliases"**

## 🧪 Testing Configuration

### Test Email Template

Send test emails to each configured address to verify routing:

```
Subject: CoolBits.ai Email Routing Test - [DATE]

Dear Andrei,

This is a test email to verify email routing configuration for CoolBits.ai.

Test Details:
- Company: COOL BITS SRL
- Primary Email: andrei@coolbits.ai
- Test Time: [TIMESTAMP]
- Routing Action: Forward/Redirect to primary email

If you receive this email, the routing configuration is working correctly.

Best regards,
@oGoogleWorkspace Email Router
CoolBits.ai Email Management System
```

### Verification Steps

1. Send test email to `andrei@coolbits.ro`
2. Send test email to `coolbits.dm@gmail.com`
3. Send test email to `coolbits.ro@gmail.com`
4. Send test email to `coolbits.ai@gmail.com`
5. Verify all emails are received at `andrei@coolbits.ai`

## 🔒 Security & Compliance

### Access Control
- **Authorized Users**: @Andrei, @oOutlook only
- **Classification**: Internal Secret - CoolBits.ai Members Only
- **Security Level**: Maximum
- **Compliance**: GDPR compliant

### Monitoring
- All email operations logged
- Routing operations monitored
- Access restricted to authorized personnel

## 📈 Forwarding Limits

Based on Google Workspace limits:
- **Maximum forwarding operations**: 30 million in 24-hour period
- **Rate limit**: 600k per 1-minute window
- **Address map limit**: 5,000 recipient addresses maximum

## 🚨 Troubleshooting

### Common Issues

1. **Changes not taking effect**
   - Wait up to 24 hours for propagation
   - Check Admin Console for error messages

2. **Emails not routing**
   - Verify address mappings are correct
   - Check routing settings configuration
   - Ensure proper permissions

3. **Duplicate emails**
   - Check "Also route to original destination" setting
   - Verify forward vs redirect actions

### Support Resources

- [Google Workspace Admin Help](https://support.google.com/a/answer/4524505?hl=en)
- Google Workspace Support Team
- CoolBits.ai Technical Support

## 📁 Generated Files

- `google_workspace_address_maps.json` - Complete address mapping configuration
- `admin_console_setup_steps.json` - Detailed setup instructions
- `email_routing_bulk_mapping.csv` - Bulk configuration file
- `test_email_routing.py` - Testing script

## ✅ Success Criteria

- ✅ All email addresses configured in Google Workspace Admin Console
- ✅ Address mappings created and saved
- ✅ Routing settings configured correctly
- ✅ Test emails successfully routed to andrei@coolbits.ai
- ✅ Monitoring and logging enabled

---

**Classification**: Internal Secret - CoolBits.ai Members Only  
**Last Updated**: September 7, 2025  
**Updated by**: @oGoogleWorkspace Email Router
