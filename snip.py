import mss
import mss.tools
from pynput.mouse import Listener

x1 = 0
y1 = 0
x2 = 0
y2 = 0

def on_click(x, y, button, pressed):
    if pressed:
        x1 = x
        y1 = y
        print(f"Pressed at ({x1},{y1})")
    else:
        x2 = x
        y2 = y
        print(f"Released at ({x2},{y2})")
        # Stop listener
        return False

with Listener(on_click=on_click) as listener:
    listener.join()

with mss.mss() as sct:
    # Use the 1st monitor
    monitor = sct.monitors[1]

    # Capture a bbox using percent values
    left = monitor["left"] + monitor["width"] * 5 // 100  # 5% from the left
    top = monitor["top"] + monitor["height"] * 5 // 100  # 5% from the top
    right = left + 400  # 400px width
    lower = top + 400  # 400px height
    bbox = (left, top, right, lower)

    # Grab the picture
    # Using PIL would be something like:
    # im = ImageGrab(bbox=bbox)
    im = sct.grab(bbox)  # type: ignore

    # Save it!
    mss.tools.to_png(im.rgb, im.size, output="screenshot.png")

if __name__=="__main__":
    print("file is being run directly")
else:
    print("file is being imported as module")