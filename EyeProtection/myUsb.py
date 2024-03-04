# import usb.core
# import usb.util

# def find_allDevices():
#     devices = usb.core.find(find_all=True)
#     for device in devices:
#         # print(device)
#         # 获取设备的Vendor ID和Product ID
#         vendor_id = device.idVendor
#         product_id = device.idProduct
#         print(f"Vendor ID: 0x{vendor_id:04X}, Product ID: 0x{product_id:04X}")

# class USBCommunication:
#     def __init__(self, vendor_id, product_id):
#         self.dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
#         if self.dev is None:
#             raise ValueError("Device not found")
        
#         self.dev.set_configuration()
#         self.ep_in = self.dev[0][(0, 0)][0]
#         self.ep_out = self.dev[0][(0, 0)][1]

#     def send_data(self, data):
#         self.dev.write(data)

#     def read_data(self, size):

#         # data = self.dev.read(0x81, size, timeout=5000)
#         # print(data)

#         return self.dev.read(0x81, size, timeout=5000)

#     def close(self):
#         usb.util.dispose_resources(self.dev)
        
# if __name__ == '__main__':
#     # find_allDevices()

#     vendor_id = 0x093A  # 替换为实际设备的 Vendor ID     0x18d1  0x093A
#     product_id = 0x2510  # 替换为实际设备的 Product ID   0x4ee7  0x2510
#     usb_comm = USBCommunication(vendor_id, product_id)

#     try:
#         data_to_send = b"Hello, USB!"
#         # usb_comm.send_data(data_to_send)

#         data_received = usb_comm.read_data(100000)
#         print("Received data:", data_received)
#     except Exception as e:
#         print("USB Error:", e)
#     finally:
#         usb_comm.close()





#!/bin/bash
import ctypes
from ctypes import * 
# prepared to be called from the same class directory python scripts
import sys
import os
import usb.core 
# now our hardware is vid = 0x03fd, pid = 0x0100)
class hardware_usb():
    def __init__(self, vid, pid, read_length = 512, backend='libusb'):
        '''
        vid: vendor id
        pid: product id 
        read_length : buffer length for reading 
        backend: select one from ['libusb', 'windriver']
        '''
        self.read_length = read_length
        self.backend = backend 
        
        if backend == 'libusb':
            usb_dev = usb.core.find(idVendor=vid, idProduct=pid)
            if usb_dev != None :
                usb_dev.set_configuration()
                self.read_addr = 0x82
                self.write_addr = 0x03 
                self.dev = usb_dev 
                self.init_status = True 
            else:
                self.init_status = False 
        elif backend == 'windriver':
            try:
                dll = ctypes.cdll.LoadLibrary( "msdev_dll.dll")
            except Exception as e :
                print("Error occurs when init usb, %s:%s"  %(str(e.__class__), str(e.args)))
                self.init_status = False 
            else:
                # input : void
                # output : int
                    # assum 0 to be successful
                self.init_driver = getattr(dll, '?InitDriver@@YA_NXZ')
                # input : PVOID pBuffer, DWORD &dwSize
                # output: bool
                self._read = getattr(dll, '?Read_USB@@YA_NPAXAAK@Z')
                # input : PVOID pBuffer, DWORD dwSize
                # output: bool
                self._write = getattr(dll, '?Write_USB@@YA_NPAXK@Z')
                if 1 == self.init_driver():
                    self.init_status = True 
                else:
                    self.init_status = False 
         
    def write(self, data):
        '''
        Write data to usb
        Note that data must bytes type
        Return True if success
        '''
        if self.backend == 'windriver':
            # BUG 此处使用c_char_p, 遇到\x00就被截断，可能有bug
            buffer = ctypes.c_char_p()
            buffer.value = data
            leng = ctypes.c_ulong(len(data))
            try:
                status = self._write(buffer,leng)
            except Exception as e :
                print("Error occurs when write usb, %s:%s" %(str(e.__class__), str(e.args)))
                status = 0
            if status == 1:
                ret = True 
            else :
                ret = False 
        elif self.backend == 'libusb':
            write_len = self.dev.write(self.write_addr, data)
            # Test if data is written 
            if write_len == len(data):
                ret = True 
            else:
                ret = False 
        return ret 
    def read(self):
        '''
        Read data from usb  
        Note we will return bytes like data
        Return None if error occurs
        '''
        if self.backend == 'windriver':
            buffer_class = c_ubyte * 512
            buffer = buffer_class()
        
            leng   = ctypes.c_ulong()
            
        
            try :
                status = self._read(buffer, ctypes.byref(leng) )
            except Exception as e :
                print("Error occurs when read from usb, %s:%s" %(str(e.__class__), str(e.args)))
                status = 0
            
            if status == 1:
                ret = bytes(buffer[:leng.value])
            else:
                ret = b'' 
        elif self.backend == 'libusb':
            try:
                ret = self.dev.read(self.read_addr, self.read_length) 
                ret = bytes(ret)
            except Exception as e:
                print("Error occurs when read from usb, %s:%s" %(str(e.__class__), str(e.args)))
                ret = b''
        return ret
if __name__ == "__main__":
    usb_ins = hardware_usb(vid=0x18d1, pid=0x4ee7)
    
    loop_num = 1
    # 在测试中发现有一定概率写入出错
    while True:
        print('============================')
        print('Loop num is', loop_num)
        print('test write function')
        data = b'\x7e\x7f\x00\x66'
        try:
            # write_ret = usb_ins.write(data)
            read_ret = usb_ins.read()
        except Exception as e:
            print("USB Error:", e)
            break
        # print('write function returns', write_ret)
        print('test read function')
        
        print(' read function returns', read_ret)
        loop_num = loop_num + 1