import string


def hex2rgb(h):
    v = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return [x/255 for x in v]


def interpolate(start_color, goal_color, steps):
    """
    Take two RGB color sets and mix them over a specified number of steps.  Return the list
    """
    start_color = hex2rgb(start_color)
    goal_color = hex2rgb(goal_color)

    R = start_color[0]
    G = start_color[1]
    B = start_color[2]

    targetR = goal_color[0]
    targetG = goal_color[1]
    targetB = goal_color[2]

    DiffR = targetR - R
    DiffG = targetG - G
    DiffB = targetB - B

    for i in range(0, steps +1):
        iR = R + (DiffR * i / steps)
        iG = G + (DiffG * i / steps)
        iB = B + (DiffB * i / steps)

        yield (iR, iG, iB)