from flask import Flask, request, jsonify, render_template
import os
import subprocess

FIFO_PATH = "/tmp/serial_cmd"

app = Flask(__name__)

def get_log_data():
    data = []
    try:
        output = subprocess.check_output(f"tail -n 100 /log.txt").decode("utf-8")
        for line in output.splitlines():
            if "SERIAL" not in line:
                continue
            data.append(line) 
        
    except Exception as e:
        print(f"Error reading log: {e}")
    return data
    
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/write", methods=["POST"])
def write_serial():
    data = request.json.get("data")

    if not data:
        return jsonify({"error": "No se envió 'data'"}), 400

    try:
        if not os.path.exists(FIFO_PATH):
            os.mkfifo(FIFO_PATH)

        fd = os.open(FIFO_PATH, os.O_WRONLY | os.O_NONBLOCK)
        with os.fdopen(fd, "w") as fifo:
            fifo.write(data + "\n")


        return jsonify({
            "status": "ok",
            "sent": data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/log", methods=["GET"])
def get_log():
    try:
        log_data = get_log_data()
        return jsonify(log_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
