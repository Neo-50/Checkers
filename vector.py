class Vector:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def tuple(self):
        return (self.x, self.y)