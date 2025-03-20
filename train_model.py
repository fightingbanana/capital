import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# === CONFIG ===
ASSETS = ["BTC-USD", "ETH-USD", "EURUSD=X", "XAUUSD=X", "CL=F"]
INTERVAL = "30m"
LOOKAHEAD = 4  # 4 candles ahead = 2 hours if 30m
THRESHOLD = 0.002  # 0.2% move
MODEL_FILE = "model.pkl"
# ==============

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def generate_features(df):
    df["RSI"] = compute_rsi(df["Close"])
    df["SMA_5"] = df["Close"].rolling(5).mean()
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["Trend"] = np.where(df["SMA_5"] > df["SMA_20"], 1, 0)
    return df

def label_data(df):
    df["Future_Close"] = df["Close"].shift(-LOOKAHEAD)
    df["Target"] = (df["Future_Close"] > df["Close"] * (1 + THRESHOLD)).astype(int)
    return df

def load_data():
    all_data = []
    for symbol in ASSETS:
        print(f"📥 Downloading {symbol}...")
        df = yf.download(symbol, period="60d", interval=INTERVAL, progress=False)
        if df.empty:
            continue
        df = generate_features(df)
        df = label_data(df)
        df["Symbol"] = symbol
        all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

def train_model(df):
    df = df.dropna()
    features = ["RSI", "Trend"]
    X = df[features]
    y = df["Target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"✅ Model trained. Accuracy: {round(acc * 100, 2)}%")

    joblib.dump(model, MODEL_FILE)
    print(f"📦 Model saved to {MODEL_FILE}")

if __name__ == "__main__":
    data = load_data()
    train_model(data)
