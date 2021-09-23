import mss
import mss.tools
from pynput.mouse import Listener

x1, y1, x2, y2 = 0, 0, 0, 0

def on_click(x, y, button, pressed):
    global x1, y1, x2, y2
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

left = min(x1, x2)
right = max(x1, x2)
top = min(y1, y2)
lower = max(y1, y2)
bbox = (left, top, right, lower)

with mss.mss() as sct:
    # Use the 1st monitor
    monitor = sct.monitors[1]
    
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