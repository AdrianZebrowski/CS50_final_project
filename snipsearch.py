import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import mss
import mss.tools
import pytesseract
import numpy
import webbrowser

# TODO: Attempt to import settings from a defaults file, and if there aren't then initialize the object as it currently is

settings = {
    'save': False,
    'search': True,
    'save_path': '',
    'search_engine': 'Wolfram Alpha'
}

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
        return self


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
        if settings['save'] == True:
            Snip(self.start_point, self.end_point).save()
        if settings['search'] == True:
            if settings['search_engine'] == 'Google':
                Snip(self.start_point, self.end_point).ocr().search_google()
            if settings['search_engine'] == 'Bing':
                Snip(self.start_point, self.end_point).ocr().search_bing()
            if settings['search_engine'] == 'Yahoo':
                Snip(self.start_point, self.end_point).ocr().search_yahoo()
            if settings['search_engine'] == 'Wolfram Alpha':
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

# TODO: Path box for save
# TODO: Add keyboard shortcuts (CTRL+1 = snip, CTRL+2 = snip + save, CTRL+G = google, CTRL+W for wolfram, etc.)
class MainMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.save = False
        self.save_path = ""
        self.search = False
        self.search_engine = ""
        QtWidgets.QApplication.restoreOverrideCursor()
        self.setGeometry(0, 0, 100, 50)
        layout = QtWidgets.QHBoxLayout()

        self.b1 = QtWidgets.QPushButton('Snip', self)
        self.b1.clicked.connect(self.on_pushButton_clicked)
        layout.addWidget(self.b1)

        self.c1 = QtWidgets.QCheckBox("Save", self)
        self.c1.setChecked(settings['save'])
        layout.addWidget(self.c1)

        self.c2 = QtWidgets.QCheckBox("Search", self)
        self.c2.setChecked(settings['search'])
        layout.addWidget(self.c2)

        self.combo = QtWidgets.QComboBox(self)
        self.combo.addItem("Google")
        self.combo.addItem("Bing")
        self.combo.addItem("Yahoo")
        self.combo.addItem("Wolfram Alpha")
        self.combo.setCurrentText(settings['search_engine'])
        self.combo.activated[str].connect(self.dropdown_state)
        layout.addWidget(self.combo)

        self.setLayout(layout)
        
    def checkbox_state(self, c):
        if c.text() == "Save":
            if c.isChecked() == True:
                settings['save'] = True
            else:
                settings['save'] = False

        if c.text() == "Search":
            if c.isChecked() == True:
                settings['search'] = True
            else:
                settings['search'] = False

    def dropdown_state(self, text):
        print(text)
        settings['search_engine'] = text
  
    def on_pushButton_clicked(self):
        self.checkbox_state(self.c2)
        self.checkbox_state(self.c1)
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

# TODO: Package this in an installer and try it out on different operating systems
