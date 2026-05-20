from utils import *

def depth_limited(initial_state: list, target_state: list, limit: int) -> list:
    initial_state = board_to_string(initial_state)
    target_state = board_to_string(target_state)

    def DLS(node: Node, depth: int) -> list:
        if node.state == target_state:
            return get_solution(node)
        
        if depth == 0:
            return None
        
        zero_pos = node.state.index('0')

        for next_move in get_possible_moves(zero_pos):
            child_state = apply_move(node.state, zero_pos, next_move)
            move_name = get_move_name(zero_pos, next_move)
            child_node = Node(
                child_state,
                node,
                move_name,
                node.cost + 1
            )
            result = DLS(child_node, depth - 1)
            if result is not None:
                return result

        return None

    start_node = Node(initial_state)
    return DLS(start_node, limit)
