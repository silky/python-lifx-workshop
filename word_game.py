#!/usr/bin/env python

from lifxlan import LifxLAN
from lifxlan.errors import WorkflowException
from time import sleep
import numpy as np
import spacy
import tqdm


our_lights = [ "A1", "A2", "A3", "A4", "A5"
             , "A6", "A7", "A8", "A9", "A10"
             ]


def setup ():
    def attempt_setup ():
        lan    = LifxLAN()
        # lights = lan.get_devices_by_name(our_lights).get_device_list()
        lights = lan.get_lights()
        lights = sorted(lights, key=lambda x: int(x.get_label().replace("A", "")))
        names  = [ l.get_label() for l in lights ]

        print("Found the following lights:")
        for name in names:
            print(f"  - {name}")

        # assert len(lights) == 10, "We need 10 lights"

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
        print("What would you like to say? I like long complex sentences!")
        x = input("> ")

        if x == "" or x is None:
            continue

        # scaled = compute_vector_spacy(x)
        scaled = compute_vector_alphabet(x)

        print("")
        print(f"Displaying ... (please wait until I'm finished!) : {x}")
        
        # play_on_lights_in_chunks(scaled, lights)
        play_on_lights_following(scaled, lights)

        print("")


letters = [ chr(x) for x in range( ord("a"), ord("z") + 1 ) ]


def compute_vector_alphabet (sentence):
    """
    """
    lower = sentence.lower()
    keep  = [ x for x in lower if x in letters ]

    def get_numbers (msg):
        max_    = 65535
        step    = max_ / 26
        colours = [ int((ord(x) - ord('a'))*step) for x in msg ]
        return colours

    return get_numbers(keep)



def compute_vector_spacy (sentence):
    encoded = nlp(sentence)
    vector  = encoded.vector

    # Filter:
    # vector = [ v for v in vector if abs(v) > 2]
    vector = [ v for k,v in enumerate(vector) if k % 20 == 0]

    delta   = 65535 / (max(vector) - min(vector))
    scaled  = delta * (vector - min(vector))
    scaled  = scaled.astype(np.int64)
    
    return scaled


def play_on_lights_following (vector, lights):
    # v = np.array([ 500, 15000, 35000, 55000 ])
    # vector = np.hstack( [v for k in range(0, len(vector) // 4)] )

    n = len(vector)

    temps = np.array([ 1000*(k+1) for k in range(9) ])
    temps = np.hstack( [temps, temps[::1][1:] ] )
    temps = np.hstack( [ temps for k in range(int(np.ceil(n/len(temps)))) ] )


    m = len(lights)
    r = int(np.ceil(n / m))

    wait = 1 / m

    zeros = [ 0 for k in range(m-1) ]

    new_vector = np.hstack( [zeros, vector, zeros] )

    # names = [ l.get_label() for l in lights ]

    # Reset them
    def reset ():
        sleep(0.5)
        for light in lights:
            try_colour(light, 30000)

    reset()

    for k in tqdm.tqdm(range(len(new_vector))):
        nums = new_vector[k:(k+m)]
        our_temps = temps[k:(k+m)]
        nums = nums[::-1]

        for i, ((hue, new_temp), light) in enumerate(zip(zip(nums, our_temps), lights)):
            # name = names[i]
            # print(f" - setting {hue} on light {name}")
            try_colour(light, hue, new_temp)
            sleep(wait)
    # reset()


def try_colour (light, hue, temp=10000):
    #
    # Over-ride the temperature
    #
    # temp = 3000
    new_colour = [ hue, 60000, 20000, temp ]
    try:
        light.set_color(new_colour, 500, True)
    except:
        # Don't do anything
        return


def play_on_lights_in_chunks (vector, lights):
    n = len(vector)
    m = len(lights)
    r = int(np.ceil(n / m))

    wait = 1 / m

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
