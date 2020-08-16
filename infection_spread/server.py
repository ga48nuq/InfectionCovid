from os import listdir, path
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from .model import InfectionModel
from .agent import Exit, State, Wall, Human, Door

# Creates a visual portrayal of the model in the browser interface
def infection_spread_portrayal(agent):
    if agent is None:
        return

    portrayal = {}
    (x, y) = agent.get_position()
    portrayal["x"] = x
    portrayal["y"] = y

    if type(agent) is Human:
        portrayal["Shape"] = "infection_spread/resources/human.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 5

    # elif type(agent) is Human.Infected:
    #     portrayal["Shape"] = "infection_spread/resources/human_infect.png"
    #     portrayal["scale"] = 1
    #     portrayal["Layer"] = 5    

    elif type(agent) is Exit:
        portrayal["Shape"] = "infection_spread/resources/exit.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1

    elif type(agent) is Door:
        portrayal["Shape"] = "infection_spread/resources/door.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1

    elif type(agent) is Wall:
        portrayal["Shape"] = "infection_spread/resources/wall.png"
        portrayal["scale"] = 1
        portrayal["Layer"] = 1

    return portrayal

# the grid size is fixed to 50x50
canvas_element = CanvasGrid(infection_spread_portrayal, 50, 50, 800, 800)

# Define the charts on our web interface visualisation
status_chart = ChartModule([{"Label": "Susceptible", "Color": "blue"},
                            {"Label": "Infected", "Color": "red"},
                            {"Label": "Removed", "Color": "green"}])

# Get list of available floorplans
floor_plans = [f for f in listdir("infection_spread/floorplans") if path.isfile(path.join("infection_spread/floorplans", f))]

# Specify the parameters changeable by the user, in the web interface
model_params = {
    "floor_plan_file": UserSettableParameter("choice", "Floorplan", value=floor_plans[0], choices=floor_plans),
    "human_count": UserSettableParameter("number", "Number Of Human Agents", value=10),
    "random_spawn": UserSettableParameter('checkbox', 'Spawn Agents at Random Locations', value=True),
    "save_plots": UserSettableParameter('checkbox', 'Save plots to file', value=True)
}

# Start the visual server with the model
server = ModularServer(InfectionModel, [canvas_element, status_chart], "Infection Model",
                       model_params)