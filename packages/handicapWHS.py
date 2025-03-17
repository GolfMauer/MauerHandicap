# sauce https://www.usga.org/handicapping/roh/2020-rules-of-handicapping.html
import statistics as stats
from handicapEGA import roundHalfUp, spreadPlayingHC

# implements 5.2a
def handicap(games: list[dict], lowHandicap: float) -> float:
    """
    calculates the handicap given 0 to 20 games and returns the handicap unrounded. 
    
    Args:
    games (list[dict]): up to the last 20 games
    lowHandicap (float): The Low Handicap Index represents the last 365-day period preceding the day 
        on which the most recent score in their scoring record was played.

    Returns:
    float: The handicap index
    """

    if not (len(games) <= 20):
        raise ValueError(f"Invalid parameter: len(games) = {len(games)}. You can only add a max of 20 games.")

    #implements 5.2a
    numGames = len(games)
    differentials = []
    for game in games:
        # implements 5.9
        differentials.append(game["handicap_dif"] + game["exceptional_reduction"])
    differentials.sort()
    
    if numGames <= 3:
        handicap = differentials[0] - 2
    elif numGames == 4:
        handicap = differentials[0] - 1
    elif numGames == 5:
        handicap = differentials[0]
    elif numGames == 6:
        handicap = stats.mean(differentials[:2]) - 1
    elif numGames <= 8:
        handicap = stats.mean(differentials[:2])
    elif numGames <= 11:
        handicap = stats.mean(differentials[:3])
    elif numGames <= 14:
        handicap = stats.mean(differentials[:4])
    elif numGames <= 16:
        handicap = stats.mean(differentials[:5])
    elif numGames <= 18:
        handicap = stats.mean(differentials[:6])
    elif numGames == 19:
        handicap = stats.mean(differentials[:7])
    else:
        handicap = stats.mean(differentials[:8])

        # implements 5.7+8
        handicap = capIncrease(handicap, games, lowHandicap)
    
    # checks if at least 54 holes where played I do not know where the correlating rule was
    enoughHoles = sum([len(game["shots"]) for game in games]) >= 54

    # implements 5.3
    if handicap > 54 or not enoughHoles: handicap = 54
        
    return roundHalfUp(handicap, 1)


# implements 5.7+8
def capIncrease(handicap: float, games: list[dict], lowHandicap: float) -> float:
    """
    Applies soft/hard cap to the HCI.

    Args:
    handicap (float): The new Handicap Index
    game (list[dict]): the last 20 games
    lowHandicap (float): The 365 low of the Handicap Index
    """
    dif = handicap - lowHandicap
    # apply soft cap
    if 3.0 < dif < 5.0:
        handicap = handicap - 0.5*dif
    elif dif >= 5.0:
        handicap = lowHandicap["whs"] + 5.0
    
    return handicap


def handicapDifferential(game: dict, course: dict, handicapIndex:float) -> dict:
    """
    calculates the handicap differential for one game. And writes it to the game dict

    Args:
    game (dict): The game the calculation is being done on.
    course (dict): The course corresponding to the game.
    handicapIndex (float): The current handicap Index.

    Returns:
    dict: the game with the new entry
    """
    adjusted = adjustGrossScore(game, course, handicapIndex)
    

    # implements 5.1a and 2.2a
    if len(game["shots"]) > 9:
        differential =(adjusted - course["course_rating"] + game["pcc"] ) * (113 / course["slope_rating"])
    # implements 5.1b and 2.2b
    elif len(game["shots"]) == 9:
        # calculation according to https://serviceportal.dgv-intranet.de/regularien/whs-handicap-regeln/i22533_1_Handicap_Regeln_2024.cfm
        score = (adjusted - course["course_rating"] + 0.5 * game["pcc"] ) * (113 / course["slope_rating"])/2
        expectedScore = ((handicapIndex * 1.04) + 2.4) / 2
        differential = score + expectedScore
    else:
        raise ValueError(f"Invalid parameter: len(game[\"shots\"]) = {len(game["shots"])}. The game needs to have 9 or more played holes.")
    
    # implements 5.9 exceptional score reduction
    delta = handicapIndex - differential
    if delta >= 7 and delta < 10:
        game["exceptional_reduction"] = -1.0
    elif delta >= 10:
        game["exceptional_reduction"] = -2.0
    else:
        game["exceptional_reduction"] = 0.0
    
    game["handicap_dif"] = roundHalfUp(differential, 1)

    return game


def adjustGrossScore(game: dict, course: dict, handicapIndex: float) -> int:
    """
    Adjusts the score/strokes and applies net double bogey adjustment.

    Args:
    game (dict): The game the calculation is being done on.
    course (dict): The course corresponding to the game.
    handicapIndex (float): The current handicap Index.

    Returns:
    int: the adjusted score/strokes
    """
    # I am not 100% certain that playing HC is used here
    playingHandicap = calcPlayingHandicap(game, course, handicapIndex)

    shots: list[int] = game["shots"]
    par: list[int] = course["par"]
    # implements 3.1a
    if handicapIndex == 54:
        for i, shot in enumerate(shots):
            if shot > par[i] + 5:
                shots[i] = par[i] + 5
    # implements 3.1b
    elif playingHandicap >= 54:
        adjustedPar = spreadPlayingHC(course, sum(game["shots"]), game["is9Hole"])
        for i, shot in enumerate(shots):
            if shot > adjustedPar[i] + 2:
                if adjustedPar[i] + 2 - shot >= 4:
                    shots[i] = par[i] + 5
                else:
                    shots[i] = adjustedPar[i] + 2
    else:
        adjustedPar = spreadPlayingHC(course, sum(game["shots"]), game["is9Hole"])

        for i, shot in enumerate(shots):
            if shot > adjustedPar[i] + 2:
                shots[i] = adjustedPar[i] + 2

    return sum(shots)


def calcPlayingHandicap(game: dict, course: dict, handicapIndex: int) -> int:
    """
    calculates the Playing Handicap. By default it is equal to the course handicap

    Args:
    game (dict): The game the calculation is being done on.
    course (dict): The course corresponding to the game.
    handicapIndex (float): The current handicap Index.

    Returns:
    int: Rounded Playing Handicap
    """
    # implements 6.1a and implements 6.1b
    modifier = 2 if game["is9Hole"] else 1
    courseHandicap = handicapIndex * course["slope_rating"] / 113 + modifier*(course["course_rating"] - sum(course["par"]))

    # implements 6.2a
    handicapAllowance = 1 if game["handicap_allowance"] is None else game["handicap_allowance"]
    playingHandicap = courseHandicap * handicapAllowance

    return round(playingHandicap)
