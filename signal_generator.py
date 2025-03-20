import yfinance as yf
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np

# Load model if available
try:
    model = joblib.load("model.pkl")
    use_model = True
except:
    model = None
    use_model = False

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_indicators(df):
    df["RSI"] = compute_rsi(df["Close"])
    df["SMA_5"] = df["Close"].rolling(5).mean()
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["Trend"] = np.where(df["SMA_5"] > df["SMA_20"], "Bullish", "Bearish")
    return df

def get_signal(symbol):
    df = yf.download(symbol, period="15d", interval="30m", progress=False)
    if df.empty:
        return f"⚠️ No data found for {symbol}"

    df = calculate_indicators(df)
    latest = df.iloc[-1]

    rsi = round(latest["RSI"], 2)
    trend = latest["Trend"]
    price = round(latest["Close"], 2)

    if use_model:
        features = df[["RSI"]].dropna().tail(1)
        prediction = model.predict(features)[0]
        confidence = round(model.predict_proba(features)[0][prediction] * 100, 2)
        signal = "BUY" if prediction == 1 else "SELL"
    else:
        if rsi < 30:
            signal = "BUY"
            confidence = 75
        elif rsi > 70:
            signal = "SELL"
            confidence = 75
        else:
            signal = "HOLD"
            confidence = 50

    direction = "UP" if signal == "BUY" else "DOWN" if signal == "SELL" else "NEUTRAL"
    emoji = "✅ BUY" if signal == "BUY" else "❌ SELL" if signal == "SELL" else "⏸️ HOLD"
    arrow = "📈 UP" if direction == "UP" else "📉 DOWN" if direction == "DOWN" else "⚖️"
    trend_emoji = "📈 Bullish" if trend == "Bullish" else "📉 Bearish"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    return (
        f"📊 Signal: {emoji}\n"
        f"Asset: {symbol}\n"
        f"Direction: {arrow}\n"
        f"Model Confidence: {confidence}%\n"
        f"Price: ${price}\n"
        f"Trend: {trend_emoji}\n"
        f"RSI: {rsi}\n"
        f"📅 Timestamp: {timestamp}"
    )

# Example usage (for test)
if __name__ == "__main__":
    assets = ["BTC-USD", "ETH-USD", "EURUSD=X", "XAUUSD=X", "CL=F"]
    for asset in assets:
        print(get_signal(asset))
        print("-" * 40)
