import cv2
from flask import Flask, Response

app = Flask(__name__)

# USB 카메라 장치 설정
camera = cv2.VideoCapture(0)  # 카메라 인덱스 0

def generate_frames():
    while True:
        # 카메라에서 프레임 읽기
        success, frame = camera.read()
        if not success:
            break
        else:
            # 프레임을 JPEG로 인코딩
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # HTTP 응답 형식으로 프레임 생성
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # 기본 웹 페이지에서 스트리밍 출력
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Webcam Stream</title>
    </head>
    <body>
        <h1>Webcam Stream</h1>
        <img src="/video_feed" width="100%">
    </body>
    </html>
    """

@app.route('/video_feed')
def video_feed():
    # 스트리밍 엔드포인트
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
