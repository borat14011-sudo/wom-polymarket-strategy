#!/usr/bin/env python3
"""
Netlify Deploy Script for Wom's Trading Presentation
Run this to deploy to Netlify from your desktop
"""

import subprocess
import sys
import os

# Install netlify-cli if not present
print("📦 Checking for Netlify CLI...")
result = subprocess.run(["npm", "list", "-g", "netlify-cli"], capture_output=True, text=True)
if "netlify-cli" not in result.stdout:
    print("🔧 Installing Netlify CLI...")
    subprocess.run(["npm", "install", "-g", "netlify-cli"], check=True)
    print("✅ Netlify CLI installed")
else:
    print("✅ Netlify CLI already installed")

# Path to deploy folder
DEPLOY_FOLDER = r"C:\Users\Borat\.openclaw\workspace\netlify-deploy"

print(f"\n🚀 Deploying folder: {DEPLOY_FOLDER}")
print("📤 This will upload your presentation to Netlify...")

# Deploy using Netlify CLI
result = subprocess.run(
    ["netlify", "deploy", "--prod", "--dir", DEPLOY_FOLDER, "--open"],
    capture_output=False,
    text=True
)

if result.returncode == 0:
    print("\n✅ Deployment successful!")
else:
    print(f"\n❌ Deployment failed with code: {result.returncode}")
    print("You may need to login first: netlify login")
