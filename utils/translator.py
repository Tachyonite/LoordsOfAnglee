import random

class Translator():
    def __init__(self,file):
        for k, v in file.items():
            setattr(self,k,v)
    def Translate(self,key):
        try:
            return str(eval('self.'+key))
        except AttributeError:
            return "!" + key +"!"
    def TranslateRandom(self,key):
        try:
            return str(random.choice(eval('self.'+key)))
        except NameError:
            return "!" + key +"!"


def loadStrings(file):
    global translator
    translator = Translator(file)

def Translate(key,random=False):
    if random:
        return translator.TranslateRandom(key)
    return translator.Translate(key)