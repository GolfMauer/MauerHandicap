import datetime
from packages.mauerDB  import MauerDB
import os

# Define the database directory and file path
db_dir = "./db"
db_path = os.path.join(db_dir, "database.json")

# Ensure the directory exists
os.makedirs(db_dir, exist_ok=True)

# Initialize the database
db = MauerDB(db_path)

# Initialize tables
gamesTable = db.table("games") # stores the games that were already calculated
courseTable = db.table("courses") # stores the courses
cronTable = db.table("cron") # stores the games that are not in the calculation yet TODO maybe inconvenient to have games split for browsing
hcLogTable = db.table("hcLog") # stores the old HCs max one per day

# Insert base Handicap
if len(hcLogTable) == 0:
    gamesTable.insert({"ega": 54, "whs": 54, "date": datetime.datetime.now().isoformat()})