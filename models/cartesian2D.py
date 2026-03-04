class Cartesian2D():
    x = 10.0,
    y = 0

    def __init__(self, input_x: float, input_y: float):
        self.x = input_x
        self.y = input_y

    def get2DCoordinates(self):
        return [
            self.x, self.y
        ]