import json, time, sys
sys.path.insert(0, '.')
from str import set_milestone_status

with open('panel/state.json','r',encoding='utf-8') as f:
    s = json.load(f)

s['overall'] = 'HEALTHY'
s['updated_at'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
set_milestone_status('M16', s)
