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
hcLog = db.table("hcLog", cache_size=366) # stores the old HCs max one per day

# creating instance of Helper and setting default tables
help = Helper(games, courses, hcLog)
            