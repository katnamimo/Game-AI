

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


# new helper functions to check things

# is an enemy ship going to attack a planet that we have conquered?
def under_attack(state):
    for enemy_ship in state.enemy_fleets():
        if enemy_ship.destination_planet in [planet.ID for planet in state.my_planets()]:
            return True
    return False

# check if strongest enemy planet has less ships than our weakest planet
# easy to conquer this planet since it is not stronger than our weakest planet
def is_enemy_weak(state):
    if not state.enemy_planets() or not state.my_planets():
        return False
    weakest_my_planet = min(state.my_planets(), key=lambda p: p.num_ships)
    strongest_enemy_planet = max(state.enemy_planets(), key=lambda p: p.num_ships)
    return strongest_enemy_planet.num_ships < weakest_my_planet.num_ships

# checks which player has the largest number of ships
# true if player 1 (us)
# false if the enemy ships outnumber us
def who_has_largest_fleet(state):
    my_planet_ships = sum(planet.num_ships for planet in state.my_planets())
    my_fleet_ships = sum(fleet.num_ships for fleet in state.my_fleets())
    my_total_ships = my_planet_ships + my_fleet_ships

    enemy_planet_ships = sum(planet.num_ships for planet in state.enemy_planets())
    enemy_fleet_ships = sum(fleet.num_ships for fleet in state.enemy_fleets())
    enemy_total_ships = enemy_planet_ships + enemy_fleet_ships

    return my_total_ships > enemy_total_ships