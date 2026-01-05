import win32gui

def encontrar_janela_cookie():
    # Busca o identificador (HWND) da janela.
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            titulo = win32gui.GetWindowText(hwnd)
            if titulo.endswith("Cookie Clicker"):
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None