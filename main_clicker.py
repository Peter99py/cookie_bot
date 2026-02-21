import time
from datetime import datetime
from src.action.clicker import clicar_no_biscoito
from src.window_finder.window_finder import Beholder

ENABLE_CLICKING        = True
ENABLE_SUGAR_CLICKING  = True

PERC_X = 0.15
PERC_Y = 0.40

def flaming_fingers():
    inicio = datetime.now()

    beholder = Beholder()

    qtd_cliques = 0

    if beholder.rect:
        print("Janela do jogo encontrada.")
    else:
        print("Janela do jogo não encontrada.")
        return

    x_dinamico = int(beholder.rect["width"] * PERC_X)
    y_dinamico = int(beholder.rect["height"] * PERC_Y)

    print("Clicker iniciado! Pressione Ctrl+C para parar.")
    try:
        while True:
            # Cliques no biscoito principal
            if ENABLE_CLICKING:
                x_dinamico = int(beholder.rect["width"] * PERC_X)
                y_dinamico = int(beholder.rect["height"] * PERC_Y)
                for _ in range(60):
                    clicar_no_biscoito(beholder.hwnd, x_dinamico, y_dinamico)
                    qtd_cliques += 1
                    time.sleep(0.0333)  # o jogo não consegue processar corretamente cliques muito rápidos

            time.sleep(0.001)
        

    except KeyboardInterrupt:
        fim = datetime.now()
        duracao = fim - inicio
        print("\nResumo da sessão:")
        print(f"início: {inicio.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"fim: {fim.strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"Duração: {duracao}")
        print(f"Total de cliques no biscoito: {qtd_cliques}")
        print("\nBot encerrado.")


if __name__ == "__main__":
    flaming_fingers()