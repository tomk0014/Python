from influxdb import InfluxDBClient
import re

# InfluxDB configuration
db_name = 'IoTSensorData'
host = 'localhost'  # or your InfluxDB host
port = 8086
username = 'enterYourUserName'
password = 'enterApassword'

# Connect to InfluxDB
client = InfluxDBClient(host, port, username, password, db_name)

def parse_device_data(data):
    """Parse the incoming data into device name and value using regular expressions."""
    pattern = re.compile(r'^(.*?)\s=\s*(.*)$')
    match = pattern.match(data)
    if match:
        return match.groups()  # Return device name and value if matched
    else:
        return None, None  # Return None, None if the data does not conform

def write_to_influxdb(data):
    """Write the parsed data to InfluxDB if it conforms to the expected format"""
    device_name, device_value = parse_device_data(data)
    if device_name is None or device_value is None:
        print("Non-conforming data received, skipping: ", data)  # Acknowledge and skip
        return  # Exit the function early

    try:
        device_value = float(device_value)  # Attempt to convert value to float for numeric storage
    except ValueError:
        pass  # Keep device_value as string if conversion fails

    json_body = [
        {
            "measurement": "measurements",
            "tags": {
                "device_name": device_name  # Optional: Adjust tags as per your data structure
            },
            "fields": {
                "value": device_value  # Ensure this matches your data format
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
