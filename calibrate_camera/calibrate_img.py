import numpy as np
import cv2
import glob
import os

CHECKERBOARD_DIMS = (8, 6)
SQUARE_SIZE_MM = 24
IMAGE_PATH_PATTERN = 'calibration_images/*.png'
OUTPUT_DIR = 'calibrated'

os.makedirs(OUTPUT_DIR, exist_ok=True)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((CHECKERBOARD_DIMS[0] * CHECKERBOARD_DIMS[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:CHECKERBOARD_DIMS[0], 0:CHECKERBOARD_DIMS[1]].T.reshape(-1,2)
objp = objp * SQUARE_SIZE_MM

objpoints = []
imgpoints = []
images = glob.glob(IMAGE_PATH_PATTERN)
img_shape = None

print(f"Processing {len(images)} images from '{IMAGE_PATH_PATTERN}'...")

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if img_shape is None:
        img_shape = gray.shape[::-1]

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD_DIMS, None)

    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        
        cv2.drawChessboardCorners(img, CHECKERBOARD_DIMS, corners2, ret)
        output_path = os.path.join(OUTPUT_DIR, os.path.basename(fname))
        cv2.imwrite(output_path, img)

if len(objpoints) > 5:
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img_shape, None, None)

    print(f"Used {len(objpoints)} of {len(images)} images.")
    
    print("\nCamera Matrix (Intrinsics):")
    print(camera_matrix)
    
    print("\nDistortion Coefficients:")
    print(dist_coeffs)

    # output_filename = 'camera_calibration_data.npz'
    # np.savez(
    #     output_filename,
    #     mtx=camera_matrix,
    #     dist=dist_coeffs
    # )
    # print(f"\nCalibration data saved to '{output_filename}'")
    print(f"Visualizations saved")

else:
    print("\n--- Failed ---")