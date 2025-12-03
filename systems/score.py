from core.events import Event, EVENT_ENEMY_KILLED, EVENT_COINS_UPDATED, EVENT_UPGRADE_TOWER, EVENT_TOWER_UPGRADED

class ScoreSystem:
    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register(self)
        self.score = 0
        self.coins = 0
        self.debug_score_logs = False

    def notify(self, event):
        if event.name == EVENT_ENEMY_KILLED:
            points = event.data.get('score', 10)
            self.score += points
            coins = event.data.get('coins', 1)
            self.coins += coins
            if self.debug_score_logs:
                print(f"[Score] +{points} points, +{coins} coin. Score: {self.score}, Coins: {self.coins}")
            self.ev_manager.post(Event(EVENT_COINS_UPDATED, data={'coins': self.coins}))
        elif event.name == EVENT_UPGRADE_TOWER:
            cost = event.data.get('cost', 5)
            up_type = event.data.get('type', 'range')
            if self.coins >= cost:
                self.coins -= cost
                if self.debug_score_logs:
                    print(f"[Score] Upgrade '{up_type}' purchased. Coins left: {self.coins}")
                self.ev_manager.post(Event(EVENT_COINS_UPDATED, data={'coins': self.coins}))
                self.ev_manager.post(Event(EVENT_TOWER_UPGRADED, data={'type': up_type, 'cost': cost}))
            else:
                if self.debug_score_logs:
                    print(f"[Score] Not enough coins: {self.coins}/{cost}")
