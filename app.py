import pygame
import constants
from node import Node


class App:
    INSTANCE: "App|None" = None

    def __init__(self, width: int, height: int) -> None:
        if self.INSTANCE:
            raise Exception("Application already running")

        # Set instance
        self.INSTANCE = self

        # Initialize
        pygame.init()
        self.running = False
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

    @property
    def height(self) -> int:
        return self.screen.get_height()

    @property
    def width(self) -> int:
        return self.screen.get_width()

    def loop(self):
        self.running = True
        
        while self.running:
            # compute
            Node.process_all_nodes()

            for event in pygame.event.get():
                if event.type == pygame.constants.QUIT:
                    self.running = False

                # listen
                Node.handle_event_for_nodes(event)

            self.screen.fill(constants.COLOR_BLACK)

            # paint
            Node.paint_all_nodes(self.screen)
            
            pygame.display.flip()

        # quit
        pygame.quit()
