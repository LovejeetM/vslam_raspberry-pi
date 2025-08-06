import numpy as np
import cv2
import glob
import os

CHECKERBOARD_DIMS = (8, 6)      # had 9 * 7 squares
SQUARE_SIZE_MM = 24         #  each square was 2.4 cm, measured by ruler.
IMAGE_PATH_PATTERN = 'calibration_images/*.png'

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((CHECKERBOARD_DIMS[0] * CHECKERBOARD_DIMS[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:CHECKERBOARD_DIMS[0], 0:CHECKERBOARD_DIMS[1]].T.reshape(-1,2)
objp = objp * SQUARE_SIZE_MM

objpoints = []
imgpoints = []

images = glob.glob(IMAGE_PATH_PATTERN)

print(f"{len(images)} images. Processing...")

img_shape = None
found_corners_count = 0

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if img_shape is None:
        img_shape = gray.shape[::-1]

    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD_DIMS, None)

    if ret == True:
        found_corners_count += 1
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        print(f"Found corners in {os.path.basename(fname)}")
    else:
        print(f"FAILED: to find corners in {os.path.basename(fname)}")

if found_corners_count < 5:
    print("\nfailed. Not enough images with detectable corners.")

else:
    # Performing calibration with valid images")
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img_shape, None, None)

    print("Camera Matrix (Intrinsics):")
    print(camera_matrix)
    print("\nDistortion Coefficients:")
    print(dist_coeffs)


    output_filename = 'camera_calibration_data.npz'
    np.savez(
        output_filename,
        mtx=camera_matrix,
        dist=dist_coeffs
    )


