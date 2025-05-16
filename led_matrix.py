import RPi.GPIO as GPIO
import time

class LEDMatrix:
    def __init__(self):
        # Define GPIO pins for your LED matrix
        # Adjust these pin numbers based on your wiring
        self.rows = [17, 27, 22, 23]  # Example row pins
        self.cols = [24, 25, 8, 7]    # Example column pins
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in self.rows + self.cols:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        
        # Define patterns
        self.safe_pattern = [
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 1]
        ]
        
        self.unsafe_pattern = [
            [1, 0, 0, 1],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [1, 0, 0, 1]
        ]

    def display_pattern(self, pattern):
        try:
            while True:  # Keep displaying until interrupted
                for row in range(4):
                    # Set all rows low
                    for r in self.rows:
                        GPIO.output(r, GPIO.LOW)
                    
                    # Set current row high
                    GPIO.output(self.rows[row], GPIO.HIGH)
                    
                    # Set columns based on pattern
                    for col in range(4):
                        if pattern[row][col]:
                            GPIO.output(self.cols[col], GPIO.HIGH)
                        else:
                            GPIO.output(self.cols[col], GPIO.LOW)
                    
                    # Small delay for persistence of vision
                    time.sleep(0.001)
                    
                    # Clear columns
                    for col in self.cols:
                        GPIO.output(col, GPIO.LOW)
        except KeyboardInterrupt:
            self.clear()

    def display_safe(self):
        self.display_pattern(self.safe_pattern)

    def display_unsafe(self):
        self.display_pattern(self.unsafe_pattern)

    def clear(self):
        for pin in self.rows + self.cols:
            GPIO.output(pin, GPIO.LOW)

    def cleanup(self):
        self.clear()
        GPIO.cleanup() 