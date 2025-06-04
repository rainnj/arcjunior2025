import cv2
import cv2.aruco as aruco
import numpy as np

class ArUcoDetector:
    def __init__(self, camera_id=0, calib_file="camera_config.npz"):
        self.cap = cv2.VideoCapture(camera_id)
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_100)
        self.parameters = aruco.DetectorParameters_create()

        data = np.load(calib_file)
        self.camera_matrix = data['camera_matrix']
        self.dist_coeffs = data['dist_coeffs']

    def get_tag(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, frame

        frame = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)

        if ids is not None:
            return ids[0][0], frame  # Return first detected tag
        return None, frame

    def release(self):
        self.cap.release()
