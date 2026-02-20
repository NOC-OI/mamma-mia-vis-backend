class Colour():
    red_channel = 255,
    green_channel = 255,
    blue_channel = 255,
    alpha_channel = 255

    def __init__(self, red, blue, green, alpha):
        self.red_channel = red
        self.blue_channel = blue
        self.green_channel = green
        self.alpha_channel = alpha

    def get_rgba(self):
        return [            
            self.red_channel,
            self.blue_channel,
            self.green_channel,
            self.alpha_channel 
        ]
        
