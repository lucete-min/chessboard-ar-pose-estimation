import cv2 as cv
import numpy as np

CHECKERBOARD = (9, 7)   # 내부 코너 개수
SQUARE_SIZE = 0.02      # 20mm = 0.02m

def draw_cube(img, imgpts):
    imgpts = np.int32(imgpts).reshape(-1, 2)

    # 아래 면
    img = cv.drawContours(img, [imgpts[:4]], -1, (255, 0, 0), 2)

    # 기둥
    for i, j in zip(range(4), range(4, 8)):
        img = cv.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (0, 255, 0), 2)

    # 위 면
    img = cv.drawContours(img, [imgpts[4:]], -1, (0, 0, 255), 2)
    return img

def draw_custom_object(img, rvec, tvec, mtx, dist):
    # 체스보드 위에 숫자 4 비슷한 모양
    pts_3d = np.float32([
        [5, 0, 0],
        [5, 2, 0],
        [6, 2, 0],
        [6, 0, 0],
        [6, 4, 0],
        [5, 4, 0],
        [7, 4, 0]
    ]) * SQUARE_SIZE

    imgpts, _ = cv.projectPoints(pts_3d, rvec, tvec, mtx, dist)
    imgpts = np.int32(imgpts).reshape(-1, 2)

    cv.line(img, tuple(imgpts[0]), tuple(imgpts[1]), (0, 255, 255), 3)
    cv.line(img, tuple(imgpts[1]), tuple(imgpts[2]), (0, 255, 255), 3)
    cv.line(img, tuple(imgpts[2]), tuple(imgpts[3]), (0, 255, 255), 3)
    cv.line(img, tuple(imgpts[2]), tuple(imgpts[4]), (0, 255, 255), 3)
    cv.line(img, tuple(imgpts[4]), tuple(imgpts[5]), (0, 255, 255), 3)
    cv.line(img, tuple(imgpts[4]), tuple(imgpts[6]), (0, 255, 255), 3)

    return img

# calibration_result.npz 불러오기
data = np.load('calibration_result.npz')
mtx = data['mtx']
dist = data['dist']

# 체스보드의 3D 점 생성
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

# 큐브 점
cube = np.float32([
    [0, 0, 0],
    [2, 0, 0],
    [2, 2, 0],
    [0, 2, 0],
    [0, 0, -2],
    [2, 0, -2],
    [2, 2, -2],
    [0, 2, -2]
]) * SQUARE_SIZE

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
shot_idx = 0

print("s: 스크린샷 저장 / q: 종료")

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임 읽기 실패")
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    found, corners = cv.findChessboardCorners(gray, CHECKERBOARD, None)

    if found:
        corners2 = cv.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria
        )

        ok, rvec, tvec = cv.solvePnP(objp, corners2, mtx, dist)

        if ok:
            imgpts, _ = cv.projectPoints(cube, rvec, tvec, mtx, dist)
            frame = draw_cube(frame, imgpts)
            frame = draw_custom_object(frame, rvec, tvec, mtx, dist)

            cv.putText(frame, "Pose detected", (20, 40),
                       cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    cv.imshow("AR Chessboard", frame)
    key = cv.waitKey(1) & 0xFF

    if key == ord('s'):
        filename = f"demo_{shot_idx}.png"
        cv.imwrite(filename, frame)
        print(f"{filename} 저장 완료")
        shot_idx += 1
    elif key == ord('q'):
        break

cap.release()
cv.destroyAllWindows()