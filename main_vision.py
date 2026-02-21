import time
from datetime import datetime
from src.action import clicar_no_biscoito, scroll_no_cookie
from src.vision import CookieVision

ENABLE_GOLDEN_COOKIE   = True
ENABLE_STORE           = True
ENABLE_UPGRADES        = True
ENABLE_STRUCTURES      = True
ENABLE_HAND_OF_FATE    = True
ENABLE_POP_UP_KILLER   = True
ENABLE_SUGAR_CLICKING  = True
ENABLE_GREEN_LETTERS   = True
DEBUG_MODE             = False

INTERVALO_GOLDEN_COOKIE = 0.4
INTERVALO_LOJA = 2
INTERVALO_POP_UP_KILLER = 150
INTERVALO_HAND_OF_FATE = 150
INTERVALO_SUGAR = 3500
INTERVALO_GREEN_L = 1

SUGAR_PERC_X = 0.307
SUGAR_PERC_Y = 0.1

GREEN_LETTERS_X = 0.52
GREEN_LETTERS_Y = 0.04

def _check_golden_cookie(vision: CookieVision, stats: dict, timers: dict) -> None:
    """Verifica e clica em Golden/Wrath cookies."""
    if not ENABLE_GOLDEN_COOKIE:
        return
    tempo_atual = timers["atual"]
    if tempo_atual - timers["golden"] < INTERVALO_GOLDEN_COOKIE:
        return

    ponto_golden = vision.find_any_golden()
    if ponto_golden:
        print(f"[{time.strftime('%H:%M:%S')}] {ponto_golden[2]}")
        clicar_no_biscoito(vision.hwnd, ponto_golden[0], ponto_golden[1])
        stats["golden_cookies"] += 1

    timers["golden"] = tempo_atual


def _check_store(vision: CookieVision, stats: dict, timers: dict) -> None:
    """Verifica e compra upgrades e estruturas da loja."""
    if not ENABLE_STORE:
        return
    tempo_atual = timers["atual"]
    if tempo_atual - timers["loja"] < INTERVALO_LOJA:
        return

    if ENABLE_UPGRADES:
        scroll_no_cookie(vision.hwnd, (vision.right_block_x_start + 70), (vision.upgrade_y_start + 70), 10)
        time.sleep(1.2)
        ponto_upgrade = vision.get_upgrade()
        if ponto_upgrade[0] is not None:
            clicar_no_biscoito(vision.hwnd, ponto_upgrade[0][0], ponto_upgrade[0][1])
            time.sleep(0.2)
            stats["upgrades"] += 1

        if ENABLE_STRUCTURES:
            _check_structures(vision, stats)

    timers["loja"] = tempo_atual


def _check_structures(vision: CookieVision, stats: dict) -> None:
    """Verifica e compra estruturas da loja (scroll para baixo e para cima)."""
    scroll_no_cookie(vision.hwnd, (vision.right_block_x_start + 70), (vision.upgrade_y_start + 70), -10)
    time.sleep(1.2)
    comprar = vision.get_structure()
    if comprar[0] is not None:
        clicar_no_biscoito(vision.hwnd, comprar[0][0], comprar[0][1])
        time.sleep(0.5)
        stats["loja"] += 1
    else:
        scroll_no_cookie(vision.hwnd, (vision.right_block_x_start + 70), (vision.upgrade_y_start + 70), 10)
        time.sleep(1.2)
        comprar = vision.get_structure()
        if comprar[0] is not None:
            clicar_no_biscoito(vision.hwnd, comprar[0][0], comprar[0][1])
            stats["loja"] += 1
            time.sleep(0.5)


def _check_hand_of_fate(vision: CookieVision, stats: dict, timers: dict) -> None:
    """Verifica e clica em Hand of Fate."""
    if not ENABLE_HAND_OF_FATE:
        return
    tempo_atual = timers["atual"]
    if tempo_atual - timers["hand_of_fate"] < INTERVALO_HAND_OF_FATE:
        return

    ponto = vision.hand_of_fate()
    if ponto:
        print(f"[{time.strftime('%H:%M:%S')}] Hand of Fate detectado!")
        clicar_no_biscoito(vision.hwnd, ponto[0], ponto[1])
        stats["hand_of_fate"] += 1

    timers["hand_of_fate"] = tempo_atual


def _check_pop_up_killer(vision: CookieVision, stats: dict, timers: dict) -> None:
    """Verifica e fecha pop-ups."""
    if not ENABLE_POP_UP_KILLER:
        return
    tempo_atual = timers["atual"]
    if tempo_atual - timers["killer"] < INTERVALO_POP_UP_KILLER:
        return

    ponto = vision.pop_up_killer()
    if ponto:
        print(f"[{time.strftime('%H:%M:%S')}] Pop-up morto!")
        clicar_no_biscoito(vision.hwnd, ponto[0], ponto[1])
        stats["pop_ups"] += 1

    timers["killer"] = tempo_atual


def _check_sugar(vision: CookieVision, rect: dict, timers: dict) -> None:
    """Clica na posição do açúcar periodicamente."""
    if not ENABLE_SUGAR_CLICKING:
        return
    tempo_atual = timers["atual"]
    if tempo_atual - timers["sugar"] < INTERVALO_SUGAR:
        return

    x = int(rect["width"] * SUGAR_PERC_X)
    y = int(rect["height"] * SUGAR_PERC_Y)
    clicar_no_biscoito(vision.hwnd, x, y)

    timers["sugar"] = tempo_atual


def _check_green_letters(vision: CookieVision, rect: dict, timers: dict) -> None:
    """Clica na posição das letras verdes periodicamente."""
    if not ENABLE_GREEN_LETTERS:
        return
    tempo_atual = timers["atual"]
    if tempo_atual - timers["green_l"] < INTERVALO_GREEN_L:
        return

    x = int(rect["width"] * GREEN_LETTERS_X)
    y = int(rect["height"] * GREEN_LETTERS_Y)
    clicar_no_biscoito(vision.hwnd, x, y)

    timers["green_l"] = tempo_atual


def _print_session_summary(inicio: datetime, stats: dict) -> None:
    """Imprime resumo da sessão ao encerrar."""
    fim = datetime.now()
    duracao = fim - inicio
    print("\nResumo da sessão:")
    print(f"início: {inicio.strftime('%d-%m-%Y %H:%M:%S')}")
    print(f"fim: {fim.strftime('%d-%m-%Y %H:%M:%S')}")
    print(f"Duração: {duracao}")
    print(f"Golden Cookies: {stats['golden_cookies']}")
    print(f"Upgrades: {stats['upgrades']}")
    print(f"Loja: {stats['loja']}")
    print(f"Hand of Fate clicados: {stats['hand_of_fate']}")
    print(f"Pop-ups mortos: {stats['pop_ups']}")
    print("\nBot encerrado.")


def beholder_eyes() -> None:
    """Loop principal do bot — orquestra todas as verificações."""
    inicio = datetime.now()

    vision = CookieVision(debug=DEBUG_MODE)

    scroll_no_cookie(vision.hwnd, (vision.right_block_x_start + 70), (vision.upgrade_y_start + 70), 10)
    time.sleep(1.2)
    vision.check_store_y()

    rect = vision.rect
    if not rect:
        print("Janela do jogo não encontrada.")
        return

    print("Janela do jogo encontrada.")
    print(f"Flags: Golden:{ENABLE_GOLDEN_COOKIE}, Upgrades:{ENABLE_UPGRADES}, Loja:{ENABLE_STORE}, Killer:{ENABLE_POP_UP_KILLER}")

    stats = {
        "golden_cookies": 0,
        "upgrades": 0,
        "loja": 0,
        "hand_of_fate": 0,
        "pop_ups": 0,
    }

    timers = {
        "golden": 0.0,
        "loja": 0.0,
        "killer": 0.0,
        "hand_of_fate": 0.0,
        "sugar": 0.0,
        "green_l": 0.0,
        "atual": 0.0,
    }

    try:
        while True:
            timers["atual"] = time.time()

            _check_golden_cookie(vision, stats, timers)
            _check_store(vision, stats, timers)
            _check_hand_of_fate(vision, stats, timers)
            _check_pop_up_killer(vision, stats, timers)
            _check_sugar(vision, rect, timers)
            _check_green_letters(vision, rect, timers)

            time.sleep(0.01)

    except KeyboardInterrupt:
        _print_session_summary(inicio, stats)


if __name__ == "__main__":
    beholder_eyes()