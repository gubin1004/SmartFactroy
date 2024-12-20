import cv2
from ultralytics import YOLO
from gpiozero import InputDevice, Motor, AngularServo
from time import sleep

# YOLOv8 모델 로드
model = YOLO("best.pt")

# 카메라 설정
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 모터 및 적외선 센서 설정
motor = Motor(forward=24, backward=25)
ir_sensor = InputDevice(17)  # 적외선 센서 GPIO 핀 번호
servo = AngularServo(13, min_angle=0, max_angle=90) #서보모터 최대 회전각 설정

previous_ir_state = ir_sensor.is_active
no_obstacle_logged = False

try:
    while True:
        # 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera")
            continue

        # 이미지 대비 및 밝기 조정
        frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=30)

        # IR 센서 상태 확인
        current_ir_state = ir_sensor.is_active
        if current_ir_state != previous_ir_state:
            previous_ir_state = current_ir_state
            no_obstacle_logged = False

            if current_ir_state:
                motor.stop()  # 장애물이 있을 때 모터 정지
                print("Detected")

                # YOLO 추론
                results = model.predict(frame, conf=0.3, imgsz=640, device="cpu", verbose=False)

                detected_bread = False
                for result in results[0].boxes:
                    conf = float(result.conf)
                    cls_id = int(result.cls)
                    label = model.names[cls_id] if cls_id < len(model.names) else "Unknown"

                    if label == "bread" and conf >= 0.5:  # Confidence 조건 완화 (여러 테스트 진행후 변경 예정)
                        detected_bread = True
                        print(f"Detected {label} with confidence {conf:.2f}")
                        break

                # 탐지 결과에 따른 동작
                if detected_bread:
                    motor.forward(speed=0.2)  # 모터 전진
                else:
                    print("No high-confidence bread detected.")
                    for angle in range(0, 90, 45):
                        servo.angle = angle
                        sleep(1)
                    for angle in range(90, -1, -45):
                        servo.angle = angle
                        sleep(0.5)

        else:
            if not no_obstacle_logged:
                print("State: No Obstacle Detected")
                no_obstacle_logged = True
            motor.forward(speed=0.2)

        sleep(0.1)

except KeyboardInterrupt:
    print("Program stopped by user")

finally:
    motor.stop()
    cap.release()
    cv2.destroyAllWindows()
