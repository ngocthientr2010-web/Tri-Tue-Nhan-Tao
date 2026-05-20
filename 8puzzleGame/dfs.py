from utils import *
from collections import deque

def DFS(initial_state: list, target_state: list) -> list:
    if initial_state == target_state:
        return []

    initial_state = board_to_string(initial_state)
    target_state = board_to_string(target_state)

    frontier = deque()
    explored = set()
    frontier_states = set()

    start_node = Node(initial_state)
    frontier.append(start_node)
    frontier_states.add(initial_state)

    while frontier:
        node = frontier.pop()

        frontier_states.remove(node.state)
        explored.add(node.state)

        zero_pos = node.state.index('0')

        for next_move in get_possible_moves(zero_pos):

            child_state = apply_move(node.state, zero_pos, next_move)
            if child_state in explored or child_state in frontier_states:
                continue

            move_name = get_move_name(
                zero_pos,
                next_move
            )

            child_node = Node(
                child_state,
                node,
                move_name,
                node.cost + 1
            )

            if child_state == target_state:
                return get_solution(child_node)

            frontier.append(child_node)
            frontier_states.add(child_state)

    return None
