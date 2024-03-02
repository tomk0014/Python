from serial_handler import read_from_arduino
from screen_sleep import setup_screen_sleep

def main():
    setup_screen_sleep()
    read_from_arduino()

if __name__ == "__main__":
    main()
