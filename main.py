# Read data from Serial Port and Sleep Screen after 10min
import serial
from influxdb import InfluxDBClient
import time
import re
import subprocess
from threading import Timer, Thread
from pynput import keyboard, mouse

# Serial port and InfluxDB configurations
arduino_port = '/dev/ttyACM0'
baud_rate = 9600
db_name = 'IoTSensorData'
host = 'localhost'
port = 8086
username = 'enterYourUserName'
password = 'enterApassword'

# Inactivity timer settings
INACTIVITY_PERIOD = 600  # 10 minutes in seconds
timer = None

def turn_screen_off():
    subprocess.call('xset dpms force off', shell=True)

def reset_timer():
    global timer
    if timer is not None:
        timer.cancel()
    timer = Timer(INACTIVITY_PERIOD, turn_screen_off)
    timer.start()

def on_press(key):
    reset_timer()

def on_click(x, y, button, pressed):
    if pressed:
        reset_timer()

def on_move(x, y):
    reset_timer()

def on_scroll(x, y, dx, dy):
    reset_timer()

def monitor_inactivity():
    # Initialize the timer
    reset_timer()

    # Set up listeners for keyboard and mouse
    with keyboard.Listener(on_press=on_press) as keyboard_listener, \
         mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as mouse_listener:
        keyboard_listener.join()
        mouse_listener.join()

def monitor_serial():
    arduino = serial.Serial(arduino_port, baud_rate)
    time.sleep(2)  # Wait for connection to establish
    client = InfluxDBClient(host, port, username, password, db_name)

    def parse_device_data(data):
        pattern = re.compile(r'^(.*?)\s=\s*(.*)$')
        match = pattern.match(data)
        if match:
            return match.groups()
        else:
            return None, None

    def write_to_influxdb(data):
        device_name, device_value = parse_device_data(data)
        if device_name is None or device_value is None:
            print("Non-conforming data received, skipping: ", data)
            return

        try:
            device_value = float(device_value)
        except ValueError:
            pass

        json_body = [
            {
                "measurement": "measurements",
                "tags": {
                    "device_name": device_name
                },
                "fields": {
                    "value": device_value
                }
            }
        ]

        try:
            success = client.write_points(json_body)
            if success:
                print(f"Data successfully written to 'IoTSensorData' for {device_name} with value {device_value}")
            else:
                print("Failed to write data to InfluxDB.")
        except Exception as e:
            print(f"An error occurred while writing to InfluxDB: {e}")

    try:
        while True:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                write_to_influxdb(line)
    except KeyboardInterrupt:
        print("Script terminated by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        arduino.close()

# Run both monitors in separate threads
if __name__ == '__main__':
    Thread(target=monitor_serial).start()
    Thread(target=monitor_inactivity).start()
