import cv2
import time

def test_camera(index):
    print(f"\nTesting camera index {index}")
    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        print(f"Failed to open camera at index {index}")
        return False
    
    print(f"Camera opened successfully at index {index}")
    print(f"Camera properties:")
    print(f"  Resolution: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    print(f"  FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    
    # Try to read a frame
    ret, frame = cap.read()
    if not ret or frame is None:
        print(f"Failed to read frame from camera at index {index}")
        cap.release()
        return False
    
    print(f"Successfully read frame from camera at index {index}")
    print(f"Frame shape: {frame.shape}")
    
    # Show the frame
    cv2.imshow(f'Camera {index}', frame)
    cv2.waitKey(2000)  # Show frame for 2 seconds
    cv2.destroyAllWindows()
    
    cap.release()
    return True

def main():
    print("Testing all possible camera indices...")
    working_cameras = []
    
    for i in range(3):  # Try first 3 indices
        if test_camera(i):
            working_cameras.append(i)
    
    if working_cameras:
        print(f"\nFound {len(working_cameras)} working camera(s) at index(es): {working_cameras}")
    else:
        print("\nNo working cameras found!")
        print("\nTroubleshooting tips:")
        print("1. Make sure your camera is properly connected")
        print("2. Check if your camera is being used by another application")
        print("3. Try unplugging and replugging your camera")
        print("4. Check Device Manager to see if your camera is recognized")
        print("5. Try updating your camera drivers")

if __name__ == "__main__":
    main() 