from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import time
import threading
import os
import requests

app = Flask(__name__)

# Configuration
PI_HOST = "192.168.1.100"  # Change this to your Raspberry Pi's IP address
PI_PORT = 5001

# Global variables for detection results
detection_results = {
    "pedestrians": 0,
    "vehicles": 0,
    "is_safe": True,
    "ped_camera_status": "Initializing...",
    "vehicle_camera_status": "Initializing...",
    "pi_connection": "Disconnected"
}

def check_pi_connection():
    try:
        response = requests.get(f"http://{PI_HOST}:{PI_PORT}/get_detection", timeout=1)
        if response.status_code == 200:
            return True
    except:
        return False
    return False

def generate_ped_frames():
    while True:
        try:
            if check_pi_connection():
                # Get frame from Raspberry Pi
                response = requests.get(f"http://{PI_HOST}:{PI_PORT}/ped_frame")
                if response.status_code == 200:
                    frame = response.content
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    continue
            
            # Fallback to local camera or error frame
            frame = create_error_frame("Pedestrian Camera Not Available")
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error generating pedestrian frame: {e}")
            time.sleep(1)

def generate_vehicle_frames():
    while True:
        try:
            if check_pi_connection():
                # Get frame from Raspberry Pi
                response = requests.get(f"http://{PI_HOST}:{PI_PORT}/vehicle_frame")
                if response.status_code == 200:
                    frame = response.content
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    continue
            
            # Fallback to local camera or error frame
            frame = create_error_frame("Vehicle Camera Not Available")
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error generating vehicle frame: {e}")
            time.sleep(1)

def create_error_frame(message):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, message, (50, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return frame

def update_detection():
    while True:
        try:
            if check_pi_connection():
                # Get data from Raspberry Pi
                response = requests.get(f"http://{PI_HOST}:{PI_PORT}/get_detection")
                if response.status_code == 200:
                    pi_data = response.json()
                    detection_results.update(pi_data)
                    detection_results["pi_connection"] = "Connected"
                    detection_results["ped_camera_status"] = "Connected to Pi"
                    detection_results["vehicle_camera_status"] = "Connected to Pi"
                    continue
            
            # Fallback to local detection or error state
            detection_results["pi_connection"] = "Disconnected"
            detection_results["ped_camera_status"] = "Local Mode"
            detection_results["vehicle_camera_status"] = "Local Mode"
            detection_results["pedestrians"] = 0
            detection_results["vehicles"] = 0
            detection_results["is_safe"] = True
            
            time.sleep(1)
        except Exception as e:
            print(f"Error in detection update: {e}")
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ped_video_feed')
def ped_video_feed():
    return Response(generate_ped_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/vehicle_video_feed')
def vehicle_video_feed():
    return Response(generate_vehicle_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_detection')
def get_detection():
    return jsonify(detection_results)

if __name__ == '__main__':
    # Start detection thread
    detection_thread = threading.Thread(target=update_detection)
    detection_thread.daemon = True
    detection_thread.start()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error starting Flask server: {e}")
