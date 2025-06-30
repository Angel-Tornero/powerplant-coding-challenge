import logging

from app.services.fuel_service import Fuel
from app.services.powerplant_service import Powerplant

logger = logging.getLogger(__name__)

PLANT_TYPE_PER_FUEL_KEY = {
    "gas(euro/MWh)": "gasfired",
    "kerosine(euro/MWh)": "turbojet",
    "wind(%)": "windturbine",

}

CO2_TONS_PER_GAS_MWH = 0.3


class ProductionPlanService:
    def __init__(self, payload):
        self.load = payload.load
        wind_efficiency = payload.fuels["wind(%)"] / 100
        co2_emission_price = payload.fuels.pop("co2(euro/ton)")
        self.fuels = []
        for key, value in payload.fuels.items():
            if key == "wind(%)":
                self.fuels.append(Fuel(key, 0, value))
            elif key=="gas(euro/MWh)":
                self.fuels.append(Fuel(key, value + co2_emission_price * CO2_TONS_PER_GAS_MWH, 1))
            else:
                self.fuels.append(Fuel(key, value, 1))
        self.fuel_by_plant_type = {PLANT_TYPE_PER_FUEL_KEY[fuel.name]: fuel for fuel in self.fuels}
        
        self.powerplants = []
        for vals in payload.powerplants:
            vals.update(
                {
                    "fuel": self.fuel_by_plant_type[vals["type"]],
                }
            )
            if vals["type"] == "windturbine":
                vals.update(
                    {
                        "efficiency": wind_efficiency,
                        "pmax": vals["pmax"] * wind_efficiency,
                    }
                )
            new_plant = Powerplant(**vals)
            self.powerplants.append(new_plant)

    def calculate_production_plan(self):
        """Algorithm to calculate the best production plan for the given payload.
        
        Steps:
        - Get required plans.
        - Initialize the solution by adding the pmin of all required plants.
        - While the achieved power is lower than desired power:
            - Calculates the best addition within the required plants (the one with lower relation price/efficiency)
        """
        required_plants = self._get_required_plants_for_solution()
        solution = []
        solution_power_per_plant = {}
        for plant in required_plants:
            solution.append(
                {
                    "name": plant.name,
                    "p": plant.pmin,
                }
            )
        solution_power_per_plant = {plant.name: plant.pmin for plant in required_plants}
        current_power = self._get_solution_power(solution_power_per_plant)
        i = 0
        while current_power < self.load and i < len(required_plants):
            best_addition = self._get_best_addition(solution_power_per_plant, current_power, required_plants)
            solution_power_per_plant[best_addition["name"]] = best_addition["p"]
            current_power = self._get_solution_power(solution_power_per_plant)
            i += 1
        return self._generate_response(solution_power_per_plant)

    def _get_required_plants_for_solution(self):
        """Return the minimum required plants to create a solution having into account its price/efficiency relation and pmin.
        
        Prioritise plants with the lowest price/efficiency ratio and those with a pmin that fits the desired load.
        """
        ordered_powerplants = self._order_by_relation_price_efficiency()
        required_plants = []
        power_sum = 0
        pmin_sum = 0
        i = 0
        while power_sum < self.load:
            if (self.load - ordered_powerplants[i].pmin) >=0:
                required_plants.append(ordered_powerplants[i])
                power_sum += ordered_powerplants[i].pmax
                pmin_sum += ordered_powerplants[i].pmin
            i += 1
            if i == len(ordered_powerplants):
                raise Exception("The service was called correctly, but no solution was found.")
        return required_plants

    def _order_by_relation_price_efficiency(self):
        """Order the powerplants by their relation price/efficiency."""
        def get_relation_price_efficiency(plant):
            return plant.get_relation_price_efficiency()
        return sorted(self.powerplants, key=get_relation_price_efficiency)

    def _get_solution_power(self, solution_power_per_plant):
        """Calculate the current achieved load."""
        return sum(solution_power_per_plant.values())

    def _get_best_addition(self, solution_power_per_plant, current_power, available_plants):
        """Calculate the best addition to the current production plan. It ignores the plants that are
        already giving its pmax to the production plan and takes the best of the rest (relation price/efficiency).
        
        Returns a dict with the name of the plant and the power it supplies to the production plan.
        """
        best_addition = None
        best_addition_value = float('inf')
        for plant in available_plants:
            if solution_power_per_plant[plant.name] < plant.pmax:
                plant_value = plant.get_relation_price_efficiency()
                if (
                    plant_value < best_addition_value
                ):
                    best_addition = plant
                    best_addition_value = plant_value
        power_to_be_supplied = self.load - current_power + solution_power_per_plant[best_addition.name]
        power_to_set = power_to_be_supplied if power_to_be_supplied <= best_addition.pmax else best_addition.pmax
        return {
            "name": best_addition.name,
            "p": power_to_set,
        }

    def _generate_response(self, solution_power_per_plant):
        """Generate the response object consisting on a list of dicts, each dict containing the plant name and
        the power it supplies.
        """
        return [
            {
                "name": plant.name,
                "p": round(solution_power_per_plant.get(plant.name, 0.), 1)
            }
            for plant in self.powerplants
        ]
