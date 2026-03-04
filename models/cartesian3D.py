class Cartesian3D():
    x = 0,
    y = 0,
    z = 0

    def __init__(self, input_x: float, input_y: float, input_z: float):
        self.x = input_x
        self.y = input_y
        self.z = input_z

    def get3DCoordinates(self):
        return [
            self.x, self.y, self.z
        ]