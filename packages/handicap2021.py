def handicap(games: list[dict], courses: list[dict]) -> list[float]:
    """calculates the handicap given 0 to 20 games with the gross, net and stable ford value. 
    Also needs the course on which the game was played to work properly
    Returns a list with 3 elements, where the first is the gross, the second is the net and
    the third the stableford value"""

    if not (len(games) <= 20):
        raise ValueError(f"Invalid parameter: len(games) = {len(games)}. You can only add a max of 20 games.")

    handicap = [54, 54, 54]  
    numHoles = 0
    for game in games:
        numHoles += len[game["shots"]] #shots is the array that tracks the amount of shots per hole
    numGames = len(games)

    if numHoles < 54:
        return handicap

    functions = [handicapDifferential, handicapDifferentialNet, handicapDifferentialStableford]

    for i , func in enumerate(functions):
        differentials = []
        for game in games:
            course = [course for course in courses if course["courseID"] == game["courseID"]]
            value: float = func(game, course[0])
            differentials.append(value)
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


def handicapDifferential() -> float:
    """calculates the handicap differential for one game"""
    print("a")


def handicapDifferentialNet() -> float:
    """calculates the handicap differential for one game using net shots"""
    print("a")


def handicapDifferentialStableford() -> float:
    """calculates the handicap differential for one game using the Stableford system"""
    print("a")


#highest priority at the top
#TODO fill out the differential functions
#TODO build packages
#TODO create ui