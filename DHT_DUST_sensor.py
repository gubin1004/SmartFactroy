import os
import fcntl
import time
import Adafruit_DHT
import requests

sensor = Adafruit_DHT.DHT11
pin = 17  #dht11 pin번호

# 미세먼지 센서의 I2C 통신을 위한 설정
I2C_SLAVE = 0x0703
PM2008 = 0x28

# 서버 URL
url = 'http://ip_address/accountapp/sensor/'  # 실제 서버 URL로 변경

try:
    # I2C 버스 열기
    fd = os.open('/dev/i2c-1', os.O_RDWR)
except OSError as e:
    print(f"Failed to open the i2c bus: {e}")
    exit(1)

try:
    # I2C 장치에 대한 액세스 요청
    fcntl.ioctl(fd, I2C_SLAVE, PM2008)
except OSError as e:
    print(f"Failed to acquire bus access/or talk to slave: {e}")
    os.close(fd)
    exit(1)

try:
    while True:
        try:
            # 온습도 측정
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

            if humidity is not None and temperature is not None:
                # 미세먼지 측정
                data = os.read(fd, 32)
                pm25 = 256 * int(data[9]) + int(data[10])
                pm10 = 256 * int(data[11]) + int(data[12])

                # 측정 데이터 출력
                print(f'Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%, PM2.5: {pm25}, PM10: {pm10}')

                # 서버에 데이터 전송
                payload = {'temperature': temperature, 'humidity': humidity, 'pm25': pm25, 'pm10': pm10}
                response = requests.post(url, json=payload)
                print("Data sent to server:", response.text)
            else:
                print('Failed to get reading from sensor')
        except OSError as e:
            print(f"Failed to read from the sensor: {e}")
            break

        # 1분(60초) 대기
        time.sleep(10)
except KeyboardInterrupt:
    pass
finally:
    # I2C 버스 닫기
    os.close(fd)
