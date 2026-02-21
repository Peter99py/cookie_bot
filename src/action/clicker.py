import logging

import pywintypes
import win32api
import win32con
import win32gui

logger = logging.getLogger(__name__)


def clicar_no_biscoito(hwnd: int, x: int, y: int) -> None:
    """Envia click esquerdo na posição (x, y) da janela via PostMessage."""
    lparam = win32api.MAKELONG(x, y)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)


def scroll_no_cookie(hwnd: int, x: int, y: int, clicks: int) -> None:
    """Envia evento de scroll na posição (x, y) da janela.

    Args:
        hwnd: Handle da janela alvo.
        x: Coordenada X em client-space.
        y: Coordenada Y em client-space.
        clicks: Quantidade de 'ticks' de scroll (positivo = cima, negativo = baixo).
    """
    try:
        point = win32gui.ClientToScreen(hwnd, (x, y))
        lparam = win32api.MAKELONG(point[0], point[1])
    except pywintypes.error as e:
        logger.warning("ClientToScreen falhou (hwnd=%s, x=%s, y=%s): %s", hwnd, x, y, e)
        return

    delta = clicks * 120
    
    wparam = delta << 16
    
    win32gui.PostMessage(hwnd, win32con.WM_MOUSEWHEEL, wparam, lparam)