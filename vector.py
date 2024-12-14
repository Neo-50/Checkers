class Vector:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def tuple(self):
        return (self.x, self.y)