import os
import textwrap as tw
import msvcrt

################# HELPERS #####################

def getch(bytes=False):
    act = False
    while not act:
        try:
            if bytes:
                act = msvcrt.getch()
            else:
                act = msvcrt.getch()
                act = act.decode("ASCII")
        except:
            if act == b'\xe0':
                act = getch()
            return act
    return act

def u():  # short for update, clears screen and resets text colour
    print(tc.w)
    os.system('cls' if os.name == 'nt' else 'clear')
    print()


d = 0


def p(text,wrap=True,gap=False):  # short for print, with optional delay

    print("  "+"\n  ".join(tw.wrap(text,80))) if wrap else print("\n  "+text) if gap else print("  "+text)

    #t.sleep((len(text) / 20))  # adds length=based delay

def s(spk, text):  # short for speaker, so you can define someone as saying something
    p("".join(spk + ": " + text))

def getAlphas(table):
    stringy = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return stringy[0:len(table)]

def a(prompt, table):
    '''Get a range checked integer from the player.'''
    vmax = len(table)-1
    vmin = 0
    if prompt[-1] != ' ':
        prompt += ' '
    quit = False
    alphas = getAlphas(table)
    while True or not quit:
        instr = getch()
        if instr == '\x03':
            break
        if instr == "" or instr == '\r':
            return vmax
        elif instr in alphas:
            return alphas.index(instr)
        else:
            pass
    inp = input("Press Ctrl+C again to quit.")
    if inp != '\x03':
        a(prompt,table)


def astr(prompt, valid_list):
    print(valid_list)
    while True:
        instr = input(prompt)
        if instr in valid_list:
            return instr
        elif instr == "x":
            return False
        else:
            print("No such thing.")



##########################################################

class tc:  # text colours
    h = '\033[35m'  # purple
    p = '\033[1;35m'  # pink
    b = '\033[0;34m'  # blue
    lb = '\033[1;34m'  # light blue
    g = '\033[32m'  # green
    y = '\033[33m'  # yellow
    f = '\033[31m'  # red
    e = '\033[0m'   # default white
    w = '\033[1;37m'  # white
    lg = '\033[1;30m'  # light grey
    c = '\033[1;36m'  # cyan


    bg_w = '\033[47m'  # white background
    bg_b = '\033[40m'  # black background
    bg_rs = '\033[49m'  # reset background
    bg_r = '\033[41m'  # red background

    '''
        These colours can be called before strings, and with the colourama (cr)
        import, it should work on all platforms.
    '''

    lookup = {
        "light grey" : lg,
        "white" : w,
        "cyan" : c,
        "red" : f,
        "purple" : h
    }
    rarity = {
        "junk" : lg,
        "common" : w,
        "uncommon" : c,
        "rare" : f,
        "epic" : h
    }

class dv:
    ds = "".join(["-" * 25])  # dash
    eq = "".join(["=" * 25])  # equals
    td = "".join(["~" * 25])  # tilde

    def header(text):
        return dv.eq + "\n\n" + str(text) + "\n\n" + dv.eq + "\n"
