import pygame
import random
import constants
from app import App
from node import Node


class RandomPositonGenerator:
    def __init__(self, bounds: pygame.Rect, minimum_distance: float) -> None:
        """Creates random position"""
        self.bounds = bounds
        self.randomizer = random.Random()
        self.minimum_distance = minimum_distance
        self.generated_positions: list[pygame.Vector2] = []

    def generate(self) -> tuple[float, float]:
        while True:
            x_bounds = self.bounds.x, self.bounds.w - self.bounds.x
            y_bounds = self.bounds.y, self.bounds.h - self.bounds.y

            x = self.randomizer.randint(*x_bounds)
            y = self.randomizer.randint(*y_bounds)

            vec = pygame.Vector2(x, y)
            if len(self.generated_positions) == 0:
                break
            else:
                smallest_dist = min(
                    [vec.distance_to(i) for i in self.generated_positions]
                )
                if smallest_dist <= self.minimum_distance:
                    continue
                break

        self.generated_positions.append(vec)
        return x, y


def colordepth(position: int, maximumvalue: int) -> pygame.Color:
    percentage = int((position / maximumvalue) * 100)

    # Normalize percentage to be between 0 and 1
    percentage = min(100, max(0, percentage)) / 100.0

    # Interpolate between hot (red) and cold (blue) using HSL color space
    hue = (1.0 - percentage) * 240.0  # 240 degrees is blue, 0 degrees is red
    saturation = 100.0
    lightness = 50.0
    alpha = 100.0

    color = pygame.Color(0, 0, 0)
    color.hsla = (hue, saturation, lightness, alpha)
    return color


class NearestNeighbourController(Node):

    @staticmethod
    def _pairstr(cache: list[str], str1: str, str2: str) -> bool:
        str1str2 = f"{str1}:{str2}"
        str2str1 = f"{str2}:{str1}"
        return str1str2 in cache or str2str1 in cache

    def __init__(self, minthreshold: float, maxthreshold: float) -> None:
        super().__init__(0, 0)
        self.minthreshold = minthreshold
        self.maxthreshold = maxthreshold
        self.neighbour_pairs: list[tuple[Body, Body, float]] = []

    def _process(self) -> None:
        self.neighbour_pairs = []
        checked_pair_cache: list[str] = []

        for body in Body.BODIES:
            # reset weigth
            body.weight = 1

        for body in [*Body.BODIES]:
            for other_body in Body.BODIES:
                # avoid self comparison
                if other_body.id == body.id:
                    continue

                # check if we've compared this pair
                if NearestNeighbourController._pairstr(
                    checked_pair_cache, body.id, other_body.id
                ):
                    continue

                # check for proximity
                distance = body.pos.distance_to(other_body.pos)
                if int(distance) in range(
                    int(self.minthreshold), int(self.maxthreshold)
                ):
                    # these guys are neigbours
                    body.weight += 1
                    other_body.weight += 1
                    self.neighbour_pairs.append((body, other_body, distance))

                # if it not in the threshold range, and it's closer
                # create a new one close to thier center, if thier weight is smaller than 6
                elif distance < self.minthreshold and (
                    body.weight < 6 or other_body.weight < 6
                ):
                    rect = pygame.Rect(body.pos, other_body.pos)
                    center = rect.center
                    Body(
                        random.randint(center[0] - 50, center[0] + 50),
                        random.randint(center[1] - 50, center[1] + 50),
                    )

                # cache that we've checked this pair
                checked_pair_cache.append(f"{body.id}:{other_body.id}")

        for body in [*Body.BODIES]:
            # Kill if it has no neigbour (1) or if it has too much (6)
            if body.weight == 1 or body.weight > 6:
                body.destroy()
                del body

        for pair in self.neighbour_pairs:
            b1 = pair[0]
            b2 = pair[1]
            distance = pair[2]

            if (b1.weight > 3) or (b2.weight > 3):
                # pair with a another random node
                b1.pos.move_towards_ip(b2.pos, -(0.08 / b1.weight))
                b2.pos.move_towards_ip(b1.pos, -(0.08 / b2.weight))
                continue

            b1.pos.move_towards_ip(b2.pos, 0.08 / b1.weight)
            b2.pos.move_towards_ip(b1.pos, 0.08 / b2.weight)

    def _paint(self, surface: pygame.Surface) -> None:
        for neighbours in self.neighbour_pairs:
            pygame.draw.line(
                surface,
                colordepth(int(neighbours[2]), int(self.maxthreshold)),
                neighbours[0].pos,
                neighbours[1].pos,
            )


class Body(Node):
    BODIES: list["Body"] = []

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        color: pygame.Color = constants.COLOR_WHITE,
        width: float = 5,
        height: float = 5,
    ) -> None:
        super().__init__(x, y)
        self.color = color
        self.width = width
        self.height = height
        self.weight = 1
        self.BODIES.append(self)

    def _paint(self, surface: pygame.Surface) -> None:
        rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # draw body
        pygame.draw.rect(
            surface,
            self.color,
            rect,
        )

        # draw weight
        line_end = pygame.Vector2(rect.center)
        line_end.y += self.weight

        pygame.draw.line(surface, constants.COLOR_RED, rect.center, line_end)

    def _process(self) -> None:
        # print(self.weight)
        pass

    def destroy(self):
        index = self.BODIES.index(self)
        del self.BODIES[index]
        super().destroy()


app = App(1200, 900)
sparser = RandomPositonGenerator(pygame.Rect(100, 100, 1100, 800), 30)

# controller
NearestNeighbourController(20, 200)

for _ in range(50):
    x, y = sparser.generate()
    Body(x, y)


app.loop()
