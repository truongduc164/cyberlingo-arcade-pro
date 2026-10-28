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
        "🕹️ <b>CYBERLINGO SUPER ARCADE v2.0 — ĐÃ LÊN KỆ ĐỦ 8 GAME HUYỀN THOẠI!</b>\n\n"
        "🔥 <b>4 Siêu Phẩm Mới Cực Cuốn Vừa Ra Mắt:</b>\n"
        "1️⃣ <b>🥷 Fruit Ninja Chém Quả:</b> Quẹt kiếm ánh sáng chém đôi quả Chữ Hán đúng, né bom nổ!\n"
        "2️⃣ <b>🧱 Tetris Xếp Gạch Từ:</b> Thả khối Chữ Hán rơi trúng cột nghĩa Việt để nổ hàng & phá đá!\n"
        "3️⃣ <b>👻 Pac-Man Mê Cung:</b> Lượn mê cung ăn ngọc từ đúng để hóa Siêu Cấp nuốt ngược Ma QC!\n"
        "4️⃣ <b>🏐 Phá Gạch Arkanoid:</b> Đỡ bóng nảy phá tường gạch Chữ Hán & hứng viên nang nghĩa!\n\n"
        "🌟 <b>Cùng 4 Game Kinh Điển:</b> 🔗 Pikachu • 🔨 Đập Chuột • 🐍 Rắn Ghép Câu • 👾 Bắn Tàu Galaga\n"
        "🎖️ <i>Có thêm hệ thống Thăng Cấp EXP & 3 mức Tốc Độ (Thư giãn / Chuẩn / Cao thủ)!</i>\n\n"
        f"👉 <a href=\"{PERMANENT_URL}?v=2\"><b>BẤM VÀO ĐÂY ĐỂ CHƠI THỬ NGAY</b></a>\n"
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
