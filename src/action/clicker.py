import win32api
import win32con
import win32gui

def clicar_no_biscoito(hwnd, x, y):
    lparam = win32api.MAKELONG(x, y)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)

def scroll_no_cookie(hwnd, x, y, clicks):
    try:
        point = win32gui.ClientToScreen(hwnd, (x, y))
        lparam = win32api.MAKELONG(point[0], point[1])
    except Exception:
        return

    delta = clicks * 120
    
    wparam = delta << 16
    
    win32gui.PostMessage(hwnd, win32con.WM_MOUSEWHEEL, wparam, lparam)