import pyhop
import json

def check_enough (state, ID, item, num):
    if getattr(state,item)[ID] >= num: return []
    return False

def produce_enough (state, ID, item, num):
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method(name, rule):
    requires, consumes = rule
    def method(state, ID):
        task_list = [(name, ID)]

        for key, value in requires.items():
            task_list.insert(0, ('have_enough', ID, key, value))

        for key, value in consumes.items():
            if key in ['ingot', 'coal', 'ore', 'cobble', 'stick', 'plank', 'wood']:
                task_list.append(('have_enough', ID, key, value))

        return task_list

    return method


def declare_methods(data):
    method_groups = {}
    
    for item, recipe_data in data['Recipes'].items():
        produces = list(recipe_data['Produces'].keys())[0]
        time = recipe_data['Time']
        
        if produces not in method_groups:
            method_groups[produces] = []
        
        requires = recipe_data.get('Requires', {})
        consumes = recipe_data.get('Consumes', {})
        name = 'op_' + item
        m = make_method(name, [requires, consumes])
        m.__name__ = item
        method_groups[produces].append((time, m))
    

    for produces, methods in method_groups.items():
        methods = sorted(methods, key=lambda x: x[0])  # Sort the methods by time
        name = 'produce_' + produces
        method_list = [name] + [m[1] for m in methods]
        pyhop.declare_methods(*method_list)

    return

def make_operator(rule):
    requires, consumes, produces, time = rule

    def operator(state, ID):
        # Check if all requirements are met before producing anything
        for key, value in requires.items():
            if value > getattr(state, key, {}).get(ID, 0):
                return False
        def is_available(item, num):
            return getattr(state, item)[ID] >= num

        for key, value in requires.items():
            if value > getattr(state, key)[ID]:
                # If the required item is not available, check if we can obtain it with existing tools
                if key == 'stone':
                    if not is_available('wooden_pickaxe', 1) and is_available('iron_pickaxe', 1):
                        return False
                else:
                    return False

        if time > state.time[ID]:
            return False

        for key, value in consumes.items():
            state_item = getattr(state, key)
            state_item[ID] -= value

        for key, value in produces.items():
            state_item = getattr(state, key)
            state_item[ID] += value

        state.time[ID] -= time
        return state

    return operator

def declare_operators(data):
    # Create a dictionary to store operators for each type of item
    operators_dict = {}

    for item, recipe_data in data['Recipes'].items():
        requires = recipe_data.get('Requires', {})
        consumes = recipe_data.get('Consumes', {})
        produces = recipe_data['Produces']
        time = recipe_data['Time']

        rule = [requires, consumes, produces, time]
        operator = make_operator(rule)
        operator.__name__ = 'op_' + item

        produces_item = list(produces.keys())[0]
        if produces_item not in operators_dict:
            operators_dict[produces_item] = []

        # Sort the operators by time (ascending order)
        operators_dict[produces_item].append((time, operator))
        operators_dict[produces_item].sort(key=lambda x: x[0])

    # Flatten the dictionary values into a list of tuples and sort by time
    operators_list = [(op[0], op[1]) for ops in operators_dict.values() for op in ops]
    operators_list.sort(key=lambda x: x[0])

    pyhop.declare_operators(*[operator for _, operator in operators_list])

    return
    
    # prune search branch if heuristic() returns True
    # do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
    # e.g. def heuristic2(...); pyhop.add_check(heuristic2)
def add_heuristic(data, ID):
    # Use a dictionary to store the count of crafted tools
    crafted_tools = {tool: 0 for tool in data["Tools"]}

    def check_heuristics(state, curr_task, tasks, plan, depth, calling_stack):
        
        # initialize crafted tools count at depth 0
        if depth == 0:
            for tool in data["Tools"]:
                crafted_tools[tool] = 0

        # prune if a tool is already crafted before crafting again
        if curr_task[0] == 'produce':
            item = curr_task[2]
            for tool in data["Tools"]:
                if item == tool:
                    if crafted_tools[tool] != 0:
                        return True
                    else:
                        crafted_tools[tool] += 1
                        return False

    pyhop.add_check(check_heuristics)


def set_up_state (data, ID, time=0):
    state = pyhop.State('state')
    state.time = {ID: time}

    for item in data['Items']:
        setattr(state, item, {ID: 0})

    for item in data['Tools']:
        setattr(state, item, {ID: 0})

    for item, num in data['Initial'].items():
        setattr(state, item, {ID: num})

    return state

def set_up_goals (data, ID):
    goals = []
    for item, num in data['Goal'].items():
        goals.append(('have_enough', ID, item, num))

    return goals

if __name__ == '__main__':
    rules_filename = 'crafting.json'

    with open(rules_filename) as f:
        data = json.load(f)

    state = set_up_state(data, 'agent', time=300) # allot time here
    goals = set_up_goals(data, 'agent')

    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')

    #pyhop.print_operators()
    #pyhop.print_methods()

    # Hint: verbose output can take a long time even if the solution is correct; 
    # try verbose=1 if it is taking too long
    pyhop.pyhop(state, goals, verbose=3)
    # pyhop.pyhop(state, goals, verbose=3)
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)