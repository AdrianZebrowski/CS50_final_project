import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import mss
import mss.tools
import pytesseract
import numpy
import webbrowser

# TODO: Make the screenshotted image pop up in a screen (maybe in MainMenu?)

class Snip():
    def __init__(self, start_point, end_point):

        self.left = min(start_point.x(), end_point.x())
        self.right = max(start_point.x(), end_point.x())
        self.top = min(start_point.y(), end_point.y())
        self.lower = max(start_point.y(), end_point.y())
        self.bbox = (self.left, self.top, self.right, self.lower)

        with mss.mss() as sct:
            # TODO: Make this work with multiple monitors
            # Use the 1st monitor
            self.monitor = sct.monitors[1]
            self.im = sct.grab(self.bbox)

    def ocr(self):
        self.im_rgb = numpy.flip(numpy.array(self.im, dtype=numpy.uint8)[:, :, :3], 2) # BGRA -> RGB conversion
        self.ocr_text = pytesseract.image_to_string(self.im_rgb)
        return self

    def search_google(self):
        url = "https://www.google.com/search?q={}".format(self.ocr_text)
        webbrowser.open_new_tab(url)

    def search_bing(self):
        url = "https://www.bing.com/search?q={}".format(self.ocr_text)
        webbrowser.open_new_tab(url)

    def search_yahoo(self):
        url = "https://search.yahoo.com/search?p={}".format(self.ocr_text)
        webbrowser.open_new_tab(url)

    def search_wolfram(self):
        url = "https://www.wolframalpha.com/input/?i={}".format(self.ocr_text)
        webbrowser.open_new_tab(url)

    def save(self):
        mss.tools.to_png(self.im.rgb, self.im.size, output="screenshot.png")


class TransparentOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(0.1)
        # TODO: Set this up so it uses the window sizing
        screen_width = 1920
        screen_height = 1200
        self.setGeometry(0, 0, screen_width, screen_height)
        self.end_point = QtCore.QPoint()
        self.start_point = QtCore.QPoint()

    def mousePressEvent(self, event):
        # print("Mouse pressed.")
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.update()
        # print(self.end_point.x(), self.end_point.y())

    def mouseReleaseEvent(self, event):
        Snip(self.start_point, self.end_point).ocr().search_wolfram()
        # Snip(self.start_point, self.end_point).save()
        # print("Mouse released.")
        # print(self.end_point.x(), self.end_point.y())
        self.window = MainMenu()
        self.window.show()
        self.close()
        
    def mouseMoveEvent(self, event):
        # print("Mouse moved.")
        self.end_point = event.pos()
        self.update()
        # print(self.end_point.x(), self.end_point.y())

# TODO: Add checkboxes for Save, path box for save, Search, and a dropdown for search engines
# TODO: Add keyboard shortcuts (CTRL+1 = snip, CTRL+2 = snip + save, CTRL+G = google, CTRL+W for wolfram, etc.)
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
