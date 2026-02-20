class Origin():
    horizontal = {"LEFT", "CENTER", "RIGHT"}
    vertical = {"TOP", "CENTER", "BOTTOM"}
    
    def __init__(self, horizontal, vertical):
       self.horizontal = horizontal
       self.vertical = vertical

    def get_origin(self):
        return { 
            self.horizontal, 
            self.vertical 
        }