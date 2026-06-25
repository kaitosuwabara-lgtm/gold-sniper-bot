import requests
import time
import os
from threading import Thread
from flask import Flask

# --- Flask Web Server Setup (Para sa Render Free Tier) ---
app = Flask('')

@app.route('/')
def home():
    return "Gold Smart Market Structure Bot is Online and Scanning!"

def run_web_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Configuration ---
TOKEN = "8894597120:AAGJ7p5YrFFgiBAzz_fuUH-wZ-MHYwaxnyQ"
CHAT_ID = "6110929945"
URL = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=1m&limit=50"

def send_telegram_alert(message):
    try:
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(telegram_url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
    except Exception as e:
        print("Telegram delivery failed:", e)

# --- Algorithmic Core (Smart Market Structure Engine) ---
def bot_loop():
    print("=== GOLD LUX-STYLE ENGINE STARTED ===")
    send_telegram_alert("📡 *Gold Smart Structure Engine Online*\nIndicator Active: Supply/Demand Zones + CHoCH + Buy/Sell Overlays!")
    
    bot_state = "SCANNING"
    entry_target = 0
    tp_target = 0
    sl_target = 0
    trade_type = ""

    while True:
        try:
            response = requests.get(URL, timeout=5).json()
            
            if not isinstance(response, list) or len(response) < 30:
                time.sleep(10)
                continue
            
            candles = []
            for c in response:
                candles.append({
                    'open': float(c[1]),
                    'high': float(c[2]),
                    'low': float(c[3]),
                    'close': float(c[4])
                })
            
            current_price = candles[-1]['close']

            if bot_state == "SCANNING":
                # 1. Supply & Demand Zones (Nakaraang 25 kandila)
                lookback_candles = candles[-26:-1]
                supply_zone = max(x['high'] for x in lookback_candles)  # Pulang Box
                demand_zone = min(x['low'] for x in lookback_candles)    # Berdeng Box
                
                # 2. Smooth Trend Line for CHoCH confirmation
                short_ma = sum(x['close'] for x in candles[-10:-1]) / 9
                
                last_candle = candles[-2]
                prev_candle = candles[-3]
                
                # 🟥 AUTOMATED SELL SIGNAL (Supply Zone + Bearish Crossover)
                if last_candle['high'] >= (supply_zone - 0.20) and prev_candle['close'] > short_ma and last_candle['close'] < short_ma:
                    risk = supply_zone - current_price
                    if risk > 0.15:
                        bot_state = "IN_TRADE"
                        trade_type = "SHORT"
                        entry_target = current_price
                        sl_target = supply_zone + 0.15  # SL sa itaas ng Supply Zone
                        tp_target = current_price - (risk * 2.5)  # 2.5:1 Risk Reward
                        
                        msg = (
                            "🟥🟥🟥🟥🟥🟥🟥🟥🟥\n"
                            "🎯 *LUX SMART SIGNAL: SELL* 🎯\n"
                            "🟥🟥🟥🟥🟥🟥🟥🟥🟥\n\n"
                            f"🛡️ *Market Context:* Price rejected at Supply Zone (${supply_zone:,.2f})\n"
                            f"⚡ *Trigger:* Bearish CHoCH / Market Structure Shift Confirmed\n\n"
                            f"📉 *Entry Price:* ${entry_target:,.2f}\n"
                            f"🛑 *Stop Loss:* ${sl_target:,.2f}\n"
                            f"🏆 *Take Profit:* ${tp_target:,.2f}\n"
                        )
                        send_telegram_alert(msg)

                # 🟩 AUTOMATED BUY SIGNAL (Demand Zone + Bullish Crossover)
                elif last_candle['low'] <= (demand_zone + 0.20) and prev_candle['close'] < short_ma and last_candle['close'] > short_ma:
                    risk = current_price - demand_zone
                    if risk > 0.15:
                        bot_state = "IN_TRADE"
                        trade_type = "LONG"
                        entry_target = current_price
                        sl_target = demand_zone - 0.15  # SL sa ilalim ng Demand Zone
                        tp_target = current_price + (risk * 2.5)  # 2.5:1 Risk Reward
                        
                        msg = (
                            "🟩🟩🟩🟩🟩🟩🟩🟩🟩\n"
                            "🎯 *LUX SMART SIGNAL: BUY* 🎯\n"
                            "🟩🟩🟩🟩🟩🟩🟩🟩🟩\n\n"
                            f"🛡️ *Market Context:* Price supported at Demand Zone (${demand_zone:,.2f})\n"
                            f"⚡ *Trigger:* Bullish CHoCH / Market Structure Shift Confirmed\n\n"
                            f"📈 *Entry Price:* ${entry_target:,.2f}\n"
                            f"🛑 *Stop Loss:* ${sl_target:,.2f}\n"
                            f"🏆 *Take Profit:* ${tp_target:,.2f}\n"
                        )
                        send_telegram_alert(msg)

            elif bot_state == "IN_TRADE":
                if trade_type == "SHORT":
                    if current_price <= tp_target:
                        send_telegram_alert(f"🏆 *SMART TAKE PROFIT HIT!* 💰\nGold successfully dropped to ${current_price:,.2f}!")
                        bot_state = "SCANNING"
                    elif current_price >= sl_target:
                        send_telegram_alert(f"🛑 *SMART STOP LOSS HIT* 📉\nClosed at ${current_price:,.2f} to protect capital.")
                        bot_state = "SCANNING"
                        
                elif trade_type == "LONG":
                    if current_price >= tp_target:
                        send_telegram_alert(f"🏆 *SMART TAKE PROFIT HIT!* 💰\nGold successfully surged to ${current_price:,.2f}!")
                        bot_state = "SCANNING"
                    elif current_price <= sl_target:
                        send_telegram_alert(f"🛑 *SMART STOP LOSS HIT* 📉\nClosed at ${current_price:,.2f} to protect capital.")
                        bot_state = "SCANNING"

            time.sleep(10)
            
        except Exception as e:
            print("Engine running error:", e)
            time.sleep(10)

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.start()
    run_web_server()
          
