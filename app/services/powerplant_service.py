class Powerplant:
    def __init__(self, name, type, efficiency, pmax, pmin, fuel):
        self.name = name
        self.type = type
        self.efficiency = efficiency
        self.pmax = pmax
        self.pmin = pmin
        self.fuel = fuel

    def get_relation_price_efficiency(self):
        if self.efficiency == 0:
            return float('inf')
        return self.fuel.price / self.efficiency
