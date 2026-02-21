import win32gui

class Beholder:
    def __init__(self):
        self.hwnd = self.encontrar_janela_cookie()
        self.rect = None
        self.update_rect()
        self.janelas_filhas = self.listar_janelas_filhas(self.hwnd) if self.hwnd else []

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
    
    def listar_janelas_filhas(self, parent_hwnd):
        filhas = []
        def callback(hwnd, lista):
            classe = win32gui.GetClassName(hwnd)
            titulo = win32gui.GetWindowText(hwnd)
            lista.append(hwnd)
            return True
        
        win32gui.EnumChildWindows(parent_hwnd, callback, filhas)
        return filhas

    def get_window_rect(self):
        """Retorna o rect atual da janela sem alterar self.rect (método puro)."""
        if self.hwnd:
            rect = win32gui.GetWindowRect(self.hwnd)
            return {"top": rect[1],
                    "left": rect[0],
                    "width": rect[2]-rect[0],
                    "height": rect[3]-rect[1]}
        return None

    def update_rect(self):
        """Atualiza self.rect com a posição atual da janela."""
        self.rect = self.get_window_rect()