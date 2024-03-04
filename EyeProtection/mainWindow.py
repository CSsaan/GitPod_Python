import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsBlurEffect, QLabel, QDesktopWidget, QInputDialog, QWidget, QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from mySerial import *

# 串口线程
class SerialThread(QThread):
    valueChanged = pyqtSignal(int)  # 定义一个信号，用于传递值
    def __init__(self, com_port, baud_rate):
        super(SerialThread, self).__init__()
        self.com_port = com_port
        self.baud_rate = baud_rate

    def run_SerialReader(self, command=None):
        if command:
            self.serial_reader.send_data(command)
        try:
            print('------------------- read -------------------')
            while True:
                data = self.serial_reader.read_data()
                if data:
                    # print(data)
                    self.serial_reader.readData = data
                    read_distance = len(self.serial_reader.readData) # TODO:正则化解析距离distance: xxx, 没有匹配到则为-1
                    print('read_distance:', read_distance)
                    self.valueChanged.emit(read_distance)  # 发射信号，传递值
                else:
                    self.serial_reader.readData = None
                time.sleep(0.1)  # 添加延迟，减少资源消耗
        except KeyboardInterrupt:
            self.serial_reader.readData = None
            self.serial_reader.close()
    
    def finished(self):
        if(self.serial_reader):
            self.serial_reader.close()

    def run(self):
        self.serial_reader = SerialReader(self.com_port, self.baud_rate)
        # self.serial_reader.run(command = b'\n ls \n')
        self.run_SerialReader(command = b'\n ls \n')
        self.serial_reader.finished.connect(self.finished)

class BlurOverlayWindow(QMainWindow):
    def __init__(self, color):
        super().__init__()

        self.color = color
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.BypassWindowManagerHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # 串口线程：选择COM号+发送接收数据
        COM_num = None
        COM_num = self.select_COM()
        if(COM_num == None):
            QMessageBox.critical(self, 'Error', 'NOT USE a COM. The program now exit.')
            print('The program now exit.')
            raise SystemExit # 退出程序
        self.serial_thread = SerialThread(COM_num, 115200)
        self.serial_thread.valueChanged.connect(self.handleValue)  # 连接信号与槽
        # self.serial_thread.finished.connect(self.decryptFinished)
        self.serial_thread.start()
        
        # 主窗口全屏透明
        desktop = QDesktopWidget()
        screenRect = desktop.screenGeometry(desktop.primaryScreen())
        self.setGeometry(0, 0, screenRect.width(), screenRect.height())

        # 添加黑色掩膜（边缘高斯模糊）
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(25)
        self.label = QLabel(self)
        self.label.setStyleSheet(f"background-color: rgba({self.color.red()}, {self.color.green()}, {self.color.blue()}, {self.color.alpha()});")
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label.setGeometry(int(screenRect.width()/4), int(screenRect.height()/4), int(screenRect.width()/2), int(screenRect.height()/2))
        self.label.setGraphicsEffect(blur_effect)

    def mousePressEvent(self, event):
        print("clicked ")
        pass  # 鼠标点击事件处理

    def select_COM(self):
        all_com = []
        all_description = []
        all_com, all_description = find_allCOM()
        widget = QWidget()
        com_port, ok = QInputDialog.getItem(widget, "COM端口", "请选择COM端口：", all_description, 0, False)
        if ok:
            print("您选择的COM端口是：", com_port)
            return all_com[all_description.index(com_port)]
        else:
            return None
    
    def handleValue(self, value):
        if(value != -1):
            self.label.setStyleSheet(f"background-color: rgba({self.color.red()}, {self.color.green()}, {self.color.blue()}, {value});")
            print("Received value from serial thread:", value)
        else:
            self.label.setStyleSheet(f"background-color: rgba({self.color.red()}, {self.color.green()}, {self.color.blue()}, {0});")
            print("unReceived value from serial thread!")
    
    def decryptFinished(self):
        print("Serial communication finished.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    color = QColor(0, 0, 0, 255)  # 设置颜色值，可以根据需要修改
    window = BlurOverlayWindow(color)
    window.show()
    sys.exit(app.exec_())

