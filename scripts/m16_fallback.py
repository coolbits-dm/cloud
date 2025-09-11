import json, time, subprocess, os
p = "panel/state.json"
with open(p,"r",encoding="utf-8") as f: s=json.load(f)
s["milestone"]="M16"; s["overall"]="HEALTHY"; s["updated_at"]=time.strftime("%Y-%m-%dT%H:%M:%S%z")
with open(p,"w",encoding="utf-8") as f: json.dump(s,f,ensure_ascii=False,indent=2)
os.makedirs("panel", exist_ok=True)
sha = subprocess.run(["git","rev-parse","HEAD"], capture_output=True, text=True).stdout.strip()
with open("panel/gates.jsonl","a",encoding="utf-8") as f:
    f.write(json.dumps({"ts":s["updated_at"],"milestone":"M16","overall":"HEALTHY","sha":sha},ensure_ascii=False)+"\n")
