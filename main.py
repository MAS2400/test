import sys
if sys.platform == "win32":
    try:
        import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
from ui.app import App

if __name__ == '__main__':
    App().mainloop()
