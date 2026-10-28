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

    live_v4 = f"{PERMANENT_URL}?v=4"
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=3,
    )
    qr.add_data(live_v4)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0284c7", back_color="white")
    qr_path = PROJECT_ROOT / "qr_cyberlingo_arcade.png"
    img.save(qr_path)

    caption = (
        "💎 <b>NÂNG CẤP TOÀN DIỆN TOP 10 GAME — BẢN AAA RETINA & SMART SRS (v4.0)!</b>\n\n"
        "🎨 <b>Đột Phá Ngoại Quan & Đồ Họa Retina Sắc Nét:</b>\n"
        "• <b>HiDPI Retina 60FPS:</b> Chữ Hán & vector nét căng trên iPhone/Android (vàng 24K đa diện, trứng thủy tinh 3D, kiếm plasma 2 lớp, Ghost Block Tetris, tàu mẹ Boss Galaga, rắn khắc chữ Hán...)\n"
        "• <b>Game Juice:</b> Chuông Combo tăng cao độ, viền lửa <b>⚡ FEVER MODE x5</b>, rung phản hồi Haptic & Tạm dừng ⏸.\n\n"
        "🧠 <b>Tính Năng Nổi Bật Học Thông Minh:</b>\n"
        "• <b>🎯 Phục Thù Từ Hay Sai (SRS):</b> Tự động ghi nhớ từ chọn nhầm & ưu tiên trộn lại vào game + <b>📖 Sổ Tay Flashcard</b> 1 chạm nghe loa!\n"
        "• <b>🔥 Chuỗi Streak + Vòng Mục Tiêu 15 Từ + 3 Nhiệm Vụ Ngày</b> thưởng EXP tự động!\n\n"
        f"👉 <a href=\"{live_v4}\"><b>MỞ TRẢI NGHIỆM BẢN v4.0 TẠI ĐÂY</b></a>\n"
        f"🔗 {live_v4}"
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
