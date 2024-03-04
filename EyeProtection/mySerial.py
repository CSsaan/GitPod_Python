import serial
import time
import binascii
import serial.tools.list_ports

ALL_DESCRIPTION = []
ALL_COM = []
def find_allCOM():
    ports = serial.tools.list_ports.comports()
    if len(ports) == 0:
        print("None COM")
        return []
    else:
        print("Have Find COM: ")
        for port in ports:
            ALL_COM.append(str(port.device))
            ALL_DESCRIPTION.append(f"{str(port.device)}-{str(port.description)}")
            print(f'*{len(ALL_COM)}*: {port.description}')
        return ALL_COM, ALL_DESCRIPTION
    # print('-------------------------------------------')
    
    # while True:
    #     try:
    #         num = int(input("please select a COM: "))
    #         if 0 < num <= len(ALL_COM):
    #             return num
    #         else:
    #             print(f"must input a number between [0, {len(ALL_COM)}]")
    #     except ValueError:
    #         print("must input a number!")

class SerialReader:
    def __init__(self, port, baudrate):
        self.readData = None
        try:
            self.ser = serial.Serial(port, baudrate, 8, 'N', 1)
            if(self.ser.is_open):
                print(f"Has open Port: {port}")
                # self.run()
            else:
                print(f"cannot Port: {port} - {baudrate}")
        except Exception as e:
            print(f"Failed to initialize serial port: {e}")
            self.ser = None

    def send_data(self, command):
        try:
            self.ser.write(command)
            self.ser.flush()
            print(f"Sent Str: {command}")
        except Exception as e:
            print(f"Error sending data: {e}")

    # 将字符串转换为十六进制
    def str_to_hex(self, s):
        return ' '.join([hex(ord(c)).replace('0x', '') for c in s])

    def hex_to_str(self, s):
        return ''.join([chr(i) for i in [int(b, 16) for b in s.split(' ')]])

    def str_to_bin(self, s):
        return ' '.join([bin(ord(c)).replace('0b', '') for c in s])

    def bin_to_str(self, s):
        return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])

    def send_data_str(self, data):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(data.encode())
                print(f"Sent Str: {data}")
            except Exception as e:
                print(f"Error sending data: {e}")
    
    def send_data_hex(self, data):
        list_use = []
        data = self.str_to_hex(data)
        num = data.split(" ")
        for i in range(len(num)):
            list_use.append(int(num[i], 16))
        print(f'list_use:{list_use}')
        data = bytes(list_use)
        data01 = ''.join(map(lambda x: (' ' if len(hex(x)) >= 4 else ' 0') + hex(x)[2:],data))   # 转为16进制
        try:
            self.ser.write(data)
            print('Sent Hex:' + str(data01.upper()))
        except Exception as e:
            print(f"Error sending data: {e}")

    def read_data(self):
        if self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting:
                    data = self.ser.readline().decode().strip()
                    return data
            except Exception as e:
                print(f"Error reading data from serial port: {e}")
        return None

    def close(self):
        print('------------------- close -------------------')
        if self.ser and self.ser.is_open:
            self.ser.close()

    def run(self, command=None):
        if command:
            self.send_data(command)
        try:
            print('------------------- read -------------------')
            while True:
                data = self.read_data()
                if data:
                    print(data)
                    self.readData = data
                else:
                    self.readData = None
                time.sleep(0.1)  # 添加延迟，减少资源消耗
        except KeyboardInterrupt:
            self.readData = None
            self.close()
            
if __name__ == '__main__':
    select_number = find_allCOM()
    COM_n = ALL_COM[select_number-1]
    print(f'*{COM_n.device}*')

    serial_reader = SerialReader(COM_n.device, 115200)
    
    command = b'\n ls \n'
    serial_reader.send_data(command)

    try:
        while True:
            data = serial_reader.read_data()
            if data:
                print(data)
            time.sleep(0.1)  # 添加延迟，减少资源消耗
    except KeyboardInterrupt:
        serial_reader.close()