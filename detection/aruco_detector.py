import cv2
import cv2.aruco as aruco
import numpy as np

class ArUcoDetector:
    def __init__(self, camera_id=0, calib_file=None):
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise Exception(f"Cannot open camera with ID {camera_id}")

        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
        self.parameters = aruco.DetectorParameters()

        # Skip calibration if not provided
        self.use_calibration = calib_file is not None
        if self.use_calibration:
            try:
                data = np.load(calib_file)
                self.camera_matrix = data['camera_matrix']
                self.dist_coeffs = data['dist_coeffs']
            except Exception as e:
                raise FileNotFoundError(f"❌ Failed to load calibration file: {e}")

    def get_tag(self):
        ret, frame = self.cap.read()
        if not ret:
            print("[ERROR] Frame capture failed.")
            return None, None

        if self.use_calibration:
            frame = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)

        if ids is not None:
            aruco.drawDetectedMarkers(frame, corners, ids)
            return ids[0][0], frame
        return None, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

# === Main Execution ===
if __name__ == "__main__":
    detector = ArUcoDetector(camera_id=0)  # 👈 no config file

    while True:
        tag_id, frame = detector.get_tag()
        if frame is not None:
            if tag_id is not None:
                print(f"✅ Detected ArUco Tag ID: {tag_id}")
            cv2.imshow("ArUco Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    detector.release()
