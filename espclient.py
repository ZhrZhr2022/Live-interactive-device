import socket
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from threading import Thread
import keyboard

# 配置广播端口
broadcast_port = 5555  # 广播端口

def get_local_ip():
    # 创建UDP套接字
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 连接到远程服务器（并未实际发送数据）
        temp_socket.connect(('8.8.8.8', 80))
        local_ip = temp_socket.getsockname()[0]
    except Exception as e:
        print(f"获取本地IP地址失败: {e}")
        local_ip = '127.0.0.1'
    finally:
        temp_socket.close()
    return local_ip

def calculate_broadcast_ip(local_ip):
    # 将本地IP地址拆分为四个整数
    ip_parts = local_ip.split('.')
    if len(ip_parts) != 4:
        return None

    # 获取子网掩码，默认为24位子网掩码（255.255.255.0）
    subnet_mask = '255.255.255.0'
    subnet_mask_parts = [int(part) for part in subnet_mask.split('.')]

    # 计算广播地址
    broadcast_ip_parts = []
    for i in range(4):
        broadcast_ip_parts.append(int(ip_parts[i]) | (~subnet_mask_parts[i] & 0xFF))

    # 拼接成字符串形式的广播地址
    broadcast_ip = '.'.join(map(str, broadcast_ip_parts))
    return broadcast_ip

def send_broadcast(message):
    local_ip = get_local_ip()
    broadcast_ip = calculate_broadcast_ip(local_ip)
    print(f"本地IP地址: {local_ip}")
    print(f"计算得到的广播地址: {broadcast_ip}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((local_ip, 0))

    sock.sendto(message.encode('utf-8'), (broadcast_ip, broadcast_port))
    print(f"发送广播消息: {message}")

def monitor_keyboard():
    def on_press(event):
        if event.name == 'a':
            send_broadcast("1")

    keyboard.on_press(on_press)
    keyboard.wait('esc')  # 运行直到按下'esc'键

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('登录')
        self.setGeometry(100, 100, 400, 200)

        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel('请输入用户名和密码')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(QtGui.QFont('Arial', 16))
        layout.addWidget(self.label)

        form_layout = QtWidgets.QFormLayout()

        self.username_entry = QtWidgets.QLineEdit(self)
        self.username_label = QtWidgets.QLabel('用户名:')
        self.username_label.setFont(QtGui.QFont('Arial', 12))
        form_layout.addRow(self.username_label, self.username_entry)

        self.password_entry = QtWidgets.QLineEdit(self)
        self.password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_label = QtWidgets.QLabel('密码:')
        self.password_label.setFont(QtGui.QFont('Arial', 12))
        form_layout.addRow(self.password_label, self.password_entry)

        layout.addLayout(form_layout)

        self.login_button = QtWidgets.QPushButton('登录', self)
        self.login_button.setFont(QtGui.QFont('Arial', 12))
        self.login_button.setFixedWidth(100)
        self.login_button.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_button, alignment=QtCore.Qt.AlignCenter)

        self.setLayout(layout)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def attempt_login(self):
        try:
            username = self.username_entry.text()
            password = self.password_entry.text()
            if username == 'admin' and password == '123456':
                self.label.setText('登录成功!')
                QtWidgets.QMessageBox.information(self, '成功', '登录成功')
                self.main_app()
            else:
                self.label.setText('登录失败，请重试')
        except Exception as e:
            self.label.setText('登录失败，请重试')

    def main_app(self):
        self.hide()
        self.main_window = MainWindow()
        self.main_window.show()
        self.start_keyboard_monitor()

    def start_keyboard_monitor(self):
        keyboard_thread = Thread(target=monitor_keyboard)
        keyboard_thread.daemon = True
        keyboard_thread.start()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Socket Client')
        self.setGeometry(100, 100, 400, 300)

        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel('正在监听按键...')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(QtGui.QFont('Arial', 16))
        layout.addWidget(self.label)

        self.clear_wifi_button = QtWidgets.QPushButton('清除WIFI', self)
        self.clear_wifi_button.setFont(QtGui.QFont('Arial', 12))
        self.clear_wifi_button.setFixedWidth(100)
        self.clear_wifi_button.clicked.connect(self.clear_wifi)
        layout.addWidget(self.clear_wifi_button, alignment=QtCore.Qt.AlignCenter)

        self.setLayout(layout)
        self.center()

    def set_status(self, status):
        self.label.setText(status)

    def clear_wifi(self):
        send_broadcast("2")
        QtWidgets.QApplication.quit()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

def main():
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
