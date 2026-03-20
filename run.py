import sys
import os

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "internal"))

from bari_lms import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
