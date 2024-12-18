from flask import Flask , render_template
from threading import Thread
import logging

# Configure Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return "Server is running!"  # Updated message for clarity

# Run the Flask app
def run():
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logging.error(f"Error starting server: {e}")

# Keep the server alive in a separate thread
def keep_alive():
    thread = Thread(target=run, daemon=True)  # Daemon ensures thread exits with main process
    thread.start()
    logging.info("Keep-alive server started.")
