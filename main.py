from flask import Flask, request
import train_model

app = Flask(__name__)

# === Root check ===
@app.route("/", methods=["GET"])
def home():
    return "🤖 Trading bot backend is live!"

# === Trigger model training ===
@app.route("/train", methods=["GET"])
def train():
    try:
        data = train_model.load_data()
        train_model.train_model(data)
        return "✅ Model trained and saved as model.pkl"
    except Exception as e:
        return f"❌ Training failed: {str(e)}"

# === Placeholder for Telegram bot (coming soon) ===
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    # TODO: handle Telegram commands here
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
