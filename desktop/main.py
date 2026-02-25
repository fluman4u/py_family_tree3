import os
import sys
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import app

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run()
