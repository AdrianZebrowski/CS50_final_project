import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import mss
import mss.tools
import pytesseract
import numpy
import webbrowser
import json
import datetime


class Snip(QtWidgets.QWidget):
    def __init__(self, bbox):
        super().__init__()
        
        self.bbox = bbox
        with mss.mss() as sct:
            # TODO: Make this work with multiple monitors if at all possible
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
        path = settings['save_path'] + 'screenshot_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + '.png'
        mss.tools.to_png(self.im.rgb, self.im.size, output=path)
        return self


class TransparentOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        screen_geometry = QtWidgets.QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen_geometry.width(), screen_geometry.height())
        self.end_point = QtCore.QPoint()
        self.start_point = QtCore.QPoint()
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.left = 0
        self.right = 1
        self.top = 0
        self.bottom = 1

    def mousePressEvent(self, event):
        # print("Mouse pressed.")
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.update()
        # print(self.end_point.x(), self.end_point.y())

    def mouseReleaseEvent(self, event):
        self.bbox = (self.left, self.top, self.right, self.bottom)
        if settings['save'] == True:
            Snip(self.bbox).save()
        if settings['search'] == True:
            if settings['search_engine'] == 'Google':
                Snip(self.bbox).ocr().search_google()
            if settings['search_engine'] == 'Bing':
                Snip(self.bbox).ocr().search_bing()
            if settings['search_engine'] == 'Yahoo':
                Snip(self.bbox).ocr().search_yahoo()
            if settings['search_engine'] == 'Wolfram Alpha':
                Snip(self.bbox).ocr().search_wolfram()

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
        self.left = min(self.start_point.x(), self.end_point.x())
        self.right = max(self.start_point.x(), self.end_point.x())
        self.top = min(self.start_point.y(), self.end_point.y())
        self.bottom = max(self.start_point.y(), self.end_point.y())
        # print(self.end_point.x(), self.end_point.y())

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen_width = 2
        painter.setPen(QtGui.QPen(QtCore.Qt.red, pen_width, QtCore.Qt.SolidLine))
        painter.drawRect(self.left - int(0.5 * pen_width), self.top - int(0.5 * pen_width), self.right - self.left + pen_width, self.bottom - self.top + pen_width)

# TODO: Add keyboard shortcuts (CTRL+S = snip, CTRL+V = snip + save, CTRL+G = google, CTRL+W for wolfram, etc. I can iron out the details later)

class MainMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        QtWidgets.QApplication.restoreOverrideCursor()
        self.setGeometry(0, 0, 100, 50)
        layout = QtWidgets.QGridLayout()

        self.b1 = QtWidgets.QPushButton('Snip', self)
        self.b1.clicked.connect(self.on_b1_clicked)
        layout.addWidget(self.b1)

        self.c1 = QtWidgets.QCheckBox("Save", self)
        self.c1.setChecked(settings['save'])
        self.c1.stateChanged.connect(lambda: self.checkbox_state(self.c1))
        layout.addWidget(self.c1)

        self.b2 = QtWidgets.QPushButton('Browse', self)
        self.b2.clicked.connect(self.on_b2_clicked)
        layout.addWidget(self.b2)

        self.textbox = QtWidgets.QLineEdit(self)
        if settings['save_path'] == '':
            self.textbox.setPlaceholderText("Enter snip directory here...")
        else:
            self.textbox.setText('{}'.format(settings['save_path']))
        self.textbox.textChanged[str].connect(self.textbox_state)
        layout.addWidget(self.textbox)

        self.c2 = QtWidgets.QCheckBox("Search", self)
        self.c2.setChecked(settings['search'])
        self.c2.stateChanged.connect(lambda: self.checkbox_state(self.c2))
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
        settings['search_engine'] = text

    def textbox_state(self):
        settings['save_path'] = self.textbox.text().rstrip("/") + "/"

    def on_b2_clicked(self):
        self.dialog = QtWidgets.QFileDialog()
        self.folder_path = self.dialog.getExistingDirectory(None, "Select Folder")
        self.textbox.setText('{}'.format(self.folder_path))
  
    def on_b1_clicked(self):
        self.window = TransparentOverlay()
        self.window.show()
        self.hide()

    def closeEvent(self, event):
        print("Writing last settings to json file...")
        with open('settings.json', 'w') as file:
            json.dump(settings, file)
        event.accept()

def main():

    def default_settings():
        print("No last settings found. Using default settings...")
        global settings
        settings = {
            'save': False,
            'search': False,
            'save_path': '',
            'search_engine': 'Google'
        }

    try:
        with open('settings.json') as file:
            try:
                global settings 
                settings = json.load(file)
                print("Loading last settings from file...")
            except:
                print("No last settings found. Using default settings...")
                default_settings()
    except:
        default_settings()

    app = QtWidgets.QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()

# TODO: Package this in an installer and try it out on different operating systems
