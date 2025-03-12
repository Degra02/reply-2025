from parser import Resource

class ResourceInstance:
    def __init__(self, resource, purchase_turn):
        self.resource = resource
        self.purchase_turn = purchase_turn
        self.current_life = 0
        self.is_active = True
        self.remaining_active_turns = resource.RW
        self.accumulated_buildings = 0  # For type E resources
        
    def update(self, current_turn):
        """Update resource state for a new turn"""
        self.current_life += 1
        
        # Check if resource has reached end of life
        if self.current_life >= self.resource.RL:
            return False  # Resource is obsolete
            
        # Update active/inactive state
        if self.is_active:
            self.remaining_active_turns -= 1
            if self.remaining_active_turns <= 0:
                self.is_active = False
                self.remaining_active_turns = self.resource.RM  # Start maintenance period
        else:
            self.remaining_active_turns -= 1
            if self.remaining_active_turns <= 0:
                self.is_active = True
                self.remaining_active_turns = self.resource.RW  # Start active period again
                
        return True  # Resource is still alive

class TurnSimulator:
    def __init__(self, initial_budget, resources, turns):
        self.budget = initial_budget
        self.resources = resources  # List of Resource objects
        self.turns = turns  # List of Turn objects
        self.active_resources = []  # List of ResourceInstance objects
        self.total_profit = 0
        
    def get_resource_by_id(self, resource_id):
        """Get resource by its ID"""
        for resource in self.resources:
            if resource.RI == resource_id:
                return resource
        return None
        
    def buy_resources(self, turn_idx, resource_ids):
        """Buy resources for a specific turn"""
        turn_activation_cost = 0
        
        # Calculate total activation cost for this turn
        for resource_id in resource_ids:
            resource = self.get_resource_by_id(resource_id)
            if resource:
                turn_activation_cost += resource.RA
                
        # Check if we have enough budget
        if turn_activation_cost > self.budget:
            print(f"Turn {turn_idx}: Not enough budget ({self.budget}) to buy resources (cost: {turn_activation_cost})")
            return False
            
        # If we have enough budget, add resources to active_resources
        for resource_id in resource_ids:
            resource = self.get_resource_by_id(resource_id)
            if resource:
                # Apply C-type effects (Maintenance Plan) from existing resources to new resource
                modified_resource = self.apply_c_type_effects(resource)
                
                # Add resource to active resources
                resource_instance = ResourceInstance(modified_resource, turn_idx)
                self.active_resources.append(resource_instance)
                
        # Deduct activation cost from budget
        self.budget -= turn_activation_cost
        return True
        
    def apply_c_type_effects(self, resource):
        """Apply C-type effects from active resources to a new resource"""
        modified_resource = Resource(
            resource.RI, resource.RA, resource.RP, resource.RW, 
            resource.RM, resource.RL, resource.RU, resource.RT, resource.RE
        )
        
        # Look for active C-type resources
        for active_resource in self.active_resources:
            if active_resource.is_active and active_resource.resource.RT == "C":
                if active_resource.resource.RE > 0:  # Green resource
                    # Extends life of resource
                    modified_resource.RL = int(modified_resource.RL * (1 + active_resource.resource.RE / 100))
                else:  # Non-green resource
                    # Reduces life of resource (minimum 1)
                    modified_resource.RL = max(1, int(modified_resource.RL * (1 + active_resource.resource.RE / 100)))
                    
        return modified_resource
    
    def calculate_special_effects(self, turn_idx):
        """Calculate all special effects for current turn"""
        turn = self.turns[turn_idx]
        effect_values = {
            # Default values
            "A": 0,      # Smart Meter effect (building power adjustment)
            "B_min": 0,  # Distribution Facility effect on min threshold
            "B_max": 0,  # Distribution Facility effect on max threshold
            "D": 0,      # Renewable Plant effect on profit
            "E": []      # Accumulator resources
        }
        
        # Collect all active special effects
        for resource in self.active_resources:
            if resource.is_active and resource.resource.RT in ['A', 'B', 'D', 'E']:
                effect_percentage = resource.resource.RE if resource.resource.RE is not None else 0
                
                if resource.resource.RT == 'A':  # Smart Meter
                    effect_values['A'] += effect_percentage
                elif resource.resource.RT == 'B':  # Distribution Facility
                    effect_values['B_min'] += effect_percentage
                    effect_values['B_max'] += effect_percentage
                elif resource.resource.RT == 'D':  # Renewable Plant
                    effect_values['D'] += effect_percentage
                elif resource.resource.RT == 'E':  # Accumulator
                    effect_values['E'].append(resource)
                    
        # Apply effects to current turn values
        adjusted_tm = max(0, int(turn.TM * (1 + effect_values['B_min'] / 100)))
        adjusted_tx = max(0, int(turn.TX * (1 + effect_values['B_max'] / 100)))
        adjusted_tr = max(0, int(turn.TR * (1 + effect_values['D'] / 100)))
        
        return adjusted_tm, adjusted_tx, adjusted_tr, effect_values
    
    def calculate_buildings_powered(self, effect_values):
        """Calculate total buildings powered with special effects"""
        total_buildings = 0
        
        for resource in self.active_resources:
            if resource.is_active and resource.resource.RT != 'E':  # Exclude accumulators from power calculation
                # Apply A-type effects (Smart Meter)
                adjusted_power = resource.resource.RU
                if effect_values['A'] != 0:  # Apply Smart Meter effect
                    adjusted_power = max(0, int(adjusted_power * (1 + effect_values['A'] / 100)))
                    
                total_buildings += adjusted_power
                
        return total_buildings
    
    def handle_accumulators(self, buildings_powered, adjusted_tm, adjusted_tx, effect_values):
        """Handle E-type resources (Accumulators)"""
        # Get all active accumulators
        accumulators = effect_values['E']
        
        # If we have a surplus, store it in accumulators
        if buildings_powered > adjusted_tx:
            surplus = buildings_powered - adjusted_tx
            for acc in accumulators:
                acc.accumulated_buildings += surplus
                surplus = 0  # All surplus has been stored
                break
            
            # Cap buildings powered to maximum
            buildings_powered = adjusted_tx
            
        # If we're below minimum, try to use stored power from accumulators
        elif buildings_powered < adjusted_tm and accumulators:
            deficit = adjusted_tm - buildings_powered
            for acc in accumulators:
                if acc.accumulated_buildings >= deficit:
                    acc.accumulated_buildings -= deficit
                    buildings_powered += deficit
                    deficit = 0
                    break
                else:
                    buildings_powered += acc.accumulated_buildings
                    deficit -= acc.accumulated_buildings
                    acc.accumulated_buildings = 0
                    
        return buildings_powered
    
    def transfer_accumulated_energy(self, obsolete_resource):
        """Transfer accumulated energy from obsolete accumulators to active ones"""
        if obsolete_resource.resource.RT == 'E' and obsolete_resource.accumulated_buildings > 0:
            # Find active accumulators
            active_accumulators = [r for r in self.active_resources 
                                if r.resource.RT == 'E' and r.is_active and r != obsolete_resource]
            
            if active_accumulators:
                # Transfer energy to first active accumulator
                active_accumulators[0].accumulated_buildings += obsolete_resource.accumulated_buildings
                obsolete_resource.accumulated_buildings = 0
    
    def simulate_turn(self, turn_idx, resource_ids_to_buy=None):
        """Simulate a single turn"""
        if turn_idx >= len(self.turns):
            print(f"Error: Turn index {turn_idx} is out of range")
            return False
            
        # Buy new resources if specified
        if resource_ids_to_buy:
            if not self.buy_resources(turn_idx, resource_ids_to_buy):
                return False
                
        # Update resource states
        to_remove = []
        for resource in self.active_resources:
            if not resource.update(turn_idx):
                # Resource has reached end of life
                self.transfer_accumulated_energy(resource)
                to_remove.append(resource)
                
        # Remove obsolete resources
        for resource in to_remove:
            self.active_resources.remove(resource)
            
        # Calculate special effects for this turn
        adjusted_tm, adjusted_tx, adjusted_tr, effect_values = self.calculate_special_effects(turn_idx)
        
        # Calculate total buildings powered
        buildings_powered = self.calculate_buildings_powered(effect_values)
        
        # Handle accumulators
        buildings_powered = self.handle_accumulators(buildings_powered, adjusted_tm, adjusted_tx, effect_values)
        
        # Calculate maintenance costs
        maintenance_cost = sum(r.resource.RP for r in self.active_resources)
        
        # Calculate profit
        turn_profit = 0
        if buildings_powered >= adjusted_tm:
            effective_buildings = min(buildings_powered, adjusted_tx)
            turn_profit = effective_buildings * adjusted_tr
            
        # Update budget
        self.budget += turn_profit - maintenance_cost
        self.total_profit += turn_profit
        
        # Debug information
        print(f"\nTurn {turn_idx}:")
        print(f"  Adjusted min buildings: {adjusted_tm}, max: {adjusted_tx}, profit/building: {adjusted_tr}")
        print(f"  Buildings powered: {buildings_powered}")
        print(f"  Maintenance cost: {maintenance_cost}")
        print(f"  Turn profit: {turn_profit}")
        print(f"  New budget: {self.budget}")
        print(f"  Total profit so far: {self.total_profit}")
        
        return True
        
    def simulate_game(self, purchases):
        """Simulate entire game with given purchases"""
        self.budget = initial_budget
        self.active_resources = []
        self.total_profit = 0
        
        for turn_idx in range(len(self.turns)):
            # Check if we have purchases for this turn
            resource_ids = None
            for purchase in purchases:
                if purchase[0] == turn_idx:
                    resource_ids = purchase[1:]
                    break
                    
            # Simulate turn
            if not self.simulate_turn(turn_idx, resource_ids):
                print(f"Simulation failed at turn {turn_idx}")
                return False
                
        return self.total_profit

