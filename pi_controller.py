import socket
import json
import threading
import time
from flask import Flask, jsonify, Response
import cv2
import numpy as np
from picamera2 import Picamera2
import RPi.GPIO as GPIO
from led_matrix import LEDMatrix

class PiController:
    def __init__(self, host='0.0.0.0', port=5001):
        self.host = host
        self.port = port
        self.ped_camera = None
        self.vehicle_camera = None
        self.led_matrix = None
        self.detection_data = {
            "pedestrians": 0,
            "vehicles": 0,
            "is_safe": True
        }
        self.setup_hardware()
        self.setup_server()

    def setup_hardware(self):
        try:
            # Initialize pedestrian camera
            self.ped_camera = Picamera2(0)
            ped_config = self.ped_camera.create_preview_configuration(main={"size": (640, 480)})
            self.ped_camera.configure(ped_config)
            self.ped_camera.start()

            # Initialize vehicle camera
            self.vehicle_camera = Picamera2(1)
            vehicle_config = self.vehicle_camera.create_preview_configuration(main={"size": (640, 480)})
            self.vehicle_camera.configure(vehicle_config)
            self.vehicle_camera.start()

            # Initialize LED matrix
            self.led_matrix = LEDMatrix()
            print("Hardware initialized successfully")
        except Exception as e:
            print(f"Error initializing hardware: {e}")

    def setup_server(self):
        self.app = Flask(__name__)
        
        @self.app.route('/get_detection')
        def get_detection():
            return jsonify(self.detection_data)

        @self.app.route('/ped_frame')
        def ped_frame():
            if self.ped_camera:
                frame = self.ped_camera.capture_array()
                ret, buffer = cv2.imencode('.jpg', frame)
                return Response(buffer.tobytes(), mimetype='image/jpeg')
            return None

        @self.app.route('/vehicle_frame')
        def vehicle_frame():
            if self.vehicle_camera:
                frame = self.vehicle_camera.capture_array()
                ret, buffer = cv2.imencode('.jpg', frame)
                return Response(buffer.tobytes(), mimetype='image/jpeg')
            return None

    def update_led_matrix(self, is_safe):
        try:
            if self.led_matrix:
                if is_safe:
                    # Display green pattern for safe
                    self.led_matrix.display_safe()
                else:
                    # Display red pattern for unsafe
                    self.led_matrix.display_unsafe()
        except Exception as e:
            print(f"Error updating LED matrix: {e}")

    def run_detection(self):
        while True:
            try:
                # Your detection logic here
                # This is where you'll implement your actual detection code
                # For now, using random numbers as placeholder
                self.detection_data["pedestrians"] = np.random.randint(0, 5)
                self.detection_data["vehicles"] = np.random.randint(0, 3)
                self.detection_data["is_safe"] = self.detection_data["vehicles"] == 0

                # Update LED matrix
                self.update_led_matrix(self.detection_data["is_safe"])
                
                time.sleep(1)
            except Exception as e:
                print(f"Error in detection loop: {e}")
                time.sleep(1)

    def start(self):
        # Start detection thread
        detection_thread = threading.Thread(target=self.run_detection)
        detection_thread.daemon = True
        detection_thread.start()

        # Start Flask server
        self.app.run(host=self.host, port=self.port)

    def cleanup(self):
        if self.ped_camera:
            self.ped_camera.stop()
        if self.vehicle_camera:
            self.vehicle_camera.stop()
        if self.led_matrix:
            self.led_matrix.cleanup()

if __name__ == "__main__":
    controller = PiController()
    try:
        controller.start()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        controller.cleanup() 