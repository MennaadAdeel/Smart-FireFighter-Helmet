# sim7600.py
import time
import serial


class GSMModule:
    def __init__(self, serial_port, baudrate):
        self.ser = serial.Serial(serial_port, baudrate, timeout=5)

    def send_at_command(self, command, delay=1):
        """
        Send an AT command to the SIM7600 module and return the response.
        """
        self.ser.write((command + "\r\n").encode())
        time.sleep(delay)
        response = self.ser.readlines()
        return [line.decode('utf-8').strip() for line in response]

    def get_gps_location(self):
        """
        Retrieve GPS location using the SIM7600 module.
        """
        # Enable GPS
        self.send_at_command("AT+CGNSPWR=1")
        time.sleep(2)

        # Get GPS Information
        gps_response = self.send_at_command("AT+CGNSINF")
        for line in gps_response:
            if "+CGNSINF" in line:
                data = line.split(",")
                if len(data) > 4 and data[3] and data[4]:
                    latitude = data[3]
                    longitude = data[4]
                    return {"latitude": latitude, "longitude": longitude}
        return None

    def get_signal_strength(self):
        """
        Get the signal strength of the GSM connection.
        """
        response = self.send_at_command("AT+CSQ")
        for line in response:
            if "+CSQ" in line:
                try:
                    strength = int(line.split(":")[1].split(",")[0].strip())
                    return strength  # Signal strength is a value between 0 and 31
                except (IndexError, ValueError):
                    return 0
        return 0

    def is_connected(self):
        """
        Check if the GSM module is connected to a network.
        """
        response = self.send_at_command("AT+CGATT?")
        return any("1" in line for line in response)

    def restart(self):
        """
        Restart the GSM module.
        """
        self.send_at_command("AT+CFUN=1,1")  # Reset module
        time.sleep(10)

    def send_data(self, client, topic, data):
        """
        Send data using MQTT.
        """
        try:
            client.publish(topic, data)
        except Exception as e:
            print(f"Failed to send data: {e}")
