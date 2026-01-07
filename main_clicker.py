import time
from datetime import datetime
from src.action.clicker import clicar_no_biscoito
from src.window_finder.window_finder import Beholder

ENABLE_CLICKING        = True
ENABLE_SUGAR_CLICKING  = True

PERC_X = 0.20
PERC_Y = 0.45
SUGAR_PERC_X = 0.307
SUGAR_PERC_Y = 0.1
INTERVALO_SUGAR = 3600

def flaming_fingers():
    inicio = datetime.now()

    beholder = Beholder()

    ultima_verificacao_sugar = 0
    qtd_cliques = 0

    if beholder.rect:
        print("Janela do jogo encontrada.")
    else:
        print("Janela do jogo não encontrada.")
        return

    x_dinamico = int(beholder.rect["width"] * PERC_X)
    y_dinamico = int(beholder.rect["height"] * PERC_Y)

    x_dinamico_sugar = int(beholder.rect["width"] * SUGAR_PERC_X)
    y_dinamico_sugar = int(beholder.rect["height"] * SUGAR_PERC_Y)

    print("Clicker iniciado! Pressione Ctrl+C para parar.")
    try:
        while True:
            tempo_atual = time.time()

            # Cliques no açúcar
            if tempo_atual - ultima_verificacao_sugar >= INTERVALO_SUGAR:
                if ENABLE_SUGAR_CLICKING:
                    clicar_no_biscoito(beholder.hwnd, x_dinamico_sugar, y_dinamico_sugar)
                    print(f"local do click açucar: {x_dinamico_sugar}, {y_dinamico_sugar}")

                ultima_verificacao_sugar = tempo_atual

            # Cliques no biscoito principal
            if ENABLE_CLICKING:
                for _ in range(60):
                    clicar_no_biscoito(beholder.hwnd, x_dinamico, y_dinamico)
                    qtd_cliques += 1
                    time.sleep(0.0333)  # o jogo não consegue processar corretamente cliques muito rápidos

            x_dinamico = int(beholder.rect["width"] * PERC_X)
            y_dinamico = int(beholder.rect["height"] * PERC_Y)

            # Anti derretimento da CPU
            time.sleep(0.01)
        

    except KeyboardInterrupt:
        fim = datetime.now()
        duracao = fim - inicio
        print("\nResumo da sessão:")
        print(f"início: {inicio.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"fim: {fim.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"Duração: {duracao}")
        print(f"Total de cliques no biscoito: {qtd_cliques}")
        print("\nBot encerrado.")


flaming_fingers()