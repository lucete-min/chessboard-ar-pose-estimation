import cv2 as cv
import numpy as np
import glob

CHECKERBOARD = (9,7)

objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1],3), np.float32)
objp[:,:2] = np.mgrid[0:CHECKERBOARD[0],0:CHECKERBOARD[1]].T.reshape(-1,2)

objpoints = []
imgpoints = []

images = glob.glob('images/*.jpg') + glob.glob('images/*.jpeg')

print(f"총 이미지 수: {len(images)}")

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, corners = cv.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        objpoints.append(objp)

        # 정확도 향상 
        corners2 = cv.cornerSubPix(
            gray, corners, (11,11), (-1,-1),
            (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )

        imgpoints.append(corners2)

        cv.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(100)

cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

print("\n=== Calibration Result ===")
print("Camera matrix:\n", mtx)
print("Distortion coefficients:\n", dist)
print("RMSE:", ret)

# 결과 저장 
np.savez('calibration_result.npz', mtx=mtx, dist=dist)
print("calibration_result.npz 저장 완료")