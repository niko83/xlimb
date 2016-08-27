
import app


class Gun:
    def __init__(self, rate_fire=0.5, ammo_count=20):
        self.rate_fire = rate_fire
        self.reloading = 0
        self.ammo_count = ammo_count

    def refresh(self):
        self.reloading -= app.constants.FRAME_INTERVAL

    @property
    def is_ready(self):
        return self.reloading <= 0 and self.ammo_count

    def shot(self):
        self.reloading = self.rate_fire
        self.ammo_count -= 1
