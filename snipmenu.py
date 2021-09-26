import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PIL import ImageGrab
import numpy as np
import cv2

class TransparentOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(0.5)
        screen_width = 1920
        screen_height = 1200
        self.setGeometry(0, 0, screen_width, screen_height)
        self.end_point = QtCore.QPoint()
        self.start_point = QtCore.QPoint()

    def mousePressEvent(self, event):
        print("Mouse pressed.")
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.update()
        print(self.end_point.x(), self.end_point.y())

    def mouseReleaseEvent(self, event):
        # Call capture function
        print("Mouse released.")
        print(self.end_point.x(), self.end_point.y())
        self.window = MainMenu()
        self.window.show()
        self.close()
        
    def mouseMoveEvent(self, event):
        print("Mouse moved.")
        self.end_point = event.pos()
        self.update()
        print(self.end_point.x(), self.end_point.y())

class Snip(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        print("Snip initialized...")


class MainMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        QtWidgets.QApplication.restoreOverrideCursor()
        self.setGeometry(0, 0, 100, 50)
        button = QtWidgets.QPushButton('Snip', self)
        button.clicked.connect(self.on_pushButton_clicked)
 
    def on_pushButton_clicked(self):
        self.window = TransparentOverlay()
        self.window.show()
        self.hide()
   
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()
