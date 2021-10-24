from dataclasses import dataclass


@dataclass()
class Point:
    x: int
    y: int

    def __add__(self, other):
        if type(other) == tuple:
            other = Point(*other)
        return Point(self.x + other.x, self.y + other.y)

    def __iter__(self):
        return iter((self.x, self.y))


    def asTuple(self):
        return self.x, self.y