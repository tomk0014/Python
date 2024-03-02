import serial
import time
from influxdb_handler import write_to_influxdb

# Serial port configuration
arduino_port = '/dev/ttyACM0'
baud_rate = 9600  # Adjust as per your Arduino's Configuration

# Establish a connection to the Arduino
arduino = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Wait for connection to establish

def read_from_arduino():
    try:
        while True:
            if arduino.in_waiting > 0:
                # Read data from Arduino, decode, and strip newline
                line = arduino.readline().decode('utf-8').strip()
                # Write the parsed data to InfluxDB
                write_to_influxdb(line)
    except KeyboardInterrupt:
        print("Script terminated by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        arduino.close()  # Ensure serial connection is closed on termination
