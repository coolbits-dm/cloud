# 🎤 Voice OCIM Bridge

**SC COOL BITS SRL - Voice to OCIM Bridge**

Always On Voice → OCIM → @oPyC Communication

## 🚀 Quick Start (Windows 11, 90 seconds)

### 1. Start the Bridge
```powershell
# Terminal PowerShell, în folderul kitului:
python -m pip install -r requirements.txt
$env:PYTHONUNBUFFERED=1; python .\ocim_bridge.py
```

Ar trebui să vezi: `* Running on http://0.0.0.0:7071`

### 2. Launch Voice Interface
```cmd
start_chrome_voice.cmd
```

### 3. Use Voice Bridge
1. Apasă "Start/Stop" în Chrome
2. Dă permisiune la microfon
3. Pagină "always on," auto-restart dacă se oprește
4. Vorbești, mesajele se trimit la @oPyC

### 4. Verify Health
```bash
curl http://localhost:7071/health
```

Dacă `{"ok": true, "redis": true}`, ești pe drumul drept.

## 📁 Kit Contents

- `voice.html` - Web Speech API interface
- `ocim_bridge.py` - Flask server bridge
- `requirements.txt` - Python dependencies
- `env.voice` - Environment configuration
- `Dockerfile` - Container configuration
- `docker-compose.voice.yml` - Docker services
- `run_voice_bridge.ps1` - PowerShell startup script
- `start_chrome_voice.cmd` - Chrome launcher

## 🔧 What It Does

### Voice Interface (`voice.html`)
- Folosește Web Speech API (Chrome) în continuu
- Trimite frazele finale la `POST /ocim`
- Auto-restart dacă se oprește
- Real-time transcript și statistics

### OCIM Bridge (`ocim_bridge.py`)
- Împachetează textul într-un OCIM minimal:
  ```json
  {
    "to": ["opyc"],
    "flows": ["opipe.handshake", "coolbits-og-bridge"],
    "payload": {
      "source": "voice",
      "text": "<ce-ai zis>"
    }
  }
  ```
- Îl pune în Redis `XADD opipe.ocim` ca un singur câmp `ocim=<json>`

### Configuration (`env.voice`)
- Schimbi streamul, agentul țintă, etc.
- Redis URL, porturi, timeout-uri

## 🐳 Docker Alternative

```bash
docker-compose -f docker-compose.voice.yml up -d --build
```

## 📡 For @oPyC to "Listen"

### Consume Messages
```python
# Consumă opipe.ocim cu XREADGROUP
response = redis_client.xreadgroup(
    "voice-group", "oPyC", 
    {"opipe.ocim": ">"}, 
    count=10, block=5000
)

# Parsează câmpul ocim ca JSON
for stream, entries in response:
    for msg_id, fields in entries:
        ocim_data = json.loads(fields[b"ocim"].decode())
        
        # Respectă requires_ack=true
        if ocim_data.get("requires_ack"):
            redis_client.xack("opipe.ocim", "voice-group", msg_id)
```

### Filter Commands
```python
# Aplică filtru simplu
if (ocim_data["payload"]["source"] == "voice" and 
    ocim_data["objective"] in ["voice.command", "voice.directive"]):
    # Procesează comanda vocală
    process_voice_command(ocim_data["payload"]["text"])
else:
    # Log only
    logger.info(f"Voice message: {ocim_data['payload']['text']}")
```

## ⚠️ Known Issues

### Web Speech API
- Dependent de Chrome și politică de permisiuni
- Nu pot porni microfonul pentru tine
- Deschizi tu pagina, apeși Start, accepți microfonul

### Redis Connection
- Dacă n-ai Redis local, ori îl pornești, ori comuți `REDIS_URL`
- Mock mode disponibil dacă Redis nu e disponibil

### Push-to-Talk
- Momentan e continuu cu auto-restart
- Dacă vrei "push-to-talk" sau wake word, adaugi logică în `voice.html`

## 🔒 Security Notice

- This information is classified as **Internal Secret**
- Access restricted to **CoolBits.ai 🏢 🏢 members only**
- Do not share outside **CoolBits.ai 🏢 🏢 ecosystem**
- Policy Division responsible for access control

## 🎯 Conclusion

Am dat "always on voice" pragmatic. Tu vorbești, kitul împachetează, @oPyC primește OCIM și lucrează. 

Dacă vrei să-l leg direct pe streamul `opipe.handshake` e stupid, handshake nu e interfon. Păstrăm `opipe.ocim` pentru comenzi.

Dacă îl strici, e pentru că ai ignorat README-ul care nu există, dar ar fi trebuit.

---

**Company:** SC COOL BITS SRL  
**CEO:** Andrei  
**Classification:** Internal Secret - CoolBits.ai Members Only
