from parser import parser
import sys



file =  int(sys.argv[1]) if len(sys.argv) > 1 else 0
budget, resources, turn = parser(file)


def possibilities(budget: int):
    yield []

def maintenance_cost(active_resources):
    return 0

def buy(resources):
    return 0

def compute_profit(active_resources, turn):
    return 0

def correct(resources):
    return 1.0, 1.0, 1.0, 1.0, 0

def bruteforce(budget: int, turn: int, active_resources) -> int:
    if turn == 0:
        return 0

    for possibility in possibilities(budget):
        maintenance = maintenance_cost(active_resources)
        cost = buy(active_resources, possibility) + maintenance
        active_resources_ = active_resources + possibility
        profit = compute_profit(active_resources_, turn)

        bruteforce(budget - cost + profit, turn - 1, active_resources_)
    
