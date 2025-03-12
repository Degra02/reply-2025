import os
import sys

class Resource:
    def __init__(self, RI, RA, RP, RW, RM, RL, RU, RT, RE=None):
        self.RI = RI  # Resource identifier
        self.RA = RA  # Activation cost
        self.RP = RP  # Periodic cost
        self.RW = RW  # Active turns
        self.RM = RM  # Maintenance turns
        self.RL = RL  # Life cycle
        self.RU = RU  # Buildings powered
        self.RT = RT  # Special effect type
        self.RE = RE  # Special effect parameter

class Turn:
    def __init__(self, TM, TX, TR):
        self.TM = TM  # Minimum buildings to power
        self.TX = TX  # Maximum buildings to power
        self.TR = TR  # Profit per building

def parse_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # firts line
    D, R, T = map(int, lines[0].strip().split())

    resources = []
    turns = []

    # RESOURCES
    for i in range(1, R + 1):
        parts = lines[i].strip().split()
        RI = int(parts[0])
        RA = int(parts[1])
        RP = int(parts[2])
        RW = int(parts[3])
        RM = int(parts[4])
        RL = int(parts[5])
        RU = int(parts[6])
        RT = parts[7]
        RE = int(parts[8]) if len(parts) > 8 else None
        resource = Resource(RI, RA, RP, RW, RM, RL, RU, RT, RE)
        resources.append(resource)

    # TURNS
    for i in range(R + 1, R + 1 + T):
        TM, TX, TR = map(int, lines[i].strip().split())
        turn = Turn(TM, TX, TR)
        turns.append(turn)

    return D, resources, turns


        
files = ['0-demo.txt', '1-thunberg.txt', '2-attenborough.txt', '3-goodall.txt', '4-maathai.txt', '5-carson.txt', '6-earle.txt', '7-mckibben.txt', '8-shiva.txt']


file =  int(sys.argv[1]) if len(sys.argv) > 1 else 0
D, resources, turns = parse_input("./inputs/"+files[file])

print(f"Initial Budget: {D}")
print("\nResources:")
for resource in resources:
    print(f"ID: {resource.RI}, Type: {resource.RT}, Activation Cost: {resource.RA}, Buildings Powered: {resource.RU} ")
print("\nTurns:")
for turn in turns:
    print(f"Min Buildings: {turn.TM}, Max Buildings: {turn.TX}, Profit per Building: {turn.TR}")
    
print(f"File: {files[file]}")