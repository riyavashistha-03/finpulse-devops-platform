"""
Application Entrypoint
"""
import os
from app import create_app

env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    host = os.getenv("HOST", "0.0.0.0")
    debug = env == "development"
    print(f"[*] Starting FinPulse ({env} mode) on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
