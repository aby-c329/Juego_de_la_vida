import pygame
import time
import os
import numpy as np

class GameOfLife:
    def __init__(self, width=700, height=700, nxC=60, nyC=60, title="Juego de la vida - Clases"):
        # Centro de ventana
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()

        # Parámetros de ventana
        self.width = width
        self.height = height
        self.nxC = nxC
        self.nyC = nyC
        self.dimCW = width / nxC
        self.dimCH = height / nyC
        self.bg = (25, 25, 25)

        # Ventana
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(self.bg)

        # Estado de la rejilla
        self.gameState = np.zeros((nxC, nyC), dtype=int)
        self._init_pattern()

        # Flags de control
        self.pauseExec = True
        self.endGame = False
        self.iteration = 0

        self.clock = pygame.time.Clock()

    def _init_pattern(self):
        # Patrón inicial en el centro
        posX = int((self.nxC/2)-3)
        posY = int((self.nyC/2)-5)
        coords = [
            (0,0),(1,0),(2,0),(3,0),
            (3,1),(3,2),
            (0,3),(3,3),
            (0,4),(1,4),(2,4),(3,4)
        ]
        for dx, dy in coords:
            self.gameState[posX+dx, posY+dy] = 1

    def run(self):
        while not self.endGame:
            newState = self.gameState.copy()
            self.screen.fill(self.bg)
            time.sleep(0.1)

            # Eventos
            self._handle_events(newState)

            # Actualizar si no está en pausa
            if not self.pauseExec:
                self.iteration += 1
                self._update_state(newState)

            # Dibujar
            population = self._draw_cells(newState)
            self.gameState[:] = newState

            # Título
            title = f"Juego de la vida - Clases - Población: {population} - Gen: {self.iteration}"
            if self.pauseExec:
                title += " - [PAUSADO]"
            pygame.display.set_caption(title)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        print("Juego finalizado")

    def _handle_events(self, newState):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.endGame = True
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.endGame = True
                    return
                if event.key == pygame.K_r:
                    self.iteration = 0
                    self.gameState.fill(0)
                    newState.fill(0)
                    self.pauseExec = True
                else:
                    self.pauseExec = not self.pauseExec

        # Mouse
        mouseClick = pygame.mouse.get_pressed()
        if any(mouseClick):
            if mouseClick[1]:
                self.pauseExec = not self.pauseExec
            else:
                x, y = pygame.mouse.get_pos()
                ix, iy = int(x / self.dimCW), int(y / self.dimCH)
                newState[ix, iy] = 0 if self.gameState[ix, iy] else 1

    def _update_state(self, newState):
        for x in range(self.nxC):
            for y in range(self.nyC):
                n = self._count_neighbors(x, y)
                if self.gameState[x, y] == 0 and n == 3:
                    newState[x, y] = 1
                elif self.gameState[x, y] == 1 and (n < 2 or n > 3):
                    newState[x, y] = 0

    def _count_neighbors(self, x, y):
        total = 0
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx or dy:
                    total += self.gameState[(x+dx) % self.nxC, (y+dy) % self.nyC]
        return total

    def _draw_cells(self, state):
        pop = 0
        for x in range(self.nxC):
            for y in range(self.nyC):
                poly = [
                    (int(x*self.dimCW), int(y*self.dimCH)),
                    (int((x+1)*self.dimCW), int(y*self.dimCH)),
                    (int((x+1)*self.dimCW), int((y+1)*self.dimCH)),
                    (int(x*self.dimCW), int((y+1)*self.dimCH)),
                ]
                if state[x, y] == 0:
                    pygame.draw.polygon(self.screen, (128,128,128), poly, 1)
                else:
                    pop += 1
                    color = (128,128,128) if self.pauseExec else (255,255,255)
                    pygame.draw.polygon(self.screen, color, poly, 0)
        return pop

if __name__ == "__main__":
    game = GameOfLife()
    game.run()
