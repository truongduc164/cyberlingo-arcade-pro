#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys
from pathlib import Path
import qrcode
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
PERMANENT_URL = "https://truongduc164.github.io/cyberlingo-arcade/"


def load_telegram_creds():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if token and chat_id:
        return token, chat_id

    shared_cfg = PROJECT_ROOT.parent / "23. CyberBird-Lingo-Game" / "telegram_video_hub" / "config.json"
    if shared_cfg.exists():
        data = json.loads(shared_cfg.read_text(encoding="utf-8"))
        return data.get("bot_token", ""), data.get("chat_id", "")
    return "", ""


def main():
    token, chat_id = load_telegram_creds()
    if not token or not chat_id:
        print("Missing Telegram credentials")
        return

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=3,
    )
    qr.add_data(PERMANENT_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#7c3aed", back_color="white")
    qr_path = PROJECT_ROOT / "qr_cyberlingo_arcade.png"
    img.save(qr_path)

    caption = (
        "🕹️ <b>CYBERLINGO ARCADE LAB v1.0 — 4 GAME KINH ĐIỂN LỒNG TIẾNG TRUNG!</b>\n\n"
        "✨ <b>Chạm thử ngay 4 chế độ giải trí phản xạ tiếng Trung:</b>\n"
        "1️⃣ <b>🔗 Pikachu Nối Từ:</b> Chạm ô nghe phát âm, nối cặp Chữ Hán ↔ Nghĩa Việt.\n"
        "2️⃣ <b>🔨 Đập Chuột Nghe Ý:</b> Ẩn mặt chữ, nghe giọng đọc chuẩn đập nhanh nghĩa đúng.\n"
        "3️⃣ <b>🐍 Rắn Săn Ghép Câu:</b> Lái rắn ăn đúng thứ tự từng cụm từ chuẩn ngữ pháp.\n"
        "4️⃣ <b>👾 Bắn Tàu Đấu Boss:</b> Kéo tàu bắn hạ từ đúng & đấu Boss Xưởng Trưởng!\n\n"
        "🔄 <i>Tự động đồng bộ chung kho bài học AI 17:30 hằng ngày từ CyberBird!</i>\n\n"
        f"👉 <a href=\"{PERMANENT_URL}\"><b>BẤM VÀO ĐÂY ĐỂ CHƠI THỬ NGAY</b></a>\n"
        f"🔗 {PERMANENT_URL}"
    )

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(qr_path, "rb") as f:
        r = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
            files={"photo": ("qr_cyberlingo_arcade.png", f, "image/png")},
            timeout=30,
        )
    res = r.json()
    if res.get("ok"):
        print(f"✅ Sent CyberLingo Arcade QR & link to Telegram (Msg ID: {res['result']['message_id']})")
    else:
        print("Telegram send error:", res)


if __name__ == "__main__":
    main()
