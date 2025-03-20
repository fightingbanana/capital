import signal_generator
import random

# ===== CONFIGURATION =====
STARTING_CAPITAL = 100.0  # 💸 You can change this to simulate more/less money
POSITION_SIZE = 0.10      # % of capital per trade (e.g. 0.10 = 10%)
FEE_BINANCE = 0.001       # 0.1% fee
SPREAD_OANDA = 0.0005     # Simulated OANDA spread (0.05%)
BROKER_MAP = {
    "Binance": ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "AVAX-USD"],
    "OANDA": ["EURUSD=X", "GBPJPY=X", "USDJPY=X", "XAUUSD=X", "CL=F"]
}
# ==========================

def get_broker(symbol):
    for broker, assets in BROKER_MAP.items():
        if symbol in assets:
            return broker
    return "Unknown"

def simulate_trade(signal_data, capital):
    lines = signal_data.split("\n")
    try:
        signal = lines[0].split(":")[1].strip().split()[1]
        symbol = lines[1].split(":")[1].strip()
        price = float(lines[4].split(":")[1].strip().replace("$", ""))
        broker = get_broker(symbol)
    except Exception as e:
        print(f"Skipping invalid signal: {e}")
        return 0, False

    if signal == "HOLD":
        return 0, False

    trade_size = capital * POSITION_SIZE
    units = trade_size / price

    # Simulate win or loss (randomized for now, later we’ll use real price move data)
    win = random.random() < 0.6  # 60% win rate assumption
    move_pct = random.uniform(0.01, 0.03)  # Simulate 1%–3% price moves
    pnl = units * price * move_pct
    pnl = pnl if win else -pnl

    # Deduct broker fees
    if broker == "Binance":
        fee = trade_size * FEE_BINANCE * 2  # entry + exit
    elif broker == "OANDA":
        fee = trade_size * SPREAD_OANDA * 2
    else:
        fee = 0.5  # fallback

    net_result = pnl - fee
    return net_result, win

def run_simulation():
    capital = STARTING_CAPITAL
    total_trades = 0
    wins = 0
    losses = 0
    total_pnl = 0

    all_assets = BROKER_MAP["Binance"] + BROKER_MAP["OANDA"]

    for asset in all_assets:
        signal = signal_generator.get_signal(asset)
        result, win = simulate_trade(signal, capital)
        if result != 0:
            total_trades += 1
            capital += result
            total_pnl += result
            if win:
                wins += 1
            else:
                losses += 1

    print("📈 SIMULATION COMPLETE")
    print(f"💰 Starting Capital: €{STARTING_CAPITAL}")
    print(f"🔁 Total Trades: {total_trades}")
    print(f"✅ Wins: {wins} | ❌ Losses: {losses}")
    print(f"📊 Win Rate: {round((wins / total_trades) * 100, 2)}%")
    print(f"📉 Total PnL: €{round(total_pnl, 2)}")
    print(f"🏁 Ending Capital: €{round(capital, 2)}")

if __name__ == "__main__":
    run_simulation()
