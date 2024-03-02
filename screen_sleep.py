import subprocess
from threading import Timer
from pynput import keyboard, mouse

# Global timer variable
timer = None

# Time of inactivity (5 minutes) in seconds
INACTIVITY_PERIOD = 300

def turn_screen_off():
    """Turns the screen off by using the xset command."""
    subprocess.call('xset dpms force off', shell=True)

def reset_timer():
    """Resets the inactivity timer."""
    global timer
    if timer is not None:
        timer.cancel()
    timer = Timer(INACTIVITY_PERIOD, turn_screen_off)
    timer.start()

def on_press(key):
    """Callback for keyboard events."""
    reset_timer()

def on_click(x, y, button, pressed):
    """Callback for mouse click events."""
    if pressed:
        reset_timer()

def on_move(x, y):
    """Callback for mouse movement events."""
    reset_timer()

def on_scroll(x, y, dx, dy):
    """Callback for mouse scroll events."""
    reset_timer()

# Initialize the timer
reset_timer()

# Set up listeners for keyboard and mouse
keyboard_listener = keyboard.Listener(on_press=on_press)
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

keyboard_listener.start()
mouse_listener.start()

keyboard_listener.join()
mouse_listener.join()
