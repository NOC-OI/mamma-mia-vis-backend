class Cartesian2D():
    x = 10.0,
    y = 0

    def __init__(self, inputX: float, inputY: float):
        self.x = inputX
        self.y = inputY

    def get2DCoordinates(self):
        return [
            self.x, self.y
        ]