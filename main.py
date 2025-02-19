from datetime import datetime
from tinydb import Query, TinyDB
from packages.helper  import Helper
import os

# Define the database directory and file path
db_dir = "./db" #should maybe be changed to %APPDATA%
db_path = os.path.join(db_dir, "db.json")

# Ensure the directory exists
os.makedirs(db_dir, exist_ok=True)

# Initialize the database
db = TinyDB(db_path)

# Initialize tables
games = db.table("games", cache_size=20) # stores the games that were already calculated
courses = db.table("courses") # stores the courses
cron = db.table("cron", cache_size=0) # stores a reference to the games that are not in the calculation yet
hcLog = db.table("hcLog", cache_size=366) # stores the old HCs max one per day

# creating instance of Helper and setting default tables
help = Helper(games, courses, cron, hcLog)

# implements 5.4
def HCCron() -> None:
    """
    cron job that should be run on launch/once per day
    """
    Game = Query()
    ids = cron.all()
    docs = games.search(Game.game_id.one_of(ids))
    
    today = datetime.now()
    for doc in docs:
        docDate = datetime.fromisoformat(doc["date"])
        if (today - docDate).days >= 1:
            help.updateHandicapIndex(doc, datetime.fromisoformat(doc["date"]))