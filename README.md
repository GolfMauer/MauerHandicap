# Project MAUER
Firstly it is important to establish that no one has the intent of building a wall.
But for the security of our grades a great great wall has to be build.

## Structure
To ensure efficient progress on our MAUER the folders are structured as follows
│
├── test (Data for Testing the functionality of the mauer; maybe also tests if it makes sense to separate them)
│   ├── courses (Test courses Dir)
│   └── games (Test games Dir)
├── db (PROD DB location)
│   └── db.json
├── main.py (Main/Init file)
├── packages (packages used for calculation)
│   ├── handicapEGA.py (pre 2021 handicap)
│   ├── handicapWHS.py (post 2021 handicap)
│   ├── mauerDB.py (modified version of TinyDB)
│   ├── test_handicapWHS.py
│   └── test_mauerDB.py
└── README.md

## Current Software architecture design
At the center of our application sits the great great MauerDB. Which will be split into 4 Tables:
- games: stores the games that were already calculated
- courses: stores the courses
- cron: stores the games that are not in the calculation yet; could potentially be merged with games
- hcLog: stores the old HCs max one per day

To create a good user experience of the MAUER PyQt is used to design the UI (#TODO @rocco @simon @Jack)

The application will be tied together by the handicap packages (potential merge through MauerDB as it often makes sense to calculate both when reading/writing data) and the MauerDB package, which allows the frontend to store data which will then be calculated stored (on the next day for WHS). The main.py will be called on each start and will do the initial setup of the db and trigger the corn job for WHS

Note: The handicap packages should be merged so that the frontend only interacts with the db and the db only with the packages (Model-View-Controller I think)
Note: It may be useful to create a init.py for installation of the Mauer as application that is recognized by windows

# TODO
- add tests
- create accurate test games
- consider multiple players
- consider not all holes played
- build packages
- create ui
- Soft- / Hardcap on handicap increase.
- Research on how Python applications are created
