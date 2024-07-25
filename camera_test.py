import cv2

def test_camera(index):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Cannot open camera at index {index}")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print(f"Can't receive frame from camera at index {index}")
        cap.release()
        return False
    
    print(f"Successfully captured frame from camera at index {index}")
    print(f"Frame shape: {frame.shape}")
    
    cv2.imshow(f'Camera {index}', frame)
    cv2.waitKey(2000)  # Wait for 2 seconds
    cv2.destroyAllWindows()
    
    cap.release()
    return True

# Try camera indices 0 to 9
for i in range(10):
    print(f"\nTesting camera index {i}")
    if test_camera(i):
        print(f"Camera at index {i} is working")
        break
else:
    print("No working camera found")