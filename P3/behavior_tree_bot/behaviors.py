import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from math import ceil


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    # if len(state.my_fleets()) >= 1:
    #     return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    # if len(state.my_fleets()) >= 1:
    #     return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


# attack enemy planet with the highest growth rate
def attack_strategically(state):
    if not state.my_planets() or not state.enemy_planets():
        return False

    # find our strongest planet with the most ships
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships)

    # find enemy planet with highest growth rate
    target_planet = max(state.enemy_planets(), key=lambda t: t.growth_rate)
    # target_planet = max(state.enemy_planets(), key=lambda t: t.growth_rate / (expected_fleet(state, strongest_planet, t) + 1))


    return issue_order(state, strongest_planet.ID, target_planet.ID, strongest_planet.num_ships // 2)

# attack neutral planets with the highest growth rates
def spread_to_high_growthrate_planet(state):
    # check if planet is not ours already or a neutral planet
    if not state.my_planets() or not state.neutral_planets():
        return False

    # get our strongest planet with the most ships
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships)
    
    # find the best high growthrate planet to attack
    best_planet = max(state.neutral_planets(), key=lambda p: p.growth_rate / ((p.num_ships + p.growth_rate * state.distance(strongest_planet.ID, p.ID) + 1) * state.distance(strongest_planet.ID, p.ID)))

    return issue_order(state, strongest_planet.ID, best_planet.ID, strongest_planet.num_ships // 2)

# this helps beat defensive bot
def defend_weakest_planet(state):
    weakest_planet = min(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if not weakest_planet:
        return False

    nearby_planets = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, weakest_planet.ID))
    if len(nearby_planets) < 2:
        return False

    planet1, planet2 = nearby_planets[:2]
    num_ships_to_send = ceil(0.5 * min(planet1.num_ships, planet2.num_ships))

    return issue_order(state, planet1.ID, weakest_planet.ID, num_ships_to_send) and \
           issue_order(state, planet2.ID, weakest_planet.ID, num_ships_to_send)