import time
from datetime import datetime
from src.action.clicker import clicar_no_biscoito
from src.vision.cookie_vision import CookieVision

ENABLE_GOLDEN_COOKIE   = True
ENABLE_UPGRADES        = True
ENABLE_STORE           = True
ENABLE_POP_UP_KILLER   = True
DEBUG_MODE             = True

INTERVALO_GOLDEN_COOKIE = 1.0
INTERVALO_LOJA = 5.0
INTERVALO_POP_UP_KILLER = 300

def beholder_eyes():
    inicio = datetime.now()

    vision = CookieVision(debug=DEBUG_MODE)

    ultima_verificacao_visao = 0
    ultima_verificacao_loja = 0
    ultima_verificacao_killer = 0

    qtd_golden_cookies = 0
    qtd_upgrades = 0
    qtd_loja = 0
    qtd_pop_ups_mortas = 0

    if vision.rect:
        print("Janela do jogo encontrada.")
    else:
        print("Janela do jogo não encontrada.")
        return

    print("Visão computacional iniciada! Pressione Ctrl+C para parar.")
    print(f"Flags: Golden:{ENABLE_GOLDEN_COOKIE}, Upgrades:{ENABLE_UPGRADES}, Loja:{ENABLE_STORE}, Killer:{ENABLE_POP_UP_KILLER}")

    try:
        while True:
            tempo_atual = time.time()

            # Verificação de Visão
            if tempo_atual - ultima_verificacao_visao >= INTERVALO_GOLDEN_COOKIE:
                if ENABLE_GOLDEN_COOKIE:
                    ponto_golden = vision.find_any_golden()
                    if ponto_golden:
                        print(f"[{time.strftime('%H:%M:%S')}] Golden Cookie!")
                        clicar_no_biscoito(vision.hwnd, ponto_golden[0], ponto_golden[1])
                        qtd_golden_cookies += 1

                    ultima_verificacao_visao = tempo_atual

            # Lógica da Loja
            if tempo_atual - ultima_verificacao_loja >= INTERVALO_LOJA:
                if ENABLE_UPGRADES:    
                    # PRIORIDADE 1
                    ponto_upgrade = vision.get_upgrade_status()
                    if ponto_upgrade:
                        print(f"[{time.strftime('%H:%M:%S')}] Comprei Upgrade")
                        clicar_no_biscoito(vision.hwnd, ponto_upgrade[0], ponto_upgrade[1])
                        time.sleep(0.5)
                        qtd_upgrades += 1

                    # PRIORIDADE 2
                    if ENABLE_STORE:
                        itens_disponiveis = vision.get_store_status()
                        if itens_disponiveis:
                            # Clica no urtimo
                            alvo_compra = itens_disponiveis[-1]
                            print(f"[{time.strftime('%H:%M:%S')}] Comprei estrutura da loja")
                            clicar_no_biscoito(vision.hwnd, alvo_compra[0], alvo_compra[1])
                            qtd_loja += 1

                ultima_verificacao_loja = tempo_atual

            if tempo_atual - ultima_verificacao_killer >= INTERVALO_POP_UP_KILLER:
                if ENABLE_POP_UP_KILLER:
                    ponto_pop_up = vision.close_pop_ups()
                    if ponto_pop_up:
                        clicar_no_biscoito(vision.hwnd, ponto_pop_up[0], ponto_pop_up[1])
                        qtd_pop_ups_mortas += 1

            time.sleep(0.01)

    except KeyboardInterrupt:
        fim = datetime.now()
        duracao = fim - inicio
        print("\nResumo da sessão:")
        print(f"início: {inicio.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"fim: {fim.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"Duração: {duracao}")
        print(f"Golden Cookies: {qtd_golden_cookies}")
        print(f"Upgrades: {qtd_upgrades}")
        print(f"Loja: {qtd_loja}")
        print(f"Pop-ups mortos: {qtd_pop_ups_mortas}")
        print("\nBot encerrado.")


beholder_eyes()