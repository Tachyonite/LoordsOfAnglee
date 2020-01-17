#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Micah
#
# Created:     27/11/2016
# Copyright:   (c) Micah 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import dictimporter as di
import random
from markov import getchar
from markov import getplace
import core

kingdomRoles = ["Loord","Caftij oder Garrd","Reputii","Forjmaesterr","Arkhaevist","Frer"]

def genfex(*args):
    name = getchar(args)
    ears = choose(di.dicts[1].contents,"ears")
    forehead = choose(di.dicts[1].contents,"forehead")
    eyes = choose(di.dicts[1].contents,"eyes")
    cheeks = choose(di.dicts[1].contents,"cheeks")
    nose = choose(di.dicts[1].contents,"nose")
    expressions = choose(di.dicts[1].contents,"expressions")
    face = [ears,"\n",forehead,"\n",eyes,"\n",cheeks,"\n",nose,"\n",expressions]
    face = "".join(face)
    return face,name

def genkingdom():
    sizes = (("capital",1500),("city",500),("town",200))
    name = getplace()
    descriptor = choose(di.dicts[2].contents,"descriptors")
    classes = choose(di.dicts[2].contents,"classes")
    mysize = random.choice(sizes)
    population = mysize[1]+random.randint(-50,300)
    nobles = []
    common = []
    for i in range(len(kingdomRoles)):
        nobles.append(core.Char(name, True))
    for i in range(10):
        common.append(genfex())
    if descriptor == "":
        place = [classes," of ",name]
    else:
        place = [descriptor," ",classes," of ",name]
    place = "".join(place)
    return place,mysize,population,nobles,common

def choose(choices,*cat):
    if cat:
        ''' If at least one argument has been passed in addition to the
            dictionary, we know that this isn't being called recursively.
            So we can pull out the parts of the dictionary that we care
            about and then grab a random choice from them. '''
        processed = []
        for s in cat:
            processed += choices.get(s)
        choice = random.choice(processed)
    else:
        ''' If no category arguments have been passed, we assume that
            the dict is already in a processed form. So it's safe to just
            randomly choose an item from it. '''
        processed = list(choices.values())
        if len(processed) is not 1:
            raise Exception("Poorly formatted YAML, some results are impossible.")
        choice = random.choice(processed[0])

    ''' If the choice we've found is a dictionary or list, start
        recursion to find a final value. If it's just a string we
        assume that everything is fine and pass it back out. '''
    if isinstance(choice, (dict, list)):
        return choose(choice)
    elif isinstance(choice, (str)):
        return choice
    else:
        raise Exception("Found an invalid object in dictionary structure!")



