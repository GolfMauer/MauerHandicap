def handicap(games: list[dict]) -> float:
    """calculates the handicap given 0 to 20 games. 
    
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
    
    if numGames == 3:
        value = differentials[0]
    elif numGames == 4:
        value = differentials[0] - 1
    elif numGames == 5:
        value = differentials[0] - 2
    elif numGames == 6 or numGames == 7:
        average = (differentials[0] + differentials[1])/2
        value = round(average - 1, 1)
    elif numGames >= 8:
        bestGames = differentials[0:7] #slice the best 8 games
        average = sum(bestGames)/8
        value = round(average, 1)
    handicap[i] = value
    
    return handicap


def handicapDifferential(game: dict, course: dict) -> float:
    """
    calculates the handicap differential for one game

    Args:
    game (dict): The game the calculation is being done on.
    course (dict): The course corresponding to the game.

    Returns:
    float: gross handicap differential
    """
    shots = sum(game["shots"])
    return ((shots - course["course_rating"]) * 113 / course["slope_rating"]) + game["pcc"]


def handicapDifferentialNet(game: dict, course: dict) -> float:
    """
    calculates the handicap differential for one game using net shots.
    Often used for more casual games can not be used for the Handicap without conversion

    Args:
    game (dict): The game the calculation is being done on.
    course (dict): The course corresponding to the game.

    Returns:
    float: gross handicap differential
    """
    print("a")


def handicapDifferentialStableford(game: dict, course: dict) -> float:
    """
    calculates the handicap differential for one game using the Stableford system
    Often used for more casual games can not be used for the Handicap without conversion

    Args:
    game (dict): The game the calculation is being done on.
    course (dict): The course corresponding to the game.

    Returns:
    float: gross handicap differential
    """
    print("a")


#highest priority at the top
#TODO fill out the differential functions
#TODO build packages
#TODO create ui
#TODO Soft- / Hardcap on handicap increase