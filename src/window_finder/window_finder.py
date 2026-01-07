import win32gui

class Beholder:
    def __init__(self):
        self.hwnd = self.encontrar_janela_cookie()
        self.rect = self.get_window_rect()

    def encontrar_janela_cookie(self):
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

    def get_window_rect(self):

        if self.hwnd:
            rect = win32gui.GetWindowRect(self.hwnd)
            return {"top": rect[1], "left": rect[0], "width": rect[2]-rect[0], "height": rect[3]-rect[1]}
        return None