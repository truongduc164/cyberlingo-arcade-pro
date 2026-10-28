#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOUD PAGES PUBLISHER — CYBERLINGO ARCADE PRO (DEAN OPTIMIZE)
=============================================================
Publishes static PWA `cyberlingo_arcade/` to 24/7 GitHub Pages:
  👉 https://truongduc164.github.io/cyberlingo-arcade/
"""

import shutil
import stat
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


def _force_rm_readonly(func, path, _):
    Path(path).chmod(stat.S_IWRITE)
    func(path)


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
                "description": "CyberLingo Arcade PRO — 8 Classic Chinese Voice Reflex Games (Static PWA Client) by DEAN OPTIMIZE",
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
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)

    # Clean non-.git files inside DEPLOY_DIR
    for child in DEPLOY_DIR.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child, onexc=_force_rm_readonly)
        else:
            child.chmod(stat.S_IWRITE)
            child.unlink()

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

    if not (DEPLOY_DIR / ".git").exists():
        git(["init", "-b", "main"])
        git(["remote", "add", "origin", remote_url])
    else:
        git(["remote", "set-url", "origin", remote_url])

    git(["config", "user.name", user])
    git(["config", "user.email", f"{user}@users.noreply.github.com"])
    git(["add", "-A"])
    status = git(["status", "--short"]).stdout.strip()
    if status:
        git(["commit", "-m", "deploy: CyberLingo Arcade PRO v3.0 (Top 10 Definitive Classics)"])
        git(["push", "--force", "origin", "main"])
        print(f"[Pages] Pushed v2.0 update to {remote_url}")
    else:
        print("[Pages] Already up-to-date on GitHub Pages")

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

    return PERMANENT_URL


if __name__ == "__main__":
    publish()
