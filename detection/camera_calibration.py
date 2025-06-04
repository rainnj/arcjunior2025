import cv2
import numpy as np
import os

# Settings
CHESSBOARD_SIZE = (9, 6)
CALIBRATION_IMAGES_DIR = "calibration_images"
CALIBRATION_FILE = "camera_config.npz"

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((CHESSBOARD_SIZE[0]*CHESSBOARD_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)

objpoints = []
imgpoints = []

images = [f for f in os.listdir(CALIBRATION_IMAGES_DIR) if f.endswith(".jpg") or f.endswith(".png")]
for fname in images:
    img = cv2.imread(os.path.join(CALIBRATION_IMAGES_DIR, fname))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)

# Calibration
ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Save
np.savez(CALIBRATION_FILE, camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)
print("Calibration complete. Saved to", CALIBRATION_FILE)
