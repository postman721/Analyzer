#!/usr/bin/env python3

import json
import sys
import threading
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QListWidget, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QEvent, Qt
from pyudev import Context, Monitor

class DeviceMonitorThread(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback
        self.context = Context()
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='block')

    def run(self):
        for device in iter(self.monitor.poll, None):
            self.callback(device)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Analyzer Monitoring and Mounting')
        self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        self.logTextEdit = QTextEdit(self)
        self.logTextEdit.setReadOnly(True)
        self.layout.addWidget(self.logTextEdit)

        self.deviceList = QListWidget(self)
        self.layout.addWidget(self.deviceList)

        self.refreshButton = QPushButton('Refresh Mounted Devices', self)
        self.refreshButton.clicked.connect(self.refreshMountedDevices)
        self.layout.addWidget(self.refreshButton)

        self.unmountButton = QPushButton('Unmount Selected Device', self)
        self.unmountButton.clicked.connect(self.unmountSelectedDevice)
        self.layout.addWidget(self.unmountButton)

        self.remountButton = QPushButton('Remount Selected Device', self)
        self.remountButton.clicked.connect(self.remountSelectedDevice)
        self.layout.addWidget(self.remountButton)

        self.deviceMonitorThread = DeviceMonitorThread(self.handleDeviceEvent)
        self.deviceMonitorThread.start()

        self.refreshMountedDevices()

    def handleDeviceEvent(self, device):
        QApplication.instance().postEvent(self, DeviceEvent(device))

    def customEvent(self, event):
        if isinstance(event, DeviceEvent):
            self.updateLog(event.device)

    def updateLog(self, device):
        action = device.action
        devicePath = device.device_node
        if action == 'add':
            self.logTextEdit.append(f"Device added - {devicePath}")
            self.refreshMountedDevices()
        elif action == 'remove':
            self.logTextEdit.append(f"Device removed - {devicePath}")
            self.refreshMountedDevices()

    def refreshMountedDevices(self):
        self.deviceList.clear()
        result = subprocess.run(['lsblk', '-J'], capture_output=True, text=True)
        devices = json.loads(result.stdout)
        self.parse_lsblk(devices['blockdevices'])

    def parse_lsblk(self, devices):
        for device in devices:
            name = device['name']
            mountpoint = device.get('mountpoint', '')
            self.deviceList.addItem(f"{name} {mountpoint}")
            children = device.get('children', [])
            self.parse_lsblk(children)

    def unmountSelectedDevice(self):
        selectedItem = self.deviceList.currentItem()
        if selectedItem:
            deviceInfo = selectedItem.text().split()
            deviceName = deviceInfo[0]
            result = subprocess.run(['udisksctl', 'unmount', '-b', f"/dev/{deviceName}"], stderr=subprocess.PIPE)
            if result.returncode == 0:
                self.logTextEdit.append(f"Unmounted - /dev/{deviceName}")
                self.refreshMountedDevices()
            else:
                self.logTextEdit.append(f"Failed to unmount - /dev/{deviceName}: {result.stderr.decode('utf-8')}")

    def remountSelectedDevice(self):
        selectedItem = self.deviceList.currentItem()
        if selectedItem:
            deviceInfo = selectedItem.text().split()
            deviceName = deviceInfo[0]
            result = subprocess.run(['udisksctl', 'mount', '-b', f"/dev/{deviceName}"], stderr=subprocess.PIPE)
            if result.returncode == 0:
                self.logTextEdit.append(f"Remounted - /dev/{deviceName}")
                self.refreshMountedDevices()
            else:
                self.logTextEdit.append(f"Failed to remount - /dev/{deviceName}: {result.stderr.decode('utf-8')}")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit Analyzer',
                                     "Are you sure you want to exit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class DeviceEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, device):
        super().__init__(self.EVENT_TYPE)
        self.device = device

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
