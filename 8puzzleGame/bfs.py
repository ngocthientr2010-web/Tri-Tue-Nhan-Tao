import queue

class Node:
    def __init__(self, state, parent=None, move=None, cost=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.cost = cost

def apply_move(state, curr_zero_pos, new_zero_pos) -> str:
    state = list(state)

    state[curr_zero_pos], state[new_zero_pos] = state[new_zero_pos], state[curr_zero_pos]

    return ''.join(state)

DIR = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def get_possible_moves(zero_pos) -> list:
    moves = []

    x = zero_pos // 3 
    y = zero_pos % 3
    for r, c in DIR:
        new_x, new_y = x + r, y + c
        if 0 <= new_x < 3 and 0 <= new_y < 3:
            new_zero_pos = new_x * 3 + new_y
            moves.append(new_zero_pos)

    return moves

# Get the move name based on the old and new position of the zero tile (0-8: board is fattened) 
def get_move_name(old_pos, new_pos) -> str:

    diff = new_pos - old_pos

    if diff == -3:
        return "UP"

    if diff == 3:
        return "DOWN"

    if diff == -1:
        return "LEFT"

    if diff == 1:
        return "RIGHT"


def get_solution(node) -> list:

    path = []

    while node.parent is not None:

        path.append(node.move)

        node = node.parent

    path.reverse()

    return path

def board_to_string(board):

    return ''.join(str(num) for num in board)

def BFS(initial_state, target_state):

    if initial_state == target_state:
        return []

    initial_state = board_to_string(initial_state)
    target_state = board_to_string(target_state)

    frontier = queue.Queue()
    explored = set()
    frontier_states = set()

    start_node = Node(initial_state)
    frontier.put(start_node)
    frontier_states.add(initial_state)

    while not frontier.empty():
        node = frontier.get()

        frontier_states.remove(node.state)
        explored.add(node.state)

        zero_pos = node.state.index('0')

        for next_move in get_possible_moves(zero_pos):

            child_state = apply_move(node.state, zero_pos, next_move)

            if child_state == target_state:
                return get_solution(child_node)

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

            frontier.put(child_node)
            frontier_states.add(child_state)

    return None
