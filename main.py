# Import the Resource class and other necessary components
import sys
from parser import parser
from parser import Resource
from turn import TurnSimulator

# If the script is run directly, perform a simple test
if __name__ == "__main__":
    file = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    initial_budget, resources, turns = parser(file)
    
    # Example purchases format: [(turn_index, resource_id1, resource_id2, ...), ...]
    # This mirrors the output format from the problem statement
    example_purchases = []
    
    # For the example in the problem statement:
    if file == 0:  # If using the demo file
        example_purchases = [
            (0, 5),       # Turn 0: Buy resource 5
            (1, 2),       # Turn 1: Buy resource 2
            (2, 2),       # Turn 2: Buy resource 2
            (4, 2, 2),    # Turn 4: Buy resource 2 twice
            (5, 2)        # Turn 5: Buy resource 2
        ]
    
    # Create simulator and run simulation
    simulator = TurnSimulator(initial_budget, resources, turns)
    
    # Simulate each turn individually
    print("=== Starting Simulation ===")
    for turn_idx in range(len(turns)):
        # Find purchases for this turn
        resources_to_buy = None
        for purchase in example_purchases:
            if purchase[0] == turn_idx:
                resources_to_buy = purchase[1:]
                break
        
        # Simulate turn
        simulator.simulate_turn(turn_idx, resources_to_buy)
    
    print(f"\n=== Final Total Profit: {simulator.total_profit} ===")
