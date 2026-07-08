import os
from app import create_app

config_name = os.environ.get("APP_CONFIG") or os.environ.get("FLASK_ENV")
if not config_name and os.environ.get("RENDER"):
    config_name = "production"

app = create_app(config_name or "development")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)