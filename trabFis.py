import pygame
import math
import sys

# Inicialização do Pygame
pygame.init()
largura, altura = 800, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Lançamento Oblíquo com Sistema de Pontuação")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)

# Variáveis de física
g = 9.81  # Aceleração da gravidade
angulo = 45  # Ângulo de lançamento em graus
velocidade_inicial = 50  # Velocidade inicial
t = 0  # Tempo

# Variáveis de controle de sensibilidade
SENSIBILIDADE_ANGULO = 0.5  # Velocidade de mudança do ângulo
SENSIBILIDADE_VELOCIDADE = 0.5  # Velocidade de mudança da velocidade inicial

# Posição inicial do projétil
posicao_inicial_x, posicao_inicial_y = 100, altura - 100
posicao_x, posicao_y = posicao_inicial_x, posicao_inicial_y

# Variáveis de controle para lançamento e jogo
lancado = False
jogo_ativo = True
pontuacao = 0

# Sistema de tempo
tempo_total = 60  # 60 segundos de jogo
tempo_inicial = pygame.time.get_ticks()

# Carrega a imagem do boneco
boneco_img = pygame.image.load("images/character.webp")
boneco_img = pygame.transform.scale(boneco_img, (30, 30))
boneco_largura, boneco_altura = boneco_img.get_size()

# Carrega a imagem de fundo
fundo_img = pygame.image.load("images/background.png").convert()
fundo_img = pygame.transform.scale(fundo_img, (largura, altura))

# Posição e dimensões do alvo
alvo = pygame.image.load("images/alvo.png")
alvo = pygame.transform.scale(alvo, (30, 30))
alvo_x, alvo_y = 650, 450
alvo_raio = 20

def atualizar_posicao_e_velocidade(t, angulo, velocidade_inicial):
    angulo_rad = math.radians(angulo)
    velocidade_inicial_x = velocidade_inicial * math.cos(angulo_rad)
    velocidade_inicial_y = velocidade_inicial * math.sin(angulo_rad)
    x = posicao_inicial_x + velocidade_inicial_x * t
    y = posicao_inicial_y - (velocidade_inicial_y * t - 0.5 * g * t**2)
    return (x, y), (velocidade_inicial_x, velocidade_inicial_y - g * t)

def desenhar_vetor_direcao(x, y, angulo, velocidade_inicial):
    comprimento_vetor = velocidade_inicial * 0.5
    angulo_rad = math.radians(angulo)
    fim_vetor_x = x + comprimento_vetor * math.cos(angulo_rad)
    fim_vetor_y = y - comprimento_vetor * math.sin(angulo_rad)
    pygame.draw.line(tela, AZUL, (int(x), int(y)), (int(fim_vetor_x), int(fim_vetor_y)), 3)

    comprimento_seta = 12
    angulo_seta = math.radians(25)
    ponta1_x = fim_vetor_x - comprimento_seta * math.cos(angulo_rad - angulo_seta)
    ponta1_y = fim_vetor_y + comprimento_seta * math.sin(angulo_rad - angulo_seta)
    ponta2_x = fim_vetor_x - comprimento_seta * math.cos(angulo_rad + angulo_seta)
    ponta2_y = fim_vetor_y + comprimento_seta * math.sin(angulo_rad + angulo_seta)
    pygame.draw.polygon(tela, AZUL, [(fim_vetor_x, fim_vetor_y), (ponta1_x, ponta1_y), (ponta2_x, ponta2_y)])

def verificar_colisao(x1, y1, x2, y2, raio_objeto1, raio_objeto2):
    distancia = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distancia <= (raio_objeto1 + raio_objeto2)

def reposicionar_alvo():
    # Gera uma nova posição aleatória para o alvo
    import random
    novo_x = random.randint(400, largura - 50)
    novo_y = random.randint(100, altura - 100)
    return novo_x, novo_y

def processar_entrada_continua():
    global angulo, velocidade_inicial
    
    # Obtém o estado atual de todas as teclas
    teclas = pygame.key.get_pressed()
    
    if not lancado:
        # Ajusta o ângulo
        if teclas[pygame.K_UP]:
            angulo += SENSIBILIDADE_ANGULO
        if teclas[pygame.K_DOWN]:
            angulo -= SENSIBILIDADE_ANGULO
            
        # Ajusta a velocidade
        if teclas[pygame.K_RIGHT]:
            velocidade_inicial += SENSIBILIDADE_VELOCIDADE
        if teclas[pygame.K_LEFT]:
            velocidade_inicial -= SENSIBILIDADE_VELOCIDADE
        
        # Limita o ângulo entre 0 e 90 graus
        angulo = max(0, min(90, angulo))
        # Limita a velocidade inicial entre 0 e 100
        velocidade_inicial = max(0, min(150, velocidade_inicial))

# Loop principal do jogo
rodando = True
relogio = pygame.time.Clock()

while rodando:
    tela.blit(fundo_img, (0, 0))
    
    # Calcula o tempo restante
    tempo_atual = pygame.time.get_ticks()
    tempo_passado = (tempo_atual - tempo_inicial) // 1000  # Converte para segundos
    tempo_restante = tempo_total - tempo_passado

    # Verifica se o tempo acabou
    if tempo_restante <= 0 and jogo_ativo:
        jogo_ativo = False

    # Eventos de controle
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if jogo_ativo and not lancado and evento.key == pygame.K_RETURN:
                lancado = True
                t = 0
            # Reinicia o jogo quando pressionar ESPAÇO após o tempo acabar
            elif not jogo_ativo and evento.key == pygame.K_SPACE:
                jogo_ativo = True
                tempo_inicial = pygame.time.get_ticks()
                pontuacao = 0
                lancado = False
    
    if jogo_ativo:
        # Processa entrada contínua das teclas
        processar_entrada_continua()

        # Atualiza a posição somente se foi lançado
        if lancado:
            (posicao_x, posicao_y), _ = atualizar_posicao_e_velocidade(t, angulo, velocidade_inicial)
            t += 0.1

            # Verifica colisão com o alvo
            if verificar_colisao(
                posicao_x + boneco_largura // 2, posicao_y + boneco_altura // 2,
                alvo_x, alvo_y,
                max(boneco_largura, boneco_altura) // 2, alvo_raio
            ):
                pontuacao += 1
                lancado = False
                # Reposiciona o alvo após acertar
                alvo_x, alvo_y = reposicionar_alvo()

        else:
            posicao_x, posicao_y = posicao_inicial_x, posicao_inicial_y
            desenhar_vetor_direcao(posicao_x, posicao_y, angulo, velocidade_inicial)

        # Desenha o alvo
        tela.blit(alvo, (int(alvo_x), int(alvo_y)))

        # Desenha a imagem do boneco
        tela.blit(boneco_img, (int(posicao_x), int(posicao_y)))
        
        # Desenha o vetor de direção após o lançamento
        if lancado:
            desenhar_vetor_direcao(posicao_x, posicao_y, angulo, velocidade_inicial)

        # Se o projétil sair da tela, reinicia
        if posicao_y > altura:
            lancado = False
            posicao_x, posicao_y = posicao_inicial_x, posicao_inicial_y

    # Interface do usuário
    fonte = pygame.font.Font(None, 36)
    
    # Mostra informações durante o jogo
    if jogo_ativo:
        texto_angulo = fonte.render(f"Ângulo: {angulo:.1f}°", True, PRETO)
        texto_velocidade = fonte.render(f"Velocidade: {velocidade_inicial:.1f} m/s", True, PRETO)
        texto_pontuacao = fonte.render(f"Pontuação: {pontuacao}", True, VERDE)
        texto_tempo = fonte.render(f"Tempo: {tempo_restante}s", True, VERMELHO)
        
        tela.blit(texto_angulo, (10, 10))
        tela.blit(texto_velocidade, (10, 50))
        tela.blit(texto_pontuacao, (10, 90))
        tela.blit(texto_tempo, (10, 130))
    else:
        # Mostra tela de fim de jogo
        texto_fim = fonte.render("TEMPO ESGOTADO!", True, VERMELHO)
        texto_pontuacao_final = fonte.render(f"Pontuação Final: {pontuacao}", True, VERDE)
        texto_reiniciar = fonte.render("Pressione ESPAÇO para jogar novamente", True, AZUL)
        
        tela.blit(texto_fim, (largura // 2 - 100, altura // 2 - 60))
        tela.blit(texto_pontuacao_final, (largura // 2 - 100, altura // 2))
        tela.blit(texto_reiniciar, (largura // 2 - 200, altura // 2 + 60))

    pygame.display.flip()
    relogio.tick(60)  # Aumentei para 60 FPS para movimento mais suave

pygame.quit()
sys.exit()
