#!/usr/bin/env python3
"""
HolyGust Automated Deployment Script
1. Stages and commits all modified files (if commit message provided)
2. Pushes to GitHub (origin main)
3. Triggers Render Webhook Deploy Hook automatically
"""

import sys
import subprocess
import urllib.request
import time

DEPLOY_HOOK_URL = "https://api.render.com/deploy/srv-dbkeh6bl550s73e7bc20?key=EHNWyIz-rBY"

def run_command(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Command failed: {cmd}\n{res.stderr}")
        return False
    print(res.stdout.strip())
    return True

def trigger_render_deploy():
    print("Triggering Render cloud deployment...")
    try:
        req = urllib.request.Request(DEPLOY_HOOK_URL, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
            print(f"Deploy triggered successfully: {data}")
            return True
    except Exception as e:
        print(f"Failed to trigger Render deploy hook: {e}")
        return False

def main():
    commit_msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Auto deploy HolyGust updates"
    
    print("1. Pushing to GitHub (origin main)...")
    run_command("git add -A")
    run_command(f'git commit -m "{commit_msg}"')
    if not run_command("git push origin main"):
        print("Git push failed. Aborting deploy.")
        return

    print("2. Triggering Render live build...")
    trigger_render_deploy()
    print("3. Deployment initiated! Live in ~60-90 seconds at https://kiteapp.onrender.com")

if __name__ == "__main__":
    main()
