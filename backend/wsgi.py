import os
import sys

from dotenv import load_dotenv

# On Windows the console defaults to cp1252, which can't encode the Unicode
# characters (e.g. ✔) that libraries like gradio_client print — that crash
# would otherwise surface as a bogus "try-on failed" error. Force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_ENV") == "development"
    )
