import time
from datetime import datetime
from src.action.clicker import clicar_no_biscoito
from src.vision.cookie_vision import CookieVision

ENABLE_GOLDEN_COOKIE   = True
ENABLE_STORE           = True
ENABLE_UPGRADES        = True
ENABLE_STRUCTURES      = True
ENABLE_HAND_OF_FATE    = True
ENABLE_POP_UP_KILLER   = True
ENABLE_SUGAR_CLICKING  = True
DEBUG_MODE             = False

INTERVALO_GOLDEN_COOKIE = 1.0
INTERVALO_LOJA = 5.0
INTERVALO_POP_UP_KILLER = 300
INTERVALO_HAND_OF_FATE = 600
INTERVALO_SUGAR = 3600

SUGAR_PERC_X = 0.307
SUGAR_PERC_Y = 0.1

def beholder_eyes():
    inicio = datetime.now()

    vision = CookieVision(debug=DEBUG_MODE)

    ultima_verificacao_visao = 0
    ultima_verificacao_loja = 0
    ultima_verificacao_killer = 0
    ultima_verificacao_hand_of_fate = 0
    ultima_verificacao_sugar = 0

    qtd_golden_cookies = 0
    qtd_upgrades = 0
    qtd_loja = 0
    lista_loja = []
    qtd_hand_of_fate = 0
    qtd_pop_ups_mortas = 0

    x_dinamico_sugar = int(vision.rect["width"] * SUGAR_PERC_X)
    y_dinamico_sugar = int(vision.rect["height"] * SUGAR_PERC_Y)

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
            if ENABLE_GOLDEN_COOKIE:
            # Verificação de Visão
                if tempo_atual - ultima_verificacao_visao >= INTERVALO_GOLDEN_COOKIE:
                    #print(f"[{time.strftime('%H:%M:%S')}] Verificando Golden Cookie...")
                    ponto_golden = vision.find_any_golden()
                    if ponto_golden:
                        print(f"[{time.strftime('%H:%M:%S')}] Golden Cookie!")
                        clicar_no_biscoito(vision.hwnd, ponto_golden[0], ponto_golden[1])
                        qtd_golden_cookies += 1

                    ultima_verificacao_visao = tempo_atual

            # Lógica da Loja
            if ENABLE_STORE:
                if tempo_atual - ultima_verificacao_loja >= INTERVALO_LOJA:
                    
                    comprou_upgrade = False

                    if ENABLE_UPGRADES:
                        # PRIORIDADE 1
                        #print(f"[{time.strftime('%H:%M:%S')}] Verificando Upgrades...")
                        ponto_upgrade = vision.get_upgrade()
                        if ponto_upgrade:
                            print(f"[{time.strftime('%H:%M:%S')}] Comprei Upgrade")
                            clicar_no_biscoito(vision.hwnd, ponto_upgrade[0], ponto_upgrade[1])
                            time.sleep(0.5)
                            qtd_upgrades += 1
                            comprou_upgrade = True

                        # PRIORIDADE 2
                    if ENABLE_STRUCTURES and not comprou_upgrade:
                            comprar = vision.get_structure()
                            #print(f"verificando itens_disponiveis: {itens_disponiveis}")
                            if comprar:
                                # Clica no urtimo
                                print(f"[{time.strftime('%H:%M:%S')}] Comprei estrutura da loja")
                                clicar_no_biscoito(vision.hwnd, comprar[0][0], comprar[0][1])
                                qtd_loja += 1
                                lista_loja.append(comprar[1])



                    ultima_verificacao_loja = tempo_atual

            # HAND OF FATE
            if ENABLE_HAND_OF_FATE:
                if tempo_atual - ultima_verificacao_hand_of_fate >= INTERVALO_HAND_OF_FATE:
                    #print(f"[{time.strftime('%H:%M:%S')}] Verificando Hand of Fate...")
                    ponto_hand_of_fate = vision.hand_of_fate()
                    if ponto_hand_of_fate:
                        print(f"[{time.strftime('%H:%M:%S')}] Hand of Fate detectado!")
                        clicar_no_biscoito(vision.hwnd, ponto_hand_of_fate[0], ponto_hand_of_fate[1])
                        qtd_hand_of_fate += 1

                    ultima_verificacao_hand_of_fate = tempo_atual

            # POP-UP KILLER
            if ENABLE_POP_UP_KILLER:
                if tempo_atual - ultima_verificacao_killer >= INTERVALO_POP_UP_KILLER:
                    #print(f"[{time.strftime('%H:%M:%S')}] Verificando pop-ups...")
                    ponto_pop_up = vision.close_pop_ups()
                    if ponto_pop_up:
                        print(f"[{time.strftime('%H:%M:%S')}] Pop-up morto!")
                        clicar_no_biscoito(vision.hwnd, ponto_pop_up[0], ponto_pop_up[1])
                        qtd_pop_ups_mortas += 1
                
                    ultima_verificacao_killer = tempo_atual

            # SUGAR CLICKER
            if ENABLE_SUGAR_CLICKING:
                if tempo_atual - ultima_verificacao_sugar >= INTERVALO_SUGAR:
                    x_dinamico_sugar = int(vision.rect["width"] * SUGAR_PERC_X)
                    y_dinamico_sugar = int(vision.rect["height"] * SUGAR_PERC_Y)
                    clicar_no_biscoito(vision.hwnd, x_dinamico_sugar, y_dinamico_sugar)
                    #print(f"local do click açucar: {x_dinamico_sugar}, {y_dinamico_sugar}")

                    ultima_verificacao_sugar = tempo_atual

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
        print(f"Lista de estruturas compradas na loja: {list(set(lista_loja))}")
        print(f"Hand of Fate clicados: {qtd_hand_of_fate}")
        print(f"Pop-ups mortos: {qtd_pop_ups_mortas}")
        print("\nBot encerrado.")


beholder_eyes()