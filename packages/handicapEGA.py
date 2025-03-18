# sauce https://www.ega-golf.ch/sites/default/files/hcp_booklet_2019_final_0.pdf
import math

BUFFER_UPPER_LIMIT = 36
BELOW_BUFFER_ADD = 0.1
BUFFER_LOWER_LIMIT_9HOLE = [None, 35, 35, 34, 33, None]


# implements p.25 3.11.5
def initialHandicap(stablefordScore: int, nineHole: bool) -> float:
    """
    Calculates handicap for a player based on their score and whether they played a nine-hole game.

    Args:
        stablefordScore (int): The player's Stableford score.
        nineHole (bool): True if the game was a nine-hole game, False otherwise.

    Returns:
        float: The handicap after the first game played.
    """
    if nineHole:
        stablefordScore += 18
    return min(54 - (stablefordScore - 36), 54)

def calculateNewHandicap(game: dict, cba: int, previousHandicap: float, course: dict) -> float:
    """
    Calculate the new handicap based on the game results, course conditions, and previous handicap.
    
    Args:
        game (dict): A dictionary containing game details, including shots taken.
        cba (int): The Computed Buffer Adjustment (CBA) value.
    Returns:
        float: The new calculated handicap.
    """
    
    # TODO: error for 9 hole with cat 1? -> no buffer zone given
    if previousHandicap is None:
        stableford = convertToStableford(game["shots"], course["par"])
        return initialHandicap(stableford, game["is9Hole"])
    
    handicapStrokes = playingHandicap(game["is9Hole"], previousHandicap, course["course_rating"], course["slope_rating"], sum(course["par"]))

    # implements p.24 3.9.7
    # assigning handicap strokes
    par = spreadPlayingHC(course, handicapStrokes, game["is9Hole"])
    
    stableford = convertToStableford(game["shots"], par)
    
    # if 9-hole, add 18 points, to be RECORDED
    if game["is9Hole"]:
        stableford += 18

    adjustment = calculateAdjustment(stableford, previousHandicap, cba, game["is9Hole"])

    return previousHandicap + adjustment

def ganzzahligeDivision(dividend: float, divisor: float) -> float:
    if dividend < 0:
        dividend *= -1
        return -(dividend // divisor) 
    return dividend // divisor

def spreadPlayingHC(course: dict, handicapStrokes: int, is9Hole: bool) -> list:
    par = course["par"].copy()
    strokeIndex = course["handicap_stroke_index"].copy()
    
    holecount_modifier = 9 if is9Hole else 18

    everyHole = ganzzahligeDivision(handicapStrokes, holecount_modifier)
    
    hc_stroke_modifier = 1 if handicapStrokes > 0 else -1

    rem = handicapStrokes - hc_stroke_modifier*(everyHole * holecount_modifier)
    
    # this creates tuples from the stroke index and a list from 1 to 9
    # and sorts based on the first number (original stroke index), which
    # creates a new stroke index with the same order using numbers 1-9
    if is9Hole:
        sorted_tuples = sorted(zip(strokeIndex, list(range(1,10))))
        for i, (_, new_index) in enumerate(sorted_tuples):
            strokeIndex[i] = new_index

    for i in range(holecount_modifier):
        par[i] += everyHole
        if strokeIndex[i] <= rem:
            par[i] += hc_stroke_modifier
    
    return par

# implements 3.10
def convertToStableford(shots: list[int], adjustedPar: list[int]) -> int:
    """
    Converts golf scores to Stableford points.
    
    Args:
        shots (list[int]): A list of the number of shots taken on each hole.
        adjustedPar (list[int]): A list of the adjusted par for each hole.

    Returns:
        int: The total Stableford score for the round.
    """
    score = 0
    for i in range(len(shots)):  # Corrected range to len(shots)
        score += max(0, 2 - (shots[i] - adjustedPar[i]))
    return score

# implements p24 3.9.3
def roundHalfUp(n, decimals=0) -> float:
    """
    Rounds a number to a specified number of decimal places using the "round half up" strategy. (Always round up on 0.5)
    
    Args:
        n (float): The number to be rounded.
        decimals (int, optional): The number of decimal places to round to. Defaults to 0.
    Returns:
        float: The rounded number.
    """
    
    multiplier = 10**decimals
    return math.floor(n * multiplier + 0.5) / multiplier

def playingHandicap18(handicap: float, courseRating: float, slopeRating: float, par: int) -> int:
    """
    Calculate the playing handicap for an 18-hole round of golf.
    
    Args:
        handicap (float): The player's handicap index.
        courseRating (float): The course rating, which represents the difficulty of a course for a scratch golfer.
        slopeRating (float): The slope rating, which represents the relative difficulty of a course for a bogey golfer compared to a scratch golfer.
        par (int): The par for the course.
        
    Returns:
        int: The calculated playing handicap, rounded to the nearest integer.
    """

    # implements p24 3.9.3
    # category 1-5
    if handicapToCategory(handicap) < 6:
        raw = handicap * (slopeRating / 113) + (courseRating - par)
    # category 6
    else:
        raw = handicap + playingHandicapDifferential(False, courseRating, slopeRating, par)

    # implements p24 3.9.3
    return int(roundHalfUp(raw))

def playingHandicap9(handicap: float, courseRating: float, slopeRating: float, par: int) -> int:
    """
    Calculate the playing handicap for an 9-hole round of golf.
    
    Args:
        handicap (float): The player's handicap index.
        courseRating (float): The 9 hole course rating, which represents the difficulty of a course for a scratch golfer.
        slopeRating (float): The 9 hole slope rating, which represents the relative difficulty of a course for a bogey golfer compared to a scratch golfer.
        par (int): The 9 hole par for the course.
        
    Returns:
        int: The calculated playing handicap, rounded to the nearest integer.
    """
    category = handicapToCategory(handicap)
    # implements p22 3.9.4a
    raw = 0
    if category > 1 and category < 6:
        raw = (handicap * (slopeRating / 113)) / 2 + (courseRating - par)
    if category == 6:
        raw = handicap / 2 + playingHandicapDifferential(True, courseRating, slopeRating, par)
    
    return int(roundHalfUp(raw))

def playingHandicap(is9Hole: bool, handicap: float, courseRating: float, slopeRating: float, par: int) -> int:
    """
    Calculate the playing handicap for a golfer based on whether they are playing a 9-hole or 18-hole course.
    The playing handicap describes the amount of strokes a player receivees on a given course for their handicap.
    
    Args:
        is9Hole (bool): True if the golfer is playing a 9-hole course, False if playing an 18-hole course.
        handicap (float): The golfer's handicap index.
        courseRating (float): The course rating of the golf course.
        slopeRating (float): The slope rating of the golf course.
        par (int): The par of the golf course.
        
    Returns:
        int: The calculated playing handicap.
    """
    
    if is9Hole:
        return playingHandicap9(handicap, courseRating, slopeRating, par)
    return playingHandicap18(handicap, courseRating, slopeRating, par)

# implements p.13 handicap category
def handicapToCategory(handicap: float) -> int:
    """
    Converts handicap index to handicap category

    Args:
        handicap (float): The player's handicap index.

    Returns:
        int: The player's handicap category corresponding to their handicap index.
    """
    if handicap < 4.5:
        return 1
    elif handicap < 11.5:
        return 2
    elif handicap < 18.5:
        return 3
    elif handicap < 26.5:
        return 4
    elif handicap < 37:
        return 5
    return 6

# implements p.12 buffer zone
def catToLowerBuffer(is9Hole: bool, category: int) -> int:
    """
    Caculates the lower buffer zone limit for a category.

    Args:
        is9Hole (bool): True if 9-hole game, false if 18-hole game.
        category (int): The player's handicap category.

    Returns:
        int: Lower buffer zone limit for given category.
    """
    if is9Hole:
        return BUFFER_LOWER_LIMIT_9HOLE[category-1]
    return BUFFER_UPPER_LIMIT - category

# implements p22 3.9.4
def playingHandicapDifferential(nineHole: bool, courseRating: float, slopeRating: float, par: int) -> float:
    """
    Calculate the playing handicap differential for a golf course.
    
    Args:
        nineHole (bool): Indicates if the course is a nine-hole course.
        courseRating (float): The course rating of the golf course.
        slopeRating (float): The slope rating of the golf course.
        par (int): The par for the course.
    
    Returns:
        float: The playing handicap differential.
    """
    if nineHole:
        return playingHandicap9(36.0, courseRating, slopeRating, par) - 18.0
    else:
        return playingHandicap18(36.0, courseRating, slopeRating, par) - 36.0

def calculateAdjustment(stablefordScore: int, handicap: float, cba: int, is9Hole: bool) -> float:
    """
    Calculates adjustment to handicap index.

    Args:
        stablefordScore (int): Stableford score achieved including allotted handicap strokes.
        handicap (float): The player's current handicap
        cba (int): The Calculated Buffer Adjustment of the game played.

    Returns:
        float: Amount to adjust handicap by.
    """
    adjustment = 0
    category = handicapToCategory(handicap)
    if category == 6:
        cba = 0 # cba does not apply to cat 6
    if (category == 1 and is9Hole):
        return 0


    if stablefordScore > BUFFER_UPPER_LIMIT + cba:
        for _ in range(stablefordScore - (BUFFER_UPPER_LIMIT + cba)):
            category = handicapToCategory(handicap + adjustment)
            single = category / 10
            if category == 6:
                single = 1
            adjustment -= single
        return adjustment
    
    # your HCI can't decrease in cat 6
    if category == 6:
        return 0

    lower = catToLowerBuffer(is9Hole, category)
    if stablefordScore < lower + cba:
        # cannot go back to cat 6
        for _ in range(stablefordScore - lower):
            if handicapToCategory(handicap + adjustment) == 6:
                if adjustment > 0 :
                    return adjustment - BELOW_BUFFER_ADD
                return adjustment
            adjustment += BELOW_BUFFER_ADD

    
    return adjustment
