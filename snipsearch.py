# Import necessary modules
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import mss
import mss.tools
# Special tesseract related line of code for windows version goes here
import pytesseract
import numpy
import webbrowser
import json
import datetime

# Define a class called snip, which takes a screenshot when provided with a bounding box, and then does several functions with it depending on some settings
class Snip(QtWidgets.QWidget):
    def __init__(self, bbox):
        # Initialize superclass so we have access to its methods
        super().__init__()
        # Take the screenshot using mss module, use a context here (memory management issues arise with mss otherwise, generally more pythonic too)
        with mss.mss() as sct:
            self.im = sct.grab(bbox)

    # Define a function for ocr (optical character recognition) using pytesseract
    def ocr(self):
        # Convert the image to RGB using some numpy array trickery (SOURCE: https://stackoverflow.com/questions/50588376/is-there-a-way-to-use-mss-and-pytesseract-witchout-saving-and-open)
        self.im_rgb = numpy.flip(numpy.array(self.im, dtype=numpy.uint8)[:, :, :3], 2)
        # Convert the image to text via pytesseract ocr
        self.ocr_text = pytesseract.image_to_string(self.im_rgb)
        # Have the method return self so we can daisy chain it with the search and save methods below
        return self

    # The following functions simply search the ocr output text using google, bing, yahoo, or wolfram alpha (my favorite)
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
    
    # Save function
    def save(self):
        # Create a path to save the file to, include a timestamp in the filename (also guarantees uniqueness)
        self.path = settings['save_path'] + 'screenshot_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + '.png'
        mss.tools.to_png(self.im.rgb, self.im.size, output=self.path)
        return self

# Initialize a class to create a transparent overlay, on which I will draw selection boxes (like snipping tool in Windows)
class TransparentOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Get that sweet cross cursor (again like snipping tool)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        # Have the window stay on top, make it frameless
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # Get the screen geometry and use it to set the geometry of this transparent overlay
        self.screen_geometry = QtWidgets.QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, self.screen_geometry.width(), self.screen_geometry.height())
        # Make the overlay transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # Declare start point and end point variables as qpoints (x, y coordinate pairs, essentially)
        self.end_point = QtCore.QPoint()
        self.start_point = QtCore.QPoint()
        # Declare variables for the boundaries of the selection box (make it 1x1 pixels initially, this prevents a bug where if no selection
        # box is drawn the entire screen is captured and OCR'd)
        self.left = 0
        self.right = 1
        self.top = 0
        self.bottom = 1

    # Define a method that updates the start point and end point when the mouse button is pressed
    def mousePressEvent(self, event):
        # print("Mouse pressed.")
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.update()
        # print(self.end_point.x(), self.end_point.y())

    # Define a method that, if the mouse is released, will define a bounding box based on the start and end point coordinate pairs and
    # then will pass this bounding box to the Snip class and invoke some methods based on settings
    def mouseReleaseEvent(self, event):
        self.left = min(self.start_point.x(), self.end_point.x())
        self.right = max(self.start_point.x(), self.end_point.x())
        self.top = min(self.start_point.y(), self.end_point.y())
        self.bottom = max(self.start_point.y(), self.end_point.y())
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
        # At this point, call the MainMenu class again (to the window variable) and then show it, and then close up the transparent overlay
        self.window = MainMenu()
        self.window.show()
        self.close()
    
    # Define a method that updates the end point variable when the mouse is moved
    def mouseMoveEvent(self, event):
        # print("Mouse moved.")
        self.end_point = event.pos()
        self.update()
        # print(self.end_point.x(), self.end_point.y())

    # Define a method that paints a box on the transparent window
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen_width = 2
        painter.setPen(QtGui.QPen(QtCore.Qt.red, pen_width, QtCore.Qt.SolidLine))
        # Little bit of math to make the box drawn around, but not over, the screen area that the program will capture
        painter.drawRect(self.left - int(0.5 * pen_width), self.top - int(0.5 * pen_width), self.right - self.left + pen_width, self.bottom - self.top + pen_width)


# Define a class for the main menu of the application
class MainMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Restore the cursor back to the normal cursor (since it may have been over-ridden by the TransparentOverlay class)
        QtWidgets.QApplication.restoreOverrideCursor()
        self.setGeometry(0, 0, 100, 50)
        layout = QtWidgets.QGridLayout()

        # Button to start snipping
        self.b1 = QtWidgets.QPushButton('Snip', self)
        self.b1.clicked.connect(self.on_b1_clicked)
        layout.addWidget(self.b1)

        # Button to enable saving the snipped image
        self.c1 = QtWidgets.QCheckBox("Save", self)
        self.c1.setChecked(settings['save'])
        # Call a function to check the state of the checkbox when it is checked or unchecked
        self.c1.stateChanged.connect(lambda: self.checkbox_state(self.c1))
        layout.addWidget(self.c1)

        # Button to open up a directory browser (to select where you are saving screenshots to)
        self.b2 = QtWidgets.QPushButton('Browse', self)
        self.b2.clicked.connect(self.on_b2_clicked)
        layout.addWidget(self.b2)

        # Textbox to enter the directory to save images to
        self.textbox = QtWidgets.QLineEdit(self)
        # Prompt the user for an entry if the path is empty
        if settings['save_path'] == '':
            self.textbox.setPlaceholderText("Enter snip directory here...")
        else:
            self.textbox.setText('{}'.format(settings['save_path']))
        self.textbox.textChanged[str].connect(self.textbox_state)
        layout.addWidget(self.textbox)

        # Checkbox to enable searching for the ocr text from the snipped image
        self.c2 = QtWidgets.QCheckBox("Search", self)
        self.c2.setChecked(settings['search'])
        self.c2.stateChanged.connect(lambda: self.checkbox_state(self.c2))
        layout.addWidget(self.c2)

        # Combo box for selecting search engines
        self.combo = QtWidgets.QComboBox(self)
        self.combo.addItem("Google")
        self.combo.addItem("Bing")
        self.combo.addItem("Yahoo")
        self.combo.addItem("Wolfram Alpha")
        self.combo.setCurrentText(settings['search_engine'])
        self.combo.activated[str].connect(self.dropdown_state)
        layout.addWidget(self.combo)

        self.setLayout(layout)

        # Keyboard shortcut to start snipping (just call the same function as clicking the snip button)
        self.shortcut1 = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+S"), self)
        self.shortcut1.activated.connect(self.on_b1_clicked)
    
    # Function to check the state of the checkbox and update the settings dict accordingly (this is really so that 
    # the application remembers your settings)
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

    # Function to check dropdown text and update the settings dict with it
    def dropdown_state(self, text):
        settings['search_engine'] = text
    
    # Function to check the textbox state and update the save path in the settings dict with it, also ensures it ends with /
    def textbox_state(self):
        settings['save_path'] = self.textbox.text().rstrip("/") + "/"

    # When the Browse button is clicked, open a filedialog (directory browser) and set the textbox value to whatever the user browses to
    def on_b2_clicked(self):
        self.dialog = QtWidgets.QFileDialog()
        self.folder_path = self.dialog.getExistingDirectory(None, "Select Folder")
        self.textbox.setText('{}'.format(self.folder_path))
  
    # If the snip button is clicked, TransparentOverlay class is called, that window is shown, and the menu window is hidden
    def on_b1_clicked(self):
        self.window = TransparentOverlay()
        self.window.show()
        self.hide()

    # Define a close event method to write the current settings to a json file
    def closeEvent(self, event):
        print("Writing last settings to json file...")
        with open('settings.json', 'w') as file:
            json.dump(settings, file)
        event.accept()

# Define the main function of the program
def main():

    # Define a function to create some default settings, if the program cannot find or read the json file with last settings in it
    def default_settings():
        print("No last settings found. Using default settings...")
        global settings
        settings = {
            'save': False,
            'search': False,
            'save_path': '',
            'search_engine': 'Google'
        }

    # Try/except structure to try opening settings file, call default settings if we can't even open the file
    try:
        with open('settings.json') as file:
            # Try/except structure to try loading the settings file, call default settings if we can't load the contents
            try:
                global settings 
                settings = json.load(file)
                print("Loading last settings from file...")
            except:
                print("No last settings found. Using default settings...")
                default_settings()
    except:
        default_settings()

    # Some boilerplate code to actually start the application, show the main menu, etc.
    app = QtWidgets.QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
 
 # If this script is being run as the main function (not imported as a module), run the main function
if __name__ == '__main__':
    main()

# TODO: Windows conversion
# TODO: Add feature to put image or ocr'd text into clipboard for windows version
# TODO: Package this in an installer and try it out on different operating systems
