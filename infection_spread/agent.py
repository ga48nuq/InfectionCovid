import time, enum
import numpy as np
import pandas as pd
import pylab as plt
import networkx as nx
import sys
import random
from enum import Enum

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


class State(enum.IntEnum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    REMOVED = 2
    NA = 3


class Human(Agent):
    """ An agent in an epidemic model."""

    class State(enum.IntEnum):
        SUSCEPTIBLE = 0
        INFECTED = 1
        REMOVED = 2
        NA = 3
        

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.traversable = False
        self.age = self.random.normalvariate(20,40)
        self.state = State.SUSCEPTIBLE  
        self.infection_time = 0
        self.model = model

    # @property
    # def state(self):
    #     return self._state

    # @state.setter    
    # def state(self, x):
    #     self._state = x

    # @property
    # def infection_time(self):
    #     return self._infection_time

    # @infection_time.setter    
    # def infection_time(self, x):
    #     self._infection_time = x

    def get_position(self):
        return self.pos


    def move(self):
        """Move the agent"""

        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        if self.location_is_traversable(new_position):
            self.model.grid.move_agent(self, new_position)

    def status(self):
        """Check infection status"""
        
        if self.state == State.INFECTED:

            drate = self.model.death_rate
            alive = np.random.choice([0,1], p=[drate,1-drate])
            if alive == 0:
                self.model.schedule.remove(self)            
            t = self.model.schedule.time-self.infection_time
            if t >= self.recovery_time:          
                self.state = State.REMOVED
            #print (self.model.schedule.time,self.recovery_time,t)

    def contact(self):
        """Find close contacts and infect"""
        
        cellmates = self.model.grid.get_cell_list_contents([self.pos])       
        if len(cellmates) > 1:
            #other = self.random.choice(cellmates)
            for other in cellmates:
                #print (self.model.schedule.time,self.state,other.state)                
                if self.random.random() > self.model.ptrans:
                    continue
                if self.state is State.INFECTED and other.state is State.SUSCEPTIBLE:                    
                    other.state = State.INFECTED
                    other.infection_time = self.model.schedule.time
                    other.recovery_time = model.get_recovery_time()

    def location_is_traversable(self, pos):
        if not self.model.grid.is_cell_empty(pos):
            contents = self.model.grid.get_cell_list_contents(pos)
            for agent in contents:
                if not agent.traversable:
                    return False

        return True                

    def step(self):
        self.status()
        self.move()
        self.contact()

"""
ROOM SET UP
"""

class FloorObject(Agent):
    def __init__(self, pos, traversable, model=None):
        super().__init__(pos, model)
        self.pos = pos
        self.traversable = traversable
        self.state = State.NA

    def get_position(self):
        return self.pos

class Door(FloorObject):
    def __init__(self, pos, model):
        super().__init__(pos, traversable=True, model=model)
        self.state = State.NA

class Exit(FloorObject):
    def __init__(self, pos, model):
        super().__init__(pos, traversable=True, model=model)
        self.state = State.NA

class Wall(FloorObject):
    def __init__(self, pos, model):
        super().__init__(pos, traversable=False, model=model)
        self.state = State.NA