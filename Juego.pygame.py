import pygame #Liberia de pygame
import random
import sys
import os  # Importación para manejar rutas relativas

# Inicializa pygame
pygame.init()

# Configuración de pantalla compatible con Batocera
ANCHO, ALTO = 640, 480
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Carriles y Obstáculos")

# Colores actualizados
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (50, 50, 50)
ROJO = (255, 0, 0)

# Carriles
CARRILES = [160, 320, 480]

# Velocidades iniciales
FPS = 60
velocidad_juego = 5

# Espaciado mínimo entre enemigos
DISTANCIA_MINIMA_VERTICAL = 150
MAX_COCHES = 2

# Inicialización del joystick
pygame.joystick.init()
joystick = None
joystick_bloqueado = False  # Variable para evitar movimientos múltiples
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Mando detectado: {joystick.get_name()}")

# Ruta base relativa al script
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))

# Función para mostrar texto
def mostrar_texto(texto, x, y, tamaño=36, color=BLANCO, centrado=False):
    fuente = pygame.font.Font(None, tamaño)
    superficie_texto = fuente.render(texto, True, color)
    if centrado:
        x -= superficie_texto.get_width() // 2
    pantalla.blit(superficie_texto, (x, y))

# Función para cargar imágenes
def cargar_imagen(ruta, tamaño):
    imagen = pygame.image.load(ruta)
    return pygame.transform.scale(imagen, tamaño)

# Cargar imágenes de coches
imagen_jugador = cargar_imagen(os.path.join(RUTA_BASE, "Coches", "Coche10Principal.png"), (40, 70))
imagenes_enemigos = [
    cargar_imagen(os.path.join(RUTA_BASE, "Coches", "Coche1.png"), (30, 70)),
    cargar_imagen(os.path.join(RUTA_BASE, "Coches", "Coche2.png"), (30, 70)),
    cargar_imagen(os.path.join(RUTA_BASE, "Coches", "Coche3.png"), (30, 70)),
]

# Clase Jugador
class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = imagen_jugador
        self.rect = self.image.get_rect()
        self.carril = 1
        self.rect.center = (CARRILES[self.carril], ALTO - 100)

    def mover(self, direccion):
        if direccion == -1 and self.carril > 0:
            self.carril -= 1
            self.rect.centerx = CARRILES[self.carril]
        if direccion == 1 and self.carril < len(CARRILES) - 1:
            self.carril += 1
            self.rect.centerx = CARRILES[self.carril]

    def get_hitbox(self):
        """Devuelve un rectángulo reducido para colisiones."""
        return self.rect.inflate(-10, -20)

# Clase Obstáculo
class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, velocidad):
        super().__init__()
        self.image = random.choice(imagenes_enemigos)
        self.rect = self.image.get_rect()
        self.velocidad = velocidad
        self.reposicionar()

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.top > ALTO:
            self.reposicionar()

    def reposicionar(self):
        while True:
            nuevo_carril = random.choice(CARRILES)
            nueva_y = random.randint(-300, -50)
            # Garantizar que no haya coches enemigos demasiado cerca
            if all(abs(nueva_y - o.rect.y) > DISTANCIA_MINIMA_VERTICAL for o in obstaculos if o.rect.centerx == nuevo_carril):
                self.rect.center = (nuevo_carril, nueva_y)
                break

    def get_hitbox(self):
        """Devuelve un rectángulo reducido para colisiones."""
        return self.rect.inflate(-10, -20)

# Función para generar obstáculos iniciales
def generar_obstaculos(velocidad, num_obstaculos=MAX_COCHES):
    obstaculos = []
    for _ in range(num_obstaculos):
        obstaculo = Obstaculo(velocidad)
        obstaculos.append(obstaculo)
    return obstaculos

# Menú de pausa
def mostrar_menu():
    opciones = ["Reanudar", "Salir"]
    seleccion = 0
    while True:
        pantalla.fill(NEGRO)
        mostrar_texto("PAUSA", ANCHO // 2, 50, tamaño=48, color=BLANCO, centrado=True)
        for i, opcion in enumerate(opciones):
            color = ROJO if i == seleccion else BLANCO
            mostrar_texto(opcion, ANCHO // 2, 150 + i * 50, tamaño=36, color=color, centrado=True)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                if evento.key == pygame.K_RETURN:
                    return seleccion
            if joystick:
                eje_y = joystick.get_axis(1)
                if eje_y > 0.5:  # Hacia abajo
                    seleccion = (seleccion + 1) % len(opciones)
                elif eje_y < -0.5:  # Hacia arriba
                    seleccion = (seleccion - 1) % len(opciones)
                if joystick.get_button(0):  # Botón A para seleccionar
                    return seleccion

# Juego principal
def juego():
    global obstaculos, joystick_bloqueado, velocidad_juego
    reloj = pygame.time.Clock()
    puntuacion = 0

    # Grupos de sprites
    todos_sprites = pygame.sprite.Group()
    obstaculos = pygame.sprite.Group()

    # Crear jugador
    jugador = Jugador()
    todos_sprites.add(jugador)

    # Crear obstáculos iniciales
    for obstaculo in generar_obstaculos(velocidad_juego):
        todos_sprites.add(obstaculo)
        obstaculos.add(obstaculo)

    jugando = True

    while jugando:
        direccion = 0
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    direccion = -1
                if evento.key == pygame.K_RIGHT:
                    direccion = 1
                if evento.key == pygame.K_ESCAPE:  # Menú con ESC
                    seleccion = mostrar_menu()
                    if seleccion == 1:
                        pygame.quit()
                        sys.exit()
            if joystick:
                eje_x = joystick.get_axis(0)
                if not joystick_bloqueado:
                    if eje_x < -0.8:  # Izquierda
                        direccion = -1
                        joystick_bloqueado = True
                    elif eje_x > 0.8:  # Derecha
                        direccion = 1
                        joystick_bloqueado = True
                if -0.2 < eje_x < 0.2:  # Desbloquear cuando el joystick está en neutral
                    joystick_bloqueado = False

                if joystick.get_button(7):  # Botón START para pausar
                    seleccion = mostrar_menu()
                    if seleccion == 1:
                        pygame.quit()
                        sys.exit()

        jugador.mover(direccion)
        puntuacion += 1

        # Incrementar la velocidad cada 1000 puntos
        if puntuacion % 1000 == 0:
            velocidad_juego += 0.5
            for obstaculo in obstaculos:
                obstaculo.velocidad = velocidad_juego

        # Detección de colisiones usando hitboxes ajustadas
        for obstaculo in obstaculos:
            if jugador.get_hitbox().colliderect(obstaculo.get_hitbox()):
                mostrar_texto("¡Game Over!", ANCHO // 2, ALTO // 2, tamaño=48, color=ROJO, centrado=True)
                pygame.display.flip()
                pygame.time.wait(2000)
                jugando = False

        pantalla.fill(GRIS)
        for x in CARRILES:
            pygame.draw.line(pantalla, BLANCO, (x - 40, 0), (x - 40, ALTO), 2)
        todos_sprites.update()
        todos_sprites.draw(pantalla)
        mostrar_texto(f"Puntos: {puntuacion}", 10, 10, tamaño=24)
        pygame.display.flip()
        reloj.tick(FPS)

if __name__ == "__main__":
    juego()
