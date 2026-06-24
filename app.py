import requests
import time
import os
from threading import Thread
from flask import Flask

# --- Flask Web Server Setup (Para sa Render Free Tier) ---
app = Flask('')

@app.route('/')
def home():
    return "Gold Sniper Bot is Alive and Scanning 24/7!"

def run_web_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- Iyong Bot Configuration ---
TOKEN = "8894597120:AAGJ7p5YrFFgiBAzz_fuUH-wZ-MHYwaxnyQ"
CHAT_ID = "6110929945"
URL = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"

def send_telegram_alert(message):
    try:
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(telegram_url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
    except Exception as e:
        print("Telegram delivery failed:", e)

def calculate_rsi(price_list, period=10):
    if len(price_list) < period + 1: return 50.0
    gains, losses = [], []
    for i in range(1, len(price_list)):
        diff = price_list[i] - price_list[i-1]
        if diff > 0: gains.append(diff); losses.append(0)
        else: gains.append(0); losses.append(abs(diff))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

# --- Ang Pangunahing Makina ng Bot ---
def bot_loop():
    print("=== GOLD SOLID SCALPER V8 CLOUD ENGINE STARTED ===")
    send_telegram_alert("📡 *Gold Solid Scalper V8 Cloud Engine Online*\nRunning 24/7 on Render Cloud Server!")
    
    prices = []
    bot_state = "SCANNING"
    total_trades = 0
    wins = 0

    while True:
        try:
            response = requests.get(URL, timeout=5).json()
            price = float(response['price'])
            
            prices.append(price)
            if len(prices) > 10: prices.pop(0)

            if len(prices) == 10:
                sma = sum(prices) / 10
                variance = sum((x - sma) ** 2 for x in prices) / 10
                std_dev = variance ** 0.5 if variance > 0 else 0.20
                if std_dev < 0.25: std_dev = 0.25
                
                lower_band = sma - (1.5 * std_dev)
                rsi = calculate_rsi(prices, 10)
                win_rate_pct = (wins / total_trades * 100) if total_trades > 0 else 100.0

                print(f"[{bot_state}] Gold Price: ${price:,.2f} | RSI: {rsi:.1f} | WinRate: {win_rate_pct:.1f}%")

                if bot_state == "SCANNING":
                    if price <= lower_band and rsi <= 38.0:
                        msg = (
                            "🟩🟩🟩🟩🟩🟩🟩🟩🟩\n"
                            "🟢 *SOLID GOLD CLOUD SIGNAL* 🟢\n"
                            "🟩🟩🟩🟩🟩🟩🟩🟩🟩\n\n"
                            f"📊 *BOT WIN RATE:* {win_rate_pct:.1f}%\n"
                            f"🎯 *Entry Zone:* At or below ${price:,.2f}\n"
                            f"• Take Profit: ${price + (1.2 * std_dev):,.2f}\n"
                            f"• Stop Loss: ${price - (0.8 * std_dev):,.2f}\n"
                        )
                        send_telegram_alert(msg)
                        bot_state = "IN_TRADE"
                        entry_price = price
                        tp_price = price + (1.2 * std_dev)
                        sl_price = price - (0.8 * std_dev)

                elif bot_state == "IN_TRADE":
                    if price >= tp_price:
                        total_trades += 1
                        wins += 1
                        send_telegram_alert("🏆 *TAKE PROFIT TARGET HIT ON CLOUD!* 💰")
                        bot_state = "SCANNING"
                    elif price <= sl_price:
                        total_trades += 1
                        send_telegram_alert("🛑 *STOP LOSS HIT ON CLOUD* 📉")
                        bot_state = "SCANNING"

            time.sleep(5)
        except Exception as e:
            print("Loop error:", e)
            time.sleep(5)

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.start()
    run_web_server()
  
