import depth_limited as helper

def IDDFS(initial_state: list, target_state: list) -> list:

    result = None
    depth = 0
    while result is None:
        result = helper.depth_limited(initial_state, target_state, depth)
        depth += 1
    
    return result

# start_state = [1, 2, 3, 4, 5, 6, 0, 7, 8]
# target_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# print(iterative_deepening(start_state, target_state))