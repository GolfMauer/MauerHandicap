# sauce https://www.usga.org/handicapping/roh/2020-rules-of-handicapping.html
import statistics as stats
from handicapEGA import roundHalfUp, spreadPlayingHC

# implements 5.2a
def handicap(games: list[dict]) -> float:
    """
    calculates the handicap given 0 to 20 games and returns the handicap unrounded. 
    
    Args:
    games (list[dict]): up to the last 20 games

    Returns:
    float: The handicap index
    """

    if not (len(games) <= 20):
        raise ValueError(f"Invalid parameter: len(games) = {len(games)}. You can only add a max of 20 games.")

    #implements 5.2a
    numGames = len(games)
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
    
    # checks if at least 54 holes where played I do not know where the correlating rule was
    enoughHoles = sum([len(game["shots"]) for game in games]) >= 54

    # implements 5.3
    if handicap > 54 or not enoughHoles: handicap = 54
        
    return roundHalfUp(handicap, 1)


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
        differential =(adjusted - course["course_rating"] + game["pcc"] ) * (113 / course["slopeRating"])
    # implements 5.1b and 2.2b
    elif len(game["shots"]) == 9:
        # calculation according to https://www.reddit.com/r/golf/comments/1iolhhm/comment/mckr1ic/?context=3
        score = (adjusted - course["course_rating"] + 0.5 * game["pcc"] ) * (113 / course["slopeRating"])
        expectedScore = 0.52 * handicapIndex + 1.2
        differential = score + expectedScore
    else:
        raise ValueError(f"Invalid parameter: len(game[\"shots\"]) = {len(game["shots"])}. The game needs to have 9 or more played holes.")
    
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
        adjustedPar = spreadPlayingHC(course, game["shots"], game["is9Hole"])
        for i, shot in enumerate(shots):
            if shot > adjustedPar[i] + 2:
                if adjustedPar[i] + 2 - shot >= 4:
                    shots[i] = par[i] + 5
                else:
                    shots[i] = adjustedPar[i] + 2
    else:
        # TODO discuss if it is truly the same way in EGA and WHS
        adjustedPar = spreadPlayingHC(course, game["shots"], game["is9Hole"])
        for i, shot in enumerate(shots):
            if shot > adjustedPar[i] + 2:
                shots[i] = adjustedPar[i] + 2


#
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
    courseHandicap = handicapIndex * course["slope_rating"] / 113 + modifier*(course["course_rating" - sum(course["par"])])

    # implements 6.2a
    handicapAllowance = 1 if game["handicap_allowance"] is None else game["handicap_allowance"]
    playingHandicap = courseHandicap * handicapAllowance

    return round(playingHandicap)

#TODO
#5.4 and 5.7 - 5.9 but rely on cron jub would handle them on different branch