# Cookie Bot

Bot automatizado para o jogo Cookie Clicker que realiza cliques no biscoito principal, coleta cookies dourados, compra upgrades e itens na loja.

## Funcionalidades

O bot executa as seguintes ações de forma automática:

- **Cliques no Biscoito Principal**: Realiza múltiplos cliques no biscoito do jogo com posicionamento dinâmico baseado na resolução da janela.
- **Detecção de Cookies Dourados**: Utiliza visão computacional para localizar e clicar em cookies dourados quando aparecem na tela.
- **Compra de Upgrades**: Detecta quando upgrades estão disponíveis na loja e realiza a compra automaticamente.
- **Compra na Loja**: Identifica itens disponíveis para compra na loja e compra o item de maior prioridade.
- **Estatísticas de Sessão**: Rastreia e exibe o número de cookies dourados coletados, upgrades comprados e itens da loja adquiridos.

## Como Funciona

### Detecção de Cookies Dourados

O módulo `cookie_vision.py` utiliza técnicas de processamento de imagem:

- Captura a janela do jogo em tempo real
- Aplica detecção de cor HSV para localizar pixels dourados
- Filtra por opacidade para evitar elementos semi-transparentes
- Utiliza operações morfológicas para refinar a detecção
- Encontra contornos e calcula o centro de cada cookie dourado

### Detecção de Upgrades

Analisa a seção de upgrades da loja:

- Captura a região dos upgrades
- Extrai o canal V (brilho) da imagem em HSV
- Detecta disponibilidade comparando o brilho médio
- Retorna as coordenadas para clique

### Detecção da Loja

Monitora a seção de compras:

- Divide a área da loja em itens de altura fixa
- Calcula o brilho médio de cada item
- Identifica quais itens podem ser comprados
- Prioriza o item com maior índice (normalmente o mais lucrativo)

### Sistema de Cliques

O módulo `clicker.py` usa as APIs do Windows:

- Envia mensagens de clique (WM_LBUTTONDOWN e WM_LBUTTONUP)
- Opera diretamente na janela do jogo

### Localização da Janela

O módulo `window_finder.py`:

- Enumera todas as janelas visíveis
- Procura por janelas com título terminado em "Cookie Clicker"
- Retorna o identificador (HWND) para operação