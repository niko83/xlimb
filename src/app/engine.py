import app


class Engine:
    def __init__(self, consumption=3, fuel_amount=100):
        self.consumption = consumption
        self.fuel_amount = fuel_amount
        self.power = 1000

    @property
    def is_ready(self):
        return self.fuel_amount > 0

    def acceleration(self):
        self.fuel_amount -= self.consumption * app.constants.FRAME_INTERVAL
        if self.fuel_amount < 0:
            self.fuel_amount = 0
