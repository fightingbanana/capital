import signal_generator
import random

# ===== CONFIGURATION =====
STARTING_CAPITAL = 100.0  # Change this for different bankrolls
POSITION_SIZE = 0.10      # 10% per trade
FEE_BINANCE = 0.001       # 0.1%
SPREAD_OANDA = 0.0005     # 0.05%
MAX_TRADES_TRACKED = 20   # Rolling accuracy window
BROKER_MAP = {
    "Binance": ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "AVAX-USD"],
    "OANDA": ["EURUSD=X", "GBPJPY=X", "USDJPY=X", "XAUUSD=X", "CL=F"]
}
# ==========================

last_results = []

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
        print(f"⚠️ Skipping invalid signal: {e}")
        return 0, False

    if signal == "HOLD":
        return 0, False

    trade_size = capital * POSITION_SIZE
    units = trade_size / price

    # Simulate win/loss
    win = random.random() < 0.6
    move_pct = random.uniform(0.01, 0.03)
    exit_price = price * (1 + move_pct if win else 1 - move_pct)
    pnl = (exit_price - price) * units
    gross_pnl = pnl

    # Broker fees
    if broker == "Binance":
        fee = trade_size * FEE_BINANCE * 2
    elif broker == "OANDA":
        fee = trade_size * SPREAD_OANDA * 2
    else:
        fee = 0.5

    net_pnl = gross_pnl - fee

    # Track win/loss
    last_results.append(win)
    if len(last_results) > MAX_TRADES_TRACKED:
        last_results.pop(0)

    accuracy = round((sum(last_results) / len(last_results)) * 100, 2)

    # 📬 Trade log
    print(f"\n✅ Executed {signal} for {symbol} at ${price}")
    print(f"📦 Size: €{round(trade_size, 2)} | Broker: {broker} | Fee: €{round(fee, 2)}")
    print(f"📉 Closed position at ${round(exit_price, 2)}")
    print(f"💸 PnL: {'+' if net_pnl >= 0 else ''}€{round(net_pnl, 2)} {'✅ WIN' if win else '❌ LOSS'}")
    print(f"📈 Strategy Accuracy (last {len(last_results)} trades): {accuracy}%")

    return net_pnl, win

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

    print("\n📈 SIMULATION COMPLETE")
    print(f"💰 Starting Capital: €{STARTING_CAPITAL}")
    print(f"🔁 Total Trades: {total_trades}")
    print(f"✅ Wins: {wins} | ❌ Losses: {losses}")
    print(f"📊 Win Rate: {round((wins / total_trades) * 100, 2)}%")
    print(f"📉 Total PnL: €{round(total_pnl, 2)}")
    print(f"🏁 Ending Capital: €{round(capital, 2)}")

if __name__ == "__main__":
    run_simulation()
