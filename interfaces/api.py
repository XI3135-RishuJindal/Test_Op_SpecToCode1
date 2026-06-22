from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="ok"), 200

def start_api():
    app.run(debug=True)
