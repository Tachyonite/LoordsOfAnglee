import pickle

def saveAllInformation(name,player,game):
    with open('saves/{}.dat'.format(name), 'wb') as f:
        pickle.dump([player,game], f, protocol=2)

def loadAllInformation(name):
    global player
    global game
    with open('{}'.format(name), 'rb') as f:
        p, g = pickle.load(f)
        return p, g