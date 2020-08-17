import os
import random
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from .agent import Human, State, Wall, Exit, Door
 
class InfectionModel(Model):
    """A model for infection spread."""

    def __init__(self, human_count, random_spawn, save_plots, 
            floor_plan_file="floorplan_1.txt", N=30, width=10, height=10, ptrans=0.5, 
            progression_period=3, progression_sd=2, death_rate=0.0193, recovery_days=21, 
            recovery_sd=7):
        # Load floorplan
        # floorplan = np.genfromtxt(path.join("infection_spread/floorplans/", floor_plan_file))
        with open(os.path.join("infection_spread/floorplans/", floor_plan_file), "rt") as f:
            floorplan = np.matrix([line.strip().split() for line in f.readlines()])

        # Rotate the floorplan so it's interpreted as seen in the text file
        floorplan = np.rot90(floorplan, 3)

        # Check what dimension our floorplan is
        width, height = np.shape(floorplan)

        # Init params
        self.num_agents = N
        self.initial_outbreak_size = 1
        self.recovery_days = recovery_days
        self.recovery_sd = recovery_sd
        self.ptrans = ptrans
        self.death_rate = death_rate
        self.running = True
        self.dead_agents = []
        self.width = width
        self.height = height
        self.human_count = human_count

 # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(height, width, torus=False)

 # Used to easily see if a location is an Exit or Door, since this needs to be done a lot
        self.exit_list = []
        self.door_list = []
        # If random spawn is false, spawn_list will contain the list of possible spawn points according to the floorplan
        self.random_spawn = random_spawn
        self.spawn_list = []

        # Load floorplan objects
        for (x, y), value in np.ndenumerate(floorplan):
            value = str(value)
            floor_object = None

            if value == "W":
                floor_object = Wall((x, y), self)

            elif value == "E":
                floor_object = Exit((x, y), self)
                self.exit_list.append((x, y))
                self.door_list.append((x, y))  # Add exits to doors as well

            elif value == "D":
                floor_object = Door((x, y), self)
                self.door_list.append((x, y))

            elif value == "S":
                self.spawn_list.append((x, y))

            if floor_object:
                self.grid.place_agent(floor_object, (x, y))
                self.schedule.add(floor_object)

        # Create a graph of traversable routes, used by agents for pathing
        self.graph = nx.Graph()
        for agents, x, y in self.grid.coord_iter():
            pos = (x, y)

            # If the location is empty, or a door
            if not agents or any(isinstance(agent, Door) for agent in agents):
                neighbors = self.grid.get_neighborhood(pos, moore=True, include_center=True, radius=1)

                for neighbor in neighbors:
                    # If there is contents at this location and they are not Doors or Exits, skip them
                    if not self.grid.is_cell_empty(neighbor) and neighbor not in self.door_list:
                        continue

                    self.graph.add_edge(pos, neighbor)

 # Start placing human agents
       # for i in range(0, self.human_count):
        #    if self.random_spawn:  # Place human agents randomly
         #       pos = self.grid.find_empty()
          #  else:  # Place human agents at specified spawn locations
           #     pos = random.choice(self.spawn_list)

            #if pos:
                # Create a random human
             #   health = random.randint(self.MIN_HEALTH * 100, self.MAX_HEALTH * 100) / 100
              #  speed = random.randint(self.MIN_SPEED, self.MAX_SPEED)

        for i in range(0, self.num_agents):
            a = Human(unique_id=i, model=self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            # x = self.random.randrange(self.grid.width)
            # y = self.random.randrange(self.grid.height)
            # self.grid.place_agent(a, (x, y))

            if self.random_spawn:  # Place human agents randomly
                pos = self.grid.find_empty()
            else:  # Place human agents at specified spawn locations
                pos = random.choice(self.spawn_list)

            self.grid.place_agent(a, pos)


            #make some agents infected at start
            infected = np.random.choice([0,1], 1, p=[0.98,0.02])
            if infected == 1:
                a.state = State.INFECTED
                a.recovery_time = self.get_recovery_time()
                    
        self.datacollector = DataCollector(
        	#model_reporters={"Gini": compute_gini}, 
			agent_reporters={"State": "state"})

    def get_recovery_time(self):
        return int(self.random.normalvariate(self.recovery_days,self.recovery_sd))

    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()
        self.datacollector.collect(self)


def get_column_data(model):
        #pivot the model dataframe to get states count at each step
    agent_state = model.datacollector.get_agent_vars_dataframe()
    X = pd.pivot_table(agent_state.reset_index(),index='Step',columns='State',aggfunc=np.size,fill_value=0)    
    labels = ['Susceptible','Infected','Removed', 'NA']
    X.columns = labels[:len(X.columns)]
    return X
    
def plot_states(model,ax):    
    steps = model.schedule.steps
    X = get_column_data(model)
    X.plot(ax=ax,lw=3,alpha=0.8)


pop=300
steps=100
st=time.time()
model = InfectionModel(human_count=pop, random_spawn=True, save_plots=False, ptrans=0.5)
for i in range(steps):
    model.step()
print(time.time()-st)
agent_state = model.datacollector.get_agent_vars_dataframe()
print(get_column_data(model))

f,ax=plt.subplots(1,1,figsize=(8,4))
plot_states(model,ax)
plt.savefig('SIR.png',dpi=150)