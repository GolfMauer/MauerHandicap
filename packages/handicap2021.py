def handicap(games: list[dict]) -> float:
    """
    calculates the handicap given 0 to 20 games and returns the handicap unrounded. 
    
    Args:
    games (list[dict]): up to the last 20 games

    Returns:
    float: The handicap
    """

    if not (len(games) <= 20):
        raise ValueError(f"Invalid parameter: len(games) = {len(games)}. You can only add a max of 20 games.")

    handicap = 54 
    numHoles = 0
    for game in games:
        numHoles += len[game["shots"]] #shots is the array that tracks the amount of shots per hole
    numGames = len(games)

    if numHoles < 54:
        return handicap

    
    differentials = []
    for game in games:
        differentials.append(game["handicap_dif"])
    differentials.sort()
    
    if numGames <= 3:
        handicap = differentials[0] - 2
    elif numGames == 4:
        handicap = differentials[0] - 1
    elif numGames == 5:
        handicap = differentials[0]
    elif numGames == 6:
        average = (differentials[0] + differentials[1])/2
        handicap = round(average - 1, 1)
    elif numGames <= 8:
        handicap = (differentials[0] + differentials[1])/2
    elif numGames <= 11:
        handicap = sum(differentials[0:3])/3
    elif numGames <= 14:
        handicap = sum(differentials[0:4])/4
    elif numGames <= 16:
        handicap = sum(differentials[0:5])/5
    elif numGames <= 18:
        handicap = sum(differentials[0:6])/6
    elif numGames == 19:
        handicap = sum(differentials[0:7])/7
    else:
        bestGames = differentials[0:8] #slice the best 8 games
        handicap = sum(bestGames)/8
    
    return handicap


def calcDifferential(shots: list[int], courseRating: int, slopeRating: int, pcc: int) -> float:
    """
    simple helper to calculate the differential

    Args:
    shots (list[int]): list of the shots taken
    courseRating (int): rating of the course
    slopeRating (int): rating of the slope
    pcc (int): adjustment for weather
    """

    total = sum(shots)
    #TODO consider unfinished games
    if len(shots) == 18:
        differential =(total - courseRating + pcc )* (113 / slopeRating)
    elif len(shots) == 9:
        #TODO An 18 hole differential is created by combining the 9 hole with the expected score over 9 holes
        #wouldn't that mean that we have to support both 9 hole handicap and 18 hole handicap
        #requiring to handle them separately?
        differential =(total - courseRating + 0.5*pcc )* (113 / slopeRating)

    return round(differential, 1)

def handicapDifferential(game: dict, course: dict) -> dict:
    """
    calculates the handicap differential for one game

    Args:
    game (dict): The game the calculation is being done on.
    course (dict): The course corresponding to the game.

    Returns:
    dict: the game with the new entry
    """
    differential = calcDifferential(game["shots"], course["course_rating"], course["slope_rating"], game["pcc"])
    
    game["handicap_dif"] = differential

    return game


def handicapDifferentialNet(handicap: float, game: dict, course: dict) -> dict:
    """
    calculates the handicap differential for one game using net shots.
    Often used for more casual games can not be used for the Handicap without conversion

    Args:
    handicap (float): The players current handicap
    game (dict): The game the calculation is being done on.
    course (dict): The course corresponding to the game.

    Returns:
    dict: the game with the new entry
    """
    #TODO dry code
    net = sum(game["shots"]) - handicap
    differential = ((net - course["course_rating"]) * 113 / course["slope_rating"]) + game["pcc"]
    
    game["differential_net"] = round(differential, 2)

    return game


def handicapDifferentialStableford(game: dict, course: dict) -> dict:
    """
    calculates the handicap differential for one game using the Stableford system.
    Often used for more casual games can not be used for the Handicap without conversion.
    NOTE: Requires the net differential to be written before this function is called.

    Args:
    game (dict): The game the calculation is being done on.
    course (dict): The course corresponding to the game.

    Returns:
    dict: the game with the new entry
    """
    
    handicapNet = game["handicap_net"]
    strokesPerHole = distributeStrokes(handicapNet, len(course["par"]))

    stablefordPoints = 0

    for index, (par, shots) in enumerate(zip(course["par"], game["shots"])):
        handicapStrokes = strokesPerHole[index]
        netScore = shots - handicapStrokes

        if netScore <= par - 2:
            stablefordPoints += 4 + (par - netScore)
        elif netScore == par - 1:
            stablefordPoints += 3
        elif netScore == par:
            stablefordPoints += 2
        elif netScore == par + 1:
            stablefordPoints += 1
        else:
            stablefordPoints += 0
    
    game["stableford"]  = stablefordPoints

    return game


def distributeStrokes(handicapNet: float, holes: int) -> list[int]:
    """
    distributes the handicap on the number of holes

    Args:
    handicapNet (float): the players net handicap rounded to two decimals
    holes (int): number of holes on the course

    Returns:
    list[int]: the number of strokes per hole
    """
    baseStrokes = handicapNet // holes
    remainder = handicapNet % holes

    strokes = [baseStrokes] * holes
    for i in range(remainder):
        strokes[i] += 1
    
    return strokes