import cv2
from cvzone.HandTrackingModule import HandDetector
from gpiozero import LED
from time import sleep
import requests

relay = LED(17)  # GPIO 핀 17에 릴레이 연결

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 프레임 너비 설정
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 프레임 높이 설정

# 손 감지기 초기화
detector = HandDetector(maxHands=1, detectionCon=0.8)

# 손 감지 상태 초기화
previous_state = None  # 이전 상태 (None: 초기 상태, True: 손 감지됨, False: 손 감지되지 않음)

# 서버 API 설정
SERVER_URL = "http://ip_address/accountapp/hand_detection2/"

def send_data_to_server(value):
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(SERVER_URL, json={"status": value}, headers=headers)
        if response.status_code == 201:
            print("Data sent successfully:", response.json())
        else:
            print("Failed to send data:", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print("Error connecting to server:", e)
      
try:
    while True:
        # 웹캠에서 프레임 가져오기
        ret, img = cap.read()
      
        if not ret:
            print("카메라 연결 실패!")
            break
          
        # 손 감지
        hands, img = detector.findHands(img, flipType=False)
        current_state = bool(hands)  # 현재 상태 (True: 손 감지됨, False: 손 감지되지 않음)
      
        if current_state != previous_state:  # 상태가 변경되었을 때만 실행
          
            if current_state:  # 손이 감지되었을 때
                relay.off()  # 전력 OFF
                print("손이 감지되었습니다. 전력을 차단합니다.")
                send_data_to_server(1)  # 서버로 1 전송
              
            else:  # 손이 감지되지 않았을 때
                relay.on()  # 전력 ON
                print("손이 감지되지 않았습니다. 전력을 켭니다.")
                send_data_to_server(0)  # 서버로 0 전송
              
            previous_state = current_state  # 상태 업데이트
          
        # 화면에 이미지 표시
        cv2.imshow("Image", img)
      
        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) == ord("q"):
            break
          
except KeyboardInterrupt:
    print("프로그램이 종료됩니다.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    relay.close()
