import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import json
from pathlib import Path
from datetime import datetime

API_URL = "https://call2.tgju.org/ajax.json"
DATA_FILE = Path("prices.json")
UPDATE_INTERVAL = 60000  # 60 ثانیه

ASSETS = {
    "dollar": {"key": "price_dollar_rl", "name": "💵 دلار", "unit": "ریال"},
    "euro": {"key": "price_eur", "name": "💶 یورو", "unit": "ریال"},
    "bitcoin": {"key": "crypto-bitcoin", "name": "₿ بیت کوین", "unit": "دلار"},
    "gold": {"key": "mesghal", "name": "🟡 مثقال طلا", "unit": "ریال"},
    "coin": {"key": "sekee", "name": "🪙 سکه", "unit": "ریال"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tgju.org"
}


class PriceApp:

    def __init__(self, root):
        self.root = root
        self.root.title("قیمت لحظه‌ای بازار")
        self.root.geometry("700x500")
        self.root.configure(bg="#1e1e1e")

        title = tk.Label(
            root,
            text="📈 نمایش لحظه‌ای قیمت‌ها",
            font=("Tahoma", 18, "bold"),
            bg="#1e1e1e",
            fg="white"
        )
        title.pack(pady=15)

        self.cards_frame = tk.Frame(root, bg="#1e1e1e")
        self.cards_frame.pack(fill="both", expand=True, padx=20)

        self.cards = {}

        for asset in ASSETS:
            frame = tk.Frame(
                self.cards_frame,
                bg="#2d2d2d",
                relief="raised",
                bd=1
            )
            frame.pack(fill="x", pady=5)

            name_lbl = tk.Label(
                frame,
                text=ASSETS[asset]["name"],
                font=("Tahoma", 12, "bold"),
                bg="#2d2d2d",
                fg="white"
            )
            name_lbl.pack(side="left", padx=15)

            price_lbl = tk.Label(
                frame,
                text="---",
                font=("Consolas", 12),
                bg="#2d2d2d",
                fg="white"
            )
            price_lbl.pack(side="right", padx=15)

            self.cards[asset] = price_lbl

        self.status_label = tk.Label(
            root,
            text="در انتظار دریافت اطلاعات...",
            bg="#1e1e1e",
            fg="#bbbbbb",
            font=("Tahoma", 10)
        )
        self.status_label.pack(pady=10)

        ttk.Button(
            root,
            text="بروزرسانی دستی",
            command=self.update_prices
        ).pack(pady=10)

        self.update_prices()

    def fetch_prices(self):

        response = requests.get(
            API_URL,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        payload = response.json()
        current = payload["current"]

        result = {}

        for asset_id, meta in ASSETS.items():
            item = current[meta["key"]]

            result[asset_id] = {
                "price": item["p"],
                "change": float(item.get("dp", 0)),
                "direction": item.get("dt", "")
            }

        return result

    def save_prices(self, data):
        DATA_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def refresh_ui(self, data):

        for asset, info in data.items():

            direction = info["direction"]

            if direction == "high":
                color = "#4CAF50"
                arrow = "▲"

            elif direction == "low":
                color = "#F44336"
                arrow = "▼"

            else:
                color = "white"
                arrow = "•"

            self.cards[asset].config(
                text=f"{info['price']} {arrow} {info['change']}%",
                fg=color
            )

        self.status_label.config(
            text=f"آخرین بروزرسانی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def update_prices(self):

        def worker():
            try:
                data = self.fetch_prices()
                self.save_prices(data)

                self.root.after(
                    0,
                    lambda: self.refresh_ui(data)
                )

            except Exception as e:
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "خطا",
                        str(e)
                    )
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

        self.root.after(
            UPDATE_INTERVAL,
            self.update_prices
        )


if __name__ == "__main__":
    root = tk.Tk()

    style = ttk.Style()
    style.theme_use("clam")

    app = PriceApp(root)

    root.mainloop()