# Secure str.py redirector - PIN required
# This file redirects to the secure version in app/andrei/secure/str.py

import sys
import os

# Redirect to secure version
secure_path = os.path.join(os.path.dirname(__file__), "app", "andrei", "secure", "str.py")
if os.path.exists(secure_path):
    with open(secure_path, 'r', encoding='utf-8') as f:
        exec(f.read())
else:
    print("Secure str.py not found. Please check file path.")