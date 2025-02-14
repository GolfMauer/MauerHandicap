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
        average = stats.mean(differentials[:2])
        handicap = round(average - 1, 1)
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
    
    # checks if at least 54 holes where played
    enoughHoles = sum([len(game["shots"]) for game in games]) >= 54

    # implements 5.3
    if handicap > 54 or enoughHoles: handicap = 54
        
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
    total = sum(game["shots"])
    adjusted = adjustGrossScore(total)
    

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
        raise ValueError(f"Invalid parameter: len(game[\"shots\"]) = {len(game["shots"])}. The game needs to have 9 or more holes.")
    
    game["handicap_dif"] = roundHalfUp(differential, 1)

    return game
