import depth_limited as helper

def IDDFS(initial_state: list, target_state: list) -> list:

    result = None
    depth = 0
    while result is None:
        result = helper.depth_limited(initial_state, target_state, depth)
        depth += 1
    
    return result
