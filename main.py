import time
from src.finder.window_finder import encontrar_janela_cookie
from src.action.clicker import clicar_no_biscoito
from src.vision.cookie_vision import CookieVision

ENABLE_GOLDEN_COOKIE = True
ENABLE_UPGRADES      = True
ENABLE_STORE         = True
ENABLE_CLICKING      = True
DEBUG_MODE           = False

PERC_X = 0.20
PERC_Y = 0.45
INTERVALO_VISAO = 1.0
INTERVALO_LOJA = 5.0

def main():
    hwnd_jogo = encontrar_janela_cookie()
    if not hwnd_jogo:
        print("Erro: Janela do Cookie Clicker não encontrada.")
        return

    vision = CookieVision(debug=DEBUG_MODE)
    ultima_verificacao_visao = 0
    ultima_verificacao_loja = 0
    
    rect = vision.get_window_rect()
    x_dinamico = int(rect["width"] * PERC_X)
    y_dinamico = int(rect["height"] * PERC_Y)

    print("Bot iniciado! Pressione Ctrl+C para parar.")
    print(f"Bot iniciado! Flags: Golden:{ENABLE_GOLDEN_COOKIE}, Upgrades:{ENABLE_UPGRADES}, Loja:{ENABLE_STORE}, Cliques:{ENABLE_CLICKING}")

    try:
        while True:
            tempo_atual = time.time()

            # Verificação de Visão
            if tempo_atual - ultima_verificacao_visao >= INTERVALO_VISAO:
                if ENABLE_GOLDEN_COOKIE:
                    ponto_golden = vision.find_any_golden()
                    if ponto_golden:
                        print(f"[{time.strftime('%H:%M:%S')}] Golden Cookie!")
                        clicar_no_biscoito(hwnd_jogo, ponto_golden[0], ponto_golden[1])
                    
                    rect = vision.get_window_rect()
                    if rect:
                        x_dinamico = int(rect["width"] * PERC_X)
                        y_dinamico = int(rect["height"] * PERC_Y)
                    ultima_verificacao_visao = tempo_atual

            # Lógica da Loja
            if tempo_atual - ultima_verificacao_loja >= INTERVALO_LOJA:
                if ENABLE_UPGRADES:    
                    if rect:
                        # PRIORIDADE 1
                        ponto_upgrade = vision.get_upgrade_status(rect)
                        if ponto_upgrade:
                            print(f"[{time.strftime('%H:%M:%S')}] Comprei Upgrade")
                            clicar_no_biscoito(hwnd_jogo, ponto_upgrade[0], ponto_upgrade[1])
                            time.sleep(0.5)

                    # PRIORIDADE 2
                    if ENABLE_STORE:
                        itens_disponiveis = vision.get_store_status(rect)
                        if itens_disponiveis:
                            # Clica no urtimo
                            alvo_compra = itens_disponiveis[-1]
                            print(f"[{time.strftime('%H:%M:%S')}] Comprei estrutura da loja")
                            clicar_no_biscoito(hwnd_jogo, alvo_compra[0], alvo_compra[1])

                ultima_verificacao_loja = tempo_atual

            # Cliques no biscoito principal
            if ENABLE_CLICKING:
                for _ in range(15):
                    clicar_no_biscoito(hwnd_jogo, x_dinamico, y_dinamico)
            
            # Anti derretimento da CPU
            time.sleep(0.01) 

    except KeyboardInterrupt:
        print("\nBot encerrado.")


main()