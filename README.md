# SnipSearch
#### Video Demo:  <https://www.youtube.com/watch?v=0ATa79NQKpk>
#### Description: A multi-functional, cross platform (Windows and Mac) snipping tool with optical character recognition (OCR) capabilities

SnipSearch is a tool I made that expands on the functionality of the Snipping Tool application that comes standard with Windows. I had the idea of writing a snipping tool that was cross-platform in Python, and later decided to make things more interesting by building in additional functionality. 

The features of SnipSearch are described below:

1. Automatic saving: One thing that irks me about the snipping tool in Windows is that you have to manually save the screenshot every time, which gets annoying if you want to quickly capture multiple screenshots. SnipSearch prompts the user for a directory, and if this directory is provided (it can either be browsed to, or typed directly into the text box) and the "Save" checkbox is checked, screenshots will be automatically saved to this directory in .png format.

2. Automatic searching: SnipSearch uses pytesseract, a Python module that permits usage of the Tesseract OCR engine (made by Google). If the "Search" textbox is checked, SnipSearch will use pytesseract to detect text in the screenshot, and will automatically search the internet using Google, Bing, Yahoo, or WolframAlpha (niche, but my personal favorite) for that text.

3. Clipboard functionality (Windows only for now): SnipSearch will automatically place the screenshot image (as a .png) or the OCR text into your clipboard on Windows. This is convenient for quickly pasting a screenshot into a Word document or Microsoft Paint, and is something that requires an additional step with the standard Windows snipping tool. Once I find an analogue for the Win32Clipboard module on Mac OS, I will implement this there as well.

SnipSearch is written in Python, with main files "snipsearch mac.py" and "snipsearch windows.py" containing the program itself for Mac OS and Windows respectively. An additional settings.json file is written that stores user settings, which gives the program the ability to remember settings between sessions. The PyQt5 module is used extensively, and is used to generate all GUI objects and effects (such as the selection box). This module also obtains screen information, and collects cursor position information that is then used to draw the selection box and ultimately used to determine the bounding box that defines the screenshot. The PIL module is used for its screen capture (ImageGrab) and image manipulation capabilities. Pytesseract is used for optical character recognition. Other modules include: sys, webbrowser, json, datetime, and win32clipboard.

Some immediate next steps for this tool include porting the clipboard functionality to the Mac OS version, handling exceptions when an invalid directory is provided and screenshot saving functionality is enabled, and general clean-up.
