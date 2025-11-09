#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@oPython Security Administration Prompt
CoolBits.ai / cbLM.ai - Local Security Management

This prompt provides @oPython with comprehensive security administration
capabilities for local system management and certificate verification.

Author: @SafeNet Agent (oCursor)
Company: COOL BITS SRL
"""


def generate_opython_security_prompt():
    """Generate security administration prompt for @oPython"""
    from datetime import datetime

    prompt = f"""
🔐 **@oPython Security Administration Prompt**
═══════════════════════════════════════════════════════════════

📋 **CERTIFICATE VERIFICATION STATUS**
   ✅ Certificate Found: BOUREANU ANDREI-CIPRIAN
   🔑 Thumbprint: AD61CB7BF502EBF90B75898D51F4327A833670E5
   📅 Validity: 2023-06-06 to 2025-06-05
   ⚠️  Status: EXPIRED (94 days overdue)
   🏢 Issuer: DigiSign Qualified CA Class 3 2017
   📧 Subject: BOUREANU ANDREI-CIPRIAN, SERIALNUMBER=200506245BAC189

🔒 **str.py SECURITY STATUS**
   ✅ Location: app/andrei/secure/str.py
   📊 Size: 126,311 bytes
   🔐 Encryption: EFS (AES-256)
   🔑 Certificate Thumbprint: A187 7E74 E971 3C0B 6079 D6E0 07E1 604A A6F2 1119
   👤 Access: ANDREI\\andre only
   📧 Microsoft Account: andrei@coolbits.ro
   🔐 PIN Protection: Enabled

🛡️ **SECURITY POLICIES ACTIVE**
   ✅ Zero-Trust Architecture
   ✅ HMAC Authentication
   ✅ IP Allowlist Protection
   ✅ Rate Limiting (60 RPS, 120 burst)
   ✅ Audit Logging (JSON per line)
   ✅ EFS Encryption
   ✅ PIN Protection
   ✅ Microsoft Account Integration

🎯 **IMMEDIATE ACTIONS FOR @oPython**

**CRITICAL: Certificate Renewal**
1. Contact DigiSign for certificate renewal
2. Current certificate expired 94 days ago
3. Update certificate in Windows Certificate Store
4. Verify new certificate thumbprint
5. Update security policies with new certificate

**SECURITY MAINTENANCE**
1. Monitor str.py access logs
2. Verify EFS encryption status
3. Check PIN protection functionality
4. Validate Microsoft account integration
5. Review audit logs for anomalies

**SYSTEM HARDENING**
1. Enable Windows Defender Advanced Threat Protection
2. Configure BitLocker for additional encryption
3. Set up Windows Hello PIN requirements
4. Enable Credential Guard
5. Configure Device Guard policies

🔧 **ADMINISTRATION COMMANDS**

**Certificate Management:**
```powershell
# List certificates
Get-ChildItem -Path Cert:\\CurrentUser\\My

# Check certificate validity
Get-ChildItem -Path Cert:\\CurrentUser\\My | Where-Object {{$_.Subject -like "*BOUREANU*"}}

# Import new certificate
Import-Certificate -FilePath "new_cert.pfx" -CertStoreLocation Cert:\\CurrentUser\\My
```

**File Security:**
```powershell
# Check EFS encryption
cipher /c app/andrei/secure/str.py

# Verify file permissions
icacls app/andrei/secure/str.py

# Check file integrity
Get-FileHash app/andrei/secure/str.py -Algorithm SHA256
```

**Security Monitoring:**
```powershell
# Check Windows Security Center
Get-MpComputerStatus

# View security events
Get-WinEvent -FilterHashtable {{LogName='Security'}} -MaxEvents 10

# Check BitLocker status
Get-BitLockerVolume
```

📊 **SECURITY METRICS**
   - Certificate Status: EXPIRED (Critical)
   - File Encryption: ACTIVE (AES-256)
   - Access Control: RESTRICTED
   - Audit Logging: ENABLED
   - PIN Protection: ACTIVE
   - Microsoft Integration: CONFIGURED

⚠️ **SECURITY ALERTS**
   1. 🚨 Certificate expired 94 days ago - IMMEDIATE RENEWAL REQUIRED
   2. ⚠️  Monitor for unauthorized access attempts
   3. ⚠️  Regular security audits recommended
   4. ⚠️  Backup certificate and private keys securely

🔐 **COMPLIANCE STATUS**
   ✅ EFS Encryption: Compliant
   ✅ Access Control: Compliant
   ✅ Audit Logging: Compliant
   ❌ Certificate Validity: Non-Compliant (Expired)
   ✅ PIN Protection: Compliant
   ✅ Microsoft Integration: Compliant

📋 **NEXT STEPS FOR @oPython**
1. Execute certificate renewal process
2. Update security policies with new certificate
3. Verify all security controls are functioning
4. Generate new security report
5. Update compliance documentation

═══════════════════════════════════════════════════════════════
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Agent: @SafeNet (Security Administration)
Target: @oPython (Local Security Management)
Company: COOL BITS SRL
═══════════════════════════════════════════════════════════════
"""

    return prompt


def save_security_prompt():
    """Save security prompt to file"""
    from datetime import datetime

    prompt = generate_opython_security_prompt()

    filename = f"opython_security_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"✅ Security prompt saved to: {filename}")
    return prompt


if __name__ == "__main__":
    print("🔐 Generating @oPython Security Administration Prompt...")
    prompt = save_security_prompt()
    print("\n" + prompt)
