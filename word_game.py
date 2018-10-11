#!/usr/bin/env python

from lifxlan import LifxLAN
from lifxlan.errors import WorkflowException
from time import sleep
import numpy as np
import spacy
import tqdm


our_lights = [ "GraceHopper"
             , "SophieWilson"
             , "MargaretHamilton"
             , "AdeleGoldberg"
             ]


def setup ():
    def attempt_setup (): 
        lan    = LifxLAN()
        lights = lan.get_devices_by_name(our_lights).get_device_list()
        lights = sorted(lights, key=lambda x: x.get_label())
        names  = [ l.get_label() for l in lights ]
        return lights

    k = 0
    while k < 10:
        try:
            return attempt_setup()
        except WorkflowException as e:
            print(".")
            k = k + 1
            continue


def play ():
    print("Setting up ... (CTRL-D to quit)")
    lights = setup()
    nlp    = spacy.load("en")

    print("")
    print("We're ready to play the LifX Light Speaking Game!")

    while True:
        print("What would you like to say?")
        x = input("> ")

        if x == "" or x is None:
            continue

        encoded = nlp(x)
        vector  = encoded.vector
        delta   = 65535 / (max(vector) - min(vector))
        scaled  = delta * (vector - min(vector))
        scaled  = scaled.astype(np.int64)

        print("")
        print(f"Saying ... : {x}")
        play_on_lights(scaled, lights)
        print("")


def play_on_lights (vector, lights):
    n = len(vector)
    m = len(lights)
    r = int(np.ceil(n / m))
    
    wait = 1 / m

    def try_colour (light, colour):
        new_colour = [ colour, 20000, 20000, 10000 ]
        try:
            light.set_color(new_colour, 500, True)
        except:
            # Don't do anything
            return
    
    for light in lights:
        try_colour(light, 30000)

    for k in tqdm.tqdm(range(0, r)):
        nums = vector[k*m:(k+1)*m]

        for i, (colour, light) in enumerate(zip(nums, lights)):
            try_colour(light, colour)
            sleep(wait)


if __name__ == "__main__":
    try:
        play()  
    except EOFError as e:
        print("")
        print("Thanks for playing!")

