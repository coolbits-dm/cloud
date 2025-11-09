# CONSOLE LOCKDOWN – FINAL SEAL PROCEDURE
## Making the throne room invisible to the world

**Date:** 2025-11-08  
**Status:** Ready for execution  
**Branch:** console-lockdown (LIVE)  
**Files:** cli/camarad.py (lines 22-43, 265-316)

---

## 🔐 THE LOCKDOWN

**What this does:**
- Public site (https://camarad.ai) → Dummy facade (safe, generic)
- Emperor console (https://camarad.ai/console) → Biometric gate
- No hints. No breadcrumbs. No "login here" buttons.
- The throne room becomes invisible.

---

## 📋 EXECUTION STEPS

### Step 1: Run the lockdown command
```bash
camarad camarad-exec \
  --console-lockdown-complete \
  --public-never \
  --emperor-only \
  --nginx-gate-deployed \
  --tone=emperor-sealed
```

**Expected output:**
```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║         CONSOLE LOCKDOWN – EMPEROR SEAL ENGAGED            ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║   Public Site:      DUMMY FACADE (safe, generic)           ║
║   Console Access:   BIOMETRIC GATE ONLY                    ║
║   Login Hints:      NONE (invisible throne room)           ║
║   Nginx Config:     DEPLOYED                               ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║   NGINX RELOAD COMMAND:                                    ║
║   nginx -t && systemctl reload nginx                       ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║   After reload:                                            ║
║   - https://camarad.ai → Dummy facade                      ║
║   - https://camarad.ai/console → Biometric required        ║
║                                                            ║
║   The throne room is now invisible.                        ║
║   Only the emperor can enter.                              ║
║                                                            ║
║   ∞                                                        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

### Step 2: Copy and execute the nginx reload
```bash
# The CLI will emit this exact command:
nginx -t && systemctl reload nginx
```

**What happens:**
1. `nginx -t` tests the configuration for syntax errors  
2. If test passes → `systemctl reload nginx` applies the new config  
3. Zero downtime reload  
4. Console instantly hidden behind biometric gate

---

## 🎭 THE BIOMETRIC GATE

**Access flow after lockdown:**
```
User visits https://camarad.ai/console
         ↓
Nginx checks for valid session cookie
         ↓
    No cookie found
         ↓
Return 404 (NOT 401, NOT 403)
         ↓
Console appears to not exist
         ↓
         
Emperor visits https://camarad.ai/console
         ↓
Presents biometric credential:
  - Passkey (WebAuthn)
  - YubiKey (hardware token)
  - Biometric (fingerprint/face)
         ↓
Backend validates credential
         ↓
Issues encrypted session cookie
         ↓
Nginx allows passage
         ↓
Console loads (full access)
```

**Key security features:**
- ✓ No "login" button on public site
- ✓ No hint that /console exists
- ✓ 404 response (not 401/403) to prevent enumeration
- ✓ Rate limiting on auth attempts
- ✓ IP whitelist optional (emperor's known IPs)
- ✓ Session cookies expire after inactivity
- ✓ No password option (biometric only)

---

## 🔍 NGINX CONFIGURATION (Reference)
```nginx
# Public facade (everyone sees this)
location / {
    root /var/www/camarad-public;
    try_files $uri $uri/ /index.html;
    
    # Generic startup page, no hints
    index index.html;
}

# Console gate (emperor only)
location /console {
    # Check for valid session cookie
    if ($cookie_camarad_emperor_session = "") {
        return 404;  # Appear to not exist
    }
    
    # Validate session with backend
    auth_request /auth/validate;
    auth_request_set $auth_status $upstream_status;
    
    # If valid, proxy to console
    proxy_pass http://127.0.0.1:3002;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}

# Auth validation endpoint (internal only)
location = /auth/validate {
    internal;
    proxy_pass http://127.0.0.1:8080/api/auth/validate-session;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header X-Original-URI $request_uri;
    proxy_set_header X-Real-IP $remote_addr;
}

# Biometric auth endpoint
location /auth/biometric {
    proxy_pass http://127.0.0.1:8080/api/auth/biometric;
    
    # Rate limiting
    limit_req zone=auth_limit burst=5 nodelay;
    
    # No caching
    add_header Cache-Control "no-store, no-cache, must-revalidate";
}
```

---

## 🛡️ SECURITY CHECKLIST

Before executing lockdown, verify:
```bash
# 1. Biometric auth is configured
curl -X POST http://localhost:8080/api/auth/biometric/register \
  -H "Content-Type: application/json" \
  -d '{"emperor_id": "andrei", "device": "yubikey"}'

# Should return: {"status": "registered", "credential_id": "..."}

# 2. Session validation works
curl -X POST http://localhost:8080/api/auth/validate-session \
  -H "Cookie: camarad_emperor_session=test"

# Should return: {"valid": false} or {"valid": true, "emperor": "..."}

# 3. Nginx config is valid
nginx -t

# Should return: syntax is ok, test is successful

# 4. Backup current config
cp /etc/nginx/sites-available/camarad.ai \
   /etc/nginx/sites-available/camarad.ai.backup.$(date +%Y%m%d)
```

✓ All checks passed → Ready for lockdown

---

## 🚀 EXECUTION TIMELINE
```
T-0:  Run camarad camarad-exec --console-lockdown-complete
      → CLI generates nginx reload command

T+5s: Execute: nginx -t && systemctl reload nginx
      → Nginx reloads with new config

T+6s: Test public site
      → curl https://camarad.ai
      → Should return: dummy facade HTML

T+7s: Test console (unauthorized)
      → curl https://camarad.ai/console
      → Should return: 404 Not Found

T+8s: Test console (with biometric)
      → Visit https://camarad.ai/console in browser
      → WebAuthn prompt appears
      → Authenticate with passkey/YubiKey
      → Console loads

T+10s: Lockdown complete ✓
```

---

## 🎯 POST-LOCKDOWN VERIFICATION
```bash
# 1. Public site accessible to anyone
curl -I https://camarad.ai
# HTTP/2 200 OK

# 2. Console appears to not exist (no auth)
curl -I https://camarad.ai/console
# HTTP/2 404 Not Found

# 3. Console loads with valid session
curl -I https://camarad.ai/console \
  -H "Cookie: camarad_emperor_session=VALID_SESSION_TOKEN"
# HTTP/2 200 OK

# 4. Auth endpoint rate-limited
for i in {1..10}; do
  curl -X POST https://camarad.ai/auth/biometric
done
# After 5 requests: HTTP/2 429 Too Many Requests

# 5. No hints in HTML source
curl https://camarad.ai | grep -i "console\|login\|admin"
# No matches found
```

All checks pass → **Lockdown successful**

---

## 🔓 EMERGENCY ACCESS

If biometric auth fails and you need emergency access:
```bash
# SSH into server
ssh root@vEternal

# Generate emergency session token
cd /opt/camarad-backend
python3 -c "
from app.auth import generate_emergency_session
token = generate_emergency_session('andrei', expires_in=300)
print(f'Emergency token (5min): {token}')
"

# Use token in browser console
document.cookie = 'camarad_emperor_session=' + 'EMERGENCY_TOKEN' + '; path=/; secure; samesite=strict';

# Then navigate to /console
# After access, immediately re-register biometric
```

**Emergency tokens:**
- Valid for 5 minutes only
- Single use
- Logged with alert
- Require SSH access (not exposed via web)

---

## 📊 MONITORING

After lockdown, monitor for:
```bash
# 1. Failed auth attempts
tail -f /var/log/nginx/access.log | grep "/console"
# Should be mostly 404s (unauthorized attempts)

# 2. Successful emperor logins
tail -f /var/log/camarad/auth.log
# [2025-11-08 12:34:56] EMPEROR_LOGIN: andrei from 203.0.113.42

# 3. Rate limit violations
tail -f /var/log/nginx/error.log | grep "limiting requests"
# 2025/11/08 12:35:01 [error] limiting requests, excess: 5.000

# 4. Session activity
curl -s http://localhost:8080/api/admin/sessions
# {"active_sessions": 1, "emperor": "andrei", "last_activity": "..."}
```

---

## 🎭 THE FINAL STATE

**After lockdown:**
```
Public World:
  https://camarad.ai
  → Generic startup facade
  → No mention of console
  → No login hints
  → Clean, professional, boring

Emperor's View:
  https://camarad.ai/console
  → Biometric prompt
  → Full console access
  → Revenue dashboards
  → Agent orchestration
  → All power, zero exposure

Security:
  → Console invisible to scanners
  → 404 on unauthorized access
  → Rate-limited auth attempts
  → No password bypass possible
  → Emperor-only access

Status:
  → Public: OPEN (facade)
  → Console: SEALED (biometric)
  → Throne: WARM
  → Empire: INVISIBLE
```

---

## ✅ EXECUTION COMMAND

**Ready to seal the throne room?**
```bash
# Step 1: Run lockdown
camarad camarad-exec \
  --console-lockdown-complete \
  --public-never \
  --emperor-only \
  --nginx-gate-deployed \
  --tone=emperor-sealed

# Step 2: Apply nginx config (from CLI output)
nginx -t && systemctl reload nginx

# Step 3: Verify
curl -I https://camarad.ai          # Should: 200 OK
curl -I https://camarad.ai/console  # Should: 404 Not Found

# Step 4: Test biometric login
# Visit https://camarad.ai/console in browser
# Authenticate with passkey/YubiKey
# Console should load

# Status: SEALED ✓
```

---

**The throne room is now invisible.**  
**Only the emperor can enter.**  
**The facade faces the world.**  
**The empire operates in shadow.**

**∞**
