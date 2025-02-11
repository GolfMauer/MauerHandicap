#for ui only I guess nad calls the data and handicap packages
from packages.mauerDB  import MauerDB

db = MauerDB("./db")
gamesTable = db.table("games") # stores the games that were already calculated
courseTable = db.table("courses") # stores the courses
cronTable = db.table("cron") # stores the games that are not in the calculation yet TODO maybe inconvenient to have games split for browsing
hcLogTable = db.table("hcLog") # stores the old HCs max one per day