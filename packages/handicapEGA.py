import math
import mauerDB

BUFFER_UPPER_LIMIT = 36
BELOW_BUFFER_ADD = 0.1
BUFFER_LOWER_LIMIT_9HOLE = [None, 35, 35, 34, 33, None]


def initialHandicap(sblfd_score: int, nineHole: bool) -> float:
    """
    Calculates handicap for a player based on their score and whether they played a nine-hole game.

    Args:
        sblfd_score (int): The player's Stableford score.
        nineHole (bool): True if the game was a nine-hole game, False otherwise.

    Returns:
        float: The handicap after the first game played.
    """
    if nineHole:
        sblfd_score += 18
    return 54 - (sblfd_score - 36)

def calculateNewHandicap(game: dict, cba: int, previousHandicap: float, mauer: mauerDB.MauerDB) -> float:
    """
    Calculate the new handicap based on the game results, course conditions, and previous handicap.
    
    Args:
        game (dict): A dictionary containing game details, including shots taken.
        cba (int): The Competition Buffer Adjustment (CBA) value.
        previousHandicap (float): The player's previous handicap.
    Returns:
        float: The new calculated handicap.
    """
    # applied in specific order! NEED HANDICAP STROKE INDEX
    # error for 9 hole with cat 1?
    
    course = mauer.getCourses([game])[0]
    stableford = 0
    nineHole = len(game.shots) is 9
    handicapStrokes = playingHandicap(nineHole, previousHandicap, course.course_rating, course.slope_rating, sum(course.par))
    
    for i in range(course.strokeIndex): #TODO: course entry needs stroke index
        if i+1 < handicapStrokes:
            pass
        course.par[course.strokeIndex[i]] += 1 + handicapStrokes // (9*(nineHole+1) + i+1) # absolutely bonkers math going on here
    
    # convert to stableford
    for i in range(game.shots):
        stableford += max(0, 2 - (game.shots[i] - course.par[i]))
    
    # if 9-hole, add 18 points, to be RECORDED
    if nineHole:
        stableford += 18

    adjustment = calculateAdjustment(stableford, previousHandicap, cba)

    return previousHandicap + adjustment

def roundHalfUp(n, decimals=0) -> float:
    """
    Rounds a number to a specified number of decimal places using the "round half up" strategy.
    
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
    
    # category 1-5
    if hciToCategory(handicap) < 6:
        raw = handicap * (slopeRating / 113) + (courseRating - par)
    # category 6
    else:
        raw = handicap + playingHandicapDifferential() #TODO
    
    return int(roundHalfUp(raw))

def playingHandicap9(handicap: float, courseRating: float, slopeRating: float, par: int) -> int:
    """
    Calculate the playing handicap for an 9-hole round of golf.
    
    Args:
        handicap (float): The player's handicap index.
        courseRating (float): The course rating, which represents the difficulty of a course for a scratch golfer.
        slopeRating (float): The slope rating, which represents the relative difficulty of a course for a bogey golfer compared to a scratch golfer.
        par (int): The par for the course.
        
    Returns:
        int: The calculated playing handicap, rounded to the nearest integer.
    """
    cat = hciToCategory(handicap)
    if cat > 1 and cat < 6:
        raw = (handicap * (slopeRating / 113)) / 2 + (courseRating - par)
    if cat is 6:
        raw = handicap / 2 + playingHandicapDifferential(true) #TODO
    
    return int(roundHalfUp(raw))

def playingHandicap(is9Hole: bool, handicap: float, courseRating: float, slopeRating: float, par: int) -> int:
    """
    Calculate the playing handicap for a golfer based on whether they are playing a 9-hole or 18-hole course.
    
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

def hciToCategory(handicap: float) -> int:
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
        return BUFFER_LOWER_LIMIT_9HOLE[category] # is there a better solution?
    return BUFFER_UPPER_LIMIT - category

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
        base = playingHandicap9(36.0, courseRating, slopeRating, par)
    else:
        base = playingHandicap18(36.0, courseRating, slopeRating, par)
    
    return base - 36.0

def calculateAdjustment(stablefordScore: int, handicap: float, cba: int) -> float:
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
    if hciToCategory(handicap) is 6:
        cba = 0 # cba does not apply to cat 6

    if stablefordScore > BUFFER_UPPER_LIMIT + cba:
        for _ in range(stablefordScore - (BUFFER_UPPER_LIMIT + cba)):
            cat = hciToCategory(handicap + adjustment)
            single = cat / 10
            if cat is 6:
                single = 1
            adjustment -= single
        return adjustment

    lower = catToLowerBuffer(cat)
    if stablefordScore < lower + cba:
        # only until cat 6, but not as granular as above
        if hciToCategory(handicap + adjustment) is 6:
            if adjustment > 0 :
                return adjustment - BELOW_BUFFER_ADD
            return 0.0
        for _ in range(stablefordScore - lower):
            adjustment += BELOW_BUFFER_ADD    

    return adjustment