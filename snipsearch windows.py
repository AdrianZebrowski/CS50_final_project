# Import necessary modules
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import pytesseract
import webbrowser
import json
import datetime
from io import BytesIO
import win32clipboard
from PIL import ImageGrab

# Tesseract related line of code for windows version goes here (you need to point this thing to your tesseract installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract - OCR\tesseract.exe'

# Function for taking screenshot using PIL module
def Screenshot(bbox):
    im = ImageGrab.grab(bbox)
    return im

# Define a class called snipfunctions, which takes a PIL image object as input and then manipulates it in a few useful ways
class SnipFunctions():
    def __init__(self, im):
        self.im = im

    # Define a function for ocr (optical character recognition) using pytesseract
    def ocr(self):
        # Convert the image to text via pytesseract ocr
        self.ocr_text = pytesseract.image_to_string(self.im)
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
        self.path = settings['save_path'].rstrip("/") + "/" + 'screenshot_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + '.png'
        self.im.save(self.path, 'PNG')
        return self

    # Windows-specific clipboard functions
    def clip_image(self):
        # print("Clipped the image!")
        self.im_bytes = BytesIO()
        self.im.convert('RGB').save(self.im_bytes, 'BMP')
        self.clip_data = self.im_bytes.getvalue()[14:]
        self.im_bytes.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, self.clip_data)
        win32clipboard.CloseClipboard()

    def clip_text(self):
        # print("Clipped the text!")
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(self.ocr_text)
        win32clipboard.CloseClipboard()
        

# Initialize a class to create a transparent overlay, on which I will draw selection boxes (like snipping tool in Windows)
class SnippingOverlay(QtWidgets.QWidget):
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
        self.setWindowOpacity(0.25)
        # Declare start point and end point variables as qpoints (x, y coordinate pairs, essentially)
        self.end_point = QtCore.QPoint()
        self.start_point = QtCore.QPoint()
        # Declare variables for the boundaries of the selection box (make it 1x1 pixels initially, this prevents a bug where if no selection
        # box is drawn the entire screen is captured and OCR'd - very slow!)
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
        self.bbox = (self.left, self.top, self.right, self.bottom)
        self.setWindowOpacity(0)
        self.im = Screenshot(self.bbox)

        # Save the image if this setting is enabled
        if settings['save'] == True and settings['save_path'] != '':
            SnipFunctions(self.im).save()
        
        # Windows-specific call to clipboard functions 
        if settings['clipboard'] == "image":
            SnipFunctions(self.im).clip_image()
        if settings['clipboard'] == "text":
            SnipFunctions(self.im).ocr().clip_text()

        # Search the OCR'd text
        if settings['search'] == True:
            if settings['search_engine'] == 'Google':
                SnipFunctions(self.im).ocr().search_google()
            if settings['search_engine'] == 'Bing':
                SnipFunctions(self.im).ocr().search_bing()
            if settings['search_engine'] == 'Yahoo':
                SnipFunctions(self.im).ocr().search_yahoo()
            if settings['search_engine'] == 'Wolfram Alpha':
                SnipFunctions(self.im).ocr().search_wolfram()

        #print("Mouse released.")
        #print(self.end_point.x(), self.end_point.y())
        # At this point, call the MainMenu class again (to the window variable) and then show it, and then close up the transparent overlay
        self.window = MainMenu()
        self.window.show()
        self.close()
    
    # Define a method that updates the end point variable when the mouse is moved
    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        self.left = min(self.start_point.x(), self.end_point.x())
        self.right = max(self.start_point.x(), self.end_point.x())
        self.top = min(self.start_point.y(), self.end_point.y())
        self.bottom = max(self.start_point.y(), self.end_point.y())
        # print("Mouse moved.")
        self.update()
        # print(self.end_point.x(), self.end_point.y())

    # Define a method that paints a box on the transparent window
    def paintEvent(self, event):
        #print("PAINTING")
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

        # Windows-specific controls for clipboard functionality
        self.rlabel1 = QtWidgets.QLabel("Clipboard functionality:")

        self.r1 = QtWidgets.QRadioButton("None")
        self.r1.setChecked(settings['clipboard'] == 'none')
        self.r1.toggled.connect(lambda: self.radiobox_state(self.r1))

        self.r2 = QtWidgets.QRadioButton("OCR Text")
        self.r2.setChecked(settings['clipboard'] == 'text')
        self.r2.toggled.connect(lambda: self.radiobox_state(self.r2))

        self.r3 = QtWidgets.QRadioButton("Image")
        self.r3.setChecked(settings['clipboard'] == 'image')
        self.r3.toggled.connect(lambda: self.radiobox_state(self.r3))

        self.rgroup1 = QtWidgets.QButtonGroup()
        self.rgroup1.addButton(self.r1)
        self.rgroup1.addButton(self.r2)
        self.rgroup1.addButton(self.r3)

        layout.addWidget(self.rlabel1)
        layout.addWidget(self.r1)
        layout.addWidget(self.r2)
        layout.addWidget(self.r3)

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

    def radiobox_state(self, r):
        if r.text() == "OCR Text" and r.isChecked() == True:
            settings['clipboard'] = "text"
            #print(settings['clipboard'])
        if r.text() == "Image" and r.isChecked() == True:
            settings['clipboard'] = "image"
            #print(settings['clipboard'])
        if r.text() == "None" and r.isChecked() == True:
            settings['clipboard'] = "none"
            #print(settings['clipboard'])

    # Function to check dropdown text and update the settings dict with it
    def dropdown_state(self, text):
        settings['search_engine'] = text
    
    # Function to check the textbox state and update the save path in the settings dict with it
    def textbox_state(self):
        settings['save_path'] = self.textbox.text()

    # When the Browse button is clicked, open a filedialog (directory browser) and set the textbox value to whatever the user browses to
    def on_b2_clicked(self):
        self.dialog = QtWidgets.QFileDialog()
        self.folder_path = self.dialog.getExistingDirectory(None, "Select Folder")
        self.textbox.setText('{}'.format(self.folder_path))
  
    # If the snip button is clicked, TransparentOverlay class is called, that window is shown, and the menu window is hidden
    def on_b1_clicked(self):
        self.window = SnippingOverlay()
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
            'save_path': 'C:\\',
            'search_engine': 'Google',
            'clipboard': 'none'
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

##### Partially inspired (at least as far as using PyQt5 as the base for the GUI) by https://github.com/harupy/snipping-tool
##### I found at least one instance of someone else making a snipping tool that searched the internet, so I guess my idea isn't very original, but hey
