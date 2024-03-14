import uuid
import typing
import pygame
from pygame.event import Event
from pygame.surface import Surface


class Node:
    NODES: list["Node"] = []

    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.id = str(uuid.uuid4())
        self.pos = pygame.Vector2(x, y)

        # optimization flags
        self.can_process: bool = True
        self.can_be_painted: bool = True
        self.can_listen_for: list[int] | typing.Literal[True] = []

        # include
        self.NODES.append(self)

    def _process(self) -> None:
        """Perform computations"""
        pass

    def _listen(self, event: Event) -> None:
        """Listens for event"""
        pass

    def _paint(self, surface: Surface) -> None:
        """Draws on the surface"""
        pass

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    @x.setter
    def x(self, v):
        self.pos.x = v

    @y.setter
    def y(self, v):
        self.pos.y = v

    @typing.final
    @staticmethod
    def process_all_nodes():
        for node in Node.NODES:
            if node.can_process:
                node._process()

    @typing.final
    @staticmethod
    def handle_event_for_nodes(event: Event):
        for node in Node.NODES:
            if node.can_listen_for == True or event.type in node.can_listen_for:
                node._listen(event)

    @typing.final
    @staticmethod
    def paint_all_nodes(surface: Surface):
        for node in Node.NODES:
            if node.can_be_painted:
                node._paint(surface)

    def destroy(self):
        index = self.NODES.index(self)
        del self.NODES[index]