#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOUD PAGES PUBLISHER — CYBERLINGO ARCADE PRO (DEAN OPTIMIZE)
=============================================================
Publishes static PWA `cyberlingo_arcade/` to 24/7 GitHub Pages:
  👉 https://truongduc164.github.io/cyberlingo-arcade/
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
WEB_DIR = PROJECT_ROOT / "cyberlingo_arcade"
DEPLOY_DIR = PROJECT_ROOT / ".gh_pages_deploy"
REPO_NAME = "cyberlingo-arcade"
PERMANENT_URL = f"https://truongduc164.github.io/{REPO_NAME}/"


def get_github_creds():
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    creds = dict(
        line.split("=", 1)
        for line in proc.stdout.splitlines()
        if "=" in line
    )
    return creds.get("username", "truongduc164"), creds.get("password", "")


def ensure_public_pages_repo(user: str, pat: str):
    headers = {
        "Authorization": f"token {pat}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.get(f"https://api.github.com/repos/{user}/{REPO_NAME}", headers=headers, timeout=15)
    if r.status_code == 404:
        cr = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json={
                "name": REPO_NAME,
                "description": "CyberLingo Arcade PRO — 4 Classic Chinese Voice Reflex Games (Static PWA Client) by DEAN OPTIMIZE",
                "private": False,
                "has_issues": False,
                "has_projects": False,
                "has_wiki": False,
            },
            timeout=20,
        )
        cr.raise_for_status()
        print(f"[Pages] Created static client repo: https://github.com/{user}/{REPO_NAME}")

    return headers


def publish():
    user, pat = get_github_creds()
    assert pat, "Missing GitHub credentials in Windows Credential Manager"
    headers = ensure_public_pages_repo(user, pat)

    remote_url = f"https://github.com/{user}/{REPO_NAME}.git"
    if DEPLOY_DIR.exists():
        shutil.rmtree(DEPLOY_DIR)
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)

    for item in WEB_DIR.iterdir():
        dst = DEPLOY_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)
    (DEPLOY_DIR / ".nojekyll").write_text("", encoding="utf-8")

    def git(args):
        res = subprocess.run(
            ["git", "-C", str(DEPLOY_DIR)] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if res.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {res.stderr}")
        return res

    git(["init", "-b", "main"])
    git(["config", "user.name", user])
    git(["config", "user.email", f"{user}@users.noreply.github.com"])
    git(["add", "-A"])
    git(["commit", "-m", "deploy: CyberLingo Arcade PRO v1.0 static client"])
    git(["remote", "add", "origin", remote_url])
    git(["push", "--force", "origin", "main"])
    print(f"[Pages] Pushed static client to {remote_url}")

    # Enable GitHub Pages on branch main / root
    pages_api = f"https://api.github.com/repos/{user}/{REPO_NAME}/pages"
    pr = requests.get(pages_api, headers=headers, timeout=15)
    if pr.status_code == 404:
        en = requests.post(
            pages_api,
            headers=headers,
            json={"source": {"branch": "main", "path": "/"}},
            timeout=15,
        )
        print(f"[Pages] Enabled GitHub Pages: HTTP {en.status_code}")

    # Poll until GitHub Pages CDN serves HTTP 200
    print(f"[Pages] Waiting for CDN activation at {PERMANENT_URL} ...")
    for attempt in range(24):
        try:
            resp = requests.get(PERMANENT_URL, timeout=10)
            if resp.status_code == 200 and "CYBERLINGO ARCADE" in resp.text:
                print(f"[Pages] LIVE 200 OK at {PERMANENT_URL} ({len(resp.content)} bytes)!")
                return PERMANENT_URL
        except Exception:
            pass
        time.sleep(4)
    print(f"[Pages] Deployed; CDN propagation may take ~30s: {PERMANENT_URL}")
    return PERMANENT_URL


if __name__ == "__main__":
    publish()
