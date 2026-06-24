import requests
import time
import os
from threading import Thread
from flask import Flask

# --- Flask Web Server Setup (Para sa Render Free Tier) ---
app = Flask('')

@app.route('/')
def home():
    return "Gold Sniper Rectangle Bot is Live and Scanning 1M Candles!"

def run_web_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Configuration ---
TOKEN = "8894597120:AAGJ7p5YrFFgiBAzz_fuUH-wZ-MHYwaxnyQ"
CHAT_ID = "6110929945"
# Gagamit na tayo ng Klines endpoint para sa 1-Minute Candlesticks
URL = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=1m&limit=20"

def send_telegram_alert(message):
    try:
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(telegram_url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
    except Exception as e:
        print("Telegram delivery failed:", e)

# --- Ang Pangunahing Makina ng Bot (Rectangle Strategy Engine) ---
def bot_loop():
    print("=== GOLD RECTANGLE SNIPER ENGINE STARTED ===")
    send_telegram_alert("📡 *Gold Rectangle Sniper Engine Online*\nStrategy Updated: 1M Candle Wick Rejection & Breakout!")
    
    bot_state = "SCANNING"
    # Target Variables para sa Trade Tracking
    entry_target = 0
    tp_target = 0
    sl_target = 0
    trade_type = "" # "LONG" o "SHORT"

    while True:
        try:
            # Kumuha ng Candlestick Data mula sa Binance
            response = requests.get(URL, timeout=5).json()
            
            # Ayusin ang format ng kandila (Open, High, Low, Close)
            candles = []
            for c in response:
                candles.append({
                    'open': float(c[1]),
                    'high': float(c[2]),
                    'low': float(c[3]),
                    'close': float(c[4])
                })
            
            # Siguraduhing sapat ang data
            if len(candles) < 15:
                time.sleep(10)
                continue

            current_price = candles[-1]['close']

            if bot_state == "SCANNING":
                # Pinakahuling saradong kandila (Candle -2) ang gagamiting batayan ng Rectangle
                trigger_candle = candles[-2]
                past_candles = candles[-12:-2] # Nakaraang 10 kandila para sa market structure
                
                highest_past = max(x['high'] for x in past_candles)
                lowest_past = min(x['low'] for x in past_candles)

                # 1. BEARISH SETUP (Short/Sell Signal)
                # Tingnan kung umabot sa bagong High (Liquidity Sweep) at nag-iwan ng mahabang mitsa sa itaas (Weakness)
                is_local_high = trigger_candle['high'] >= highest_past
                upper_wick = trigger_candle['high'] - max(trigger_candle['open'], trigger_candle['close'])
                body_size_bear = abs(trigger_candle['close'] - trigger_candle['open'])
                
                if is_local_high and upper_wick > (body_size_bear * 1.2) and upper_wick > 0.10:
                    # Ang parihaba ay mula sa tuktok ng katawan hanggang sa dulo ng mitsa
                    rectangle_bottom = max(trigger_candle['open'], trigger_candle['close'])
                    
                    # Sniper Entry Trigger: Kung ang kasalukuyang kandila ay sumira pababa sa parihaba
                    if current_price < rectangle_bottom:
                        risk = trigger_candle['high'] - current_price
                        if risk > 0.10: # Iwasan ang sobrang liliit na galaw
                            bot_state = "IN_TRADE"
                            trade_type = "SHORT"
                            entry_target = current_price
                            sl_target = trigger_candle['high'] + 0.10 # Stop Loss sa dulo ng mitsa
                            tp_target = current_price - (risk * 3.0)  # Solid 3:1 Reward Risk Ratio
                            
                            msg = (
                                "🟥🟥🟥🟥🟥🟥🟥🟥🟥\n"
                                "🎯 *RECTANGLE SNIPER SHORT* 🎯\n"
                                "🟥🟥🟥🟥🟥🟥🟥🟥🟥\n\n"
                                f"💡 *Reason:* Upper Wick Rejection at Local High (Weakness Confirmed)\n\n"
                                f"📉 *Entry Price:* ${entry_target:,.2f}\n"
                                f"🛑 *Stop Loss:* ${sl_target:,.2f}\n"
                                f"🏆 *Take Profit (3:1 RR):* ${tp_target:,.2f}\n"
                            )
                            send_telegram_alert(msg)

                # 2. BULLISH SETUP (Long/Buy Signal)
                # Tingnan kung umabot sa bagong Low (Anchored) at nag-iwan ng mahabang mitsa sa ibaba (Weakness)
                is_local_low = trigger_candle['low'] <= lowest_past
                lower_wick = min(trigger_candle['open'], trigger_candle['close']) - trigger_candle['low']
                body_size_bull = abs(trigger_candle['close'] - trigger_candle['open'])

                if is_local_low and lower_wick > (body_size_bull * 1.2) and lower_wick > 0.10:
                    # Ang parihaba ay mula sa ilalim ng katawan hanggang sa dulo ng mitsa sa ibaba
                    rectangle_top = min(trigger_candle['open'], trigger_candle['close'])
                    
                    # Sniper Entry Trigger: Kung ang kasalukuyang kandila ay sumira pataas sa parihaba
                    if current_price > rectangle_top:
                        risk = current_price - trigger_candle['low']
                        if risk > 0.10:
                            bot_state = "IN_TRADE"
                            trade_type = "LONG"
                            entry_target = current_price
                            sl_target = trigger_candle['low'] - 0.10  # Stop Loss sa dulo ng mitsa sa ibaba
                            tp_target = current_price + (risk * 3.0)   # Solid 3:1 Reward Risk Ratio
                            
                            msg = (
                                "🟩🟩🟩🟩🟩🟩🟩🟩🟩\n"
                                "🎯 *RECTANGLE SNIPER LONG* 🎯\n"
                                "🟩🟩🟩🟩🟩🟩🟩🟩🟩\n\n"
                                f"💡 *Reason:* Lower Wick Rejection at Local Low (Weakness Confirmed)\n\n"
                                f"📈 *Entry Price:* ${entry_target:,.2f}\n"
                                f"🛑 *Stop Loss:* ${sl_target:,.2f}\n"
                                f"🏆 *Take Profit (3:1 RR):* ${tp_target:,.2f}\n"
                            )
                            send_telegram_alert(msg)

            elif bot_state == "IN_TRADE":
                # Pagsubaybay sa kasalukuyang takbo ng posisyon
                if trade_type == "SHORT":
                    if current_price <= tp_target:
                        send_telegram_alert(f"🏆 *TAKE PROFIT TARGET HIT!* 💰\nGold reached ${current_price:,.2f} (3:1 RR Reward Secured!)")
                        bot_state = "SCANNING"
                    elif current_price >= sl_target:
                        send_telegram_alert(f"🛑 *STOP LOSS HIT* 📉\nPosition closed at ${current_price:,.2f} to protect capital.")
                        bot_state = "SCANNING"
                        
                elif trade_type == "LONG":
                    if current_price >= tp_target:
                        send_telegram_alert(f"🏆 *TAKE PROFIT TARGET HIT!* 💰\nGold reached ${current_price:,.2f} (3:1 RR Reward Secured!)")
                        bot_state = "SCANNING"
                    elif current_price <= sl_target:
                        send_telegram_alert(f"🛑 *STOP LOSS HIT* 📉\nPosition closed at ${current_price:,.2f} to protect capital.")
                        bot_state = "SCANNING"

            # Mag-scan bawat 10 segundo para laging huli sa galaw ng 1M candle
            time.sleep(10)
            
        except Exception as e:
            print("Strategy loop error:", e)
            time.sleep(10)

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.start()
    run_web_server()
            
