
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

#import p2_t3

num_nodes = 1000
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """

    #will need something to detect if all nodes have been searched


    #if no more unexplored actions
    if( len(node.untried_actions)==0 ):

        num=0
        bestnode=node

        #go through each node and find the optimal one
        for x in node.child_nodes:
            #get node
            current=node.child_nodes[x]
            #get number
            num_current=(current.wins / current.visits) + (explore_faction * sqrt( log(node.visits )/ current.visits) )

            #if node has no children then go to next node to search --old fix for the recursive loop--
            #if len(current.child_nodes)==0 and len(current.untried_actions)==0:
            #    continue

            #if theres a better node
            if(num_current>num):
                num=num_current
                bestnode=current

        #node has been chosen  

        #if still on the same node 
        if(bestnode==node):
            return bestnode,state

        state=board.next_state(state, bestnode.parent_action)
        return traverse_nodes(bestnode, board, state, identity) 
            


    #there is an unexplored action
    else:


        #make child node
        child=expand_leaf(node, board, state)

        #add child to current node
        node.child_nodes[node.untried_actions[0]]=child

        #pop action from list
        node.untried_actions.pop(0)

        state=board.next_state(state, child.parent_action)

        return child,state


    
    # Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """

    #makes new node

    new_node =  MCTSNode(parent=node, parent_action=  node.untried_actions[0] , action_list=board.legal_actions(state))


    return new_node
    # Hint: return new_node


def rollout(board, state):
    """Given the state of the game, the rollout plays out the remainder using a heuristic strategy.

    Args:
        board: The game setup.
        state: The state of the game.

    Returns:
        The win values of the final state after performing the rollout.
    """

    # Check if the game has already ended
    if board.is_ended(state):
        return board.win_values(state)

    # Get the current player
    current_player = board.current_player(state)

    # Check if the current player has an instant win move
    legal_actions = board.legal_actions(state)
    for action in legal_actions:
        new_state = board.next_state(state, action)
        win_values = board.win_values(new_state)
        if win_values and win_values[current_player] == 1:
            return win_values

    # Perform a heuristic rollout
    owned_boxes = board.owned_boxes(state)

    while not board.is_ended(state):
        # Choose a random action
        action = choice(board.legal_actions(state))
        state = board.next_state(state, action)

    return board.win_values(state)



def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """

    #if not at root
    if node != None:

        #add won to win
        #won will be 1 if its a win and 0 if a loss
        node.wins+=won
        #add 1 to visit
        node.visits+=1
        
        #recurse
        backpropagate(node.parent,won)



def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)

    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!

        #find new node
        node,sampled_game=traverse_nodes(node,board,sampled_game,identity_of_bot)
     
        #rollout from node
        win_num=rollout(board, sampled_game)
  
        #backpropagate winner
        backpropagate(node, win_num[identity_of_bot])

    #now the best move needs to be found
    bestmove=()
    bestwin=0
 
    for x in root_node.child_nodes:
        #get current node and find its win rate
        current=root_node.child_nodes[x]

        #find the win rate
        current_win=current.wins/current.visits

        #find any instant lose moves for opponent
     

        # if new best win rate is found and if there are less instant lose moves
        if current_win >= bestwin :
            #update bestwin
            bestwin=current_win
            #update bestmove
            bestmove=x



    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return bestmove
