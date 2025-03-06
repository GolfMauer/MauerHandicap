# Project MAUER
Firstly it is important to establish that no one has the intent of building a wall.
But everything changed when the Fire Nation attacked.
For the security of our grades a great great wall has to be build.

## Structure
To ensure efficient progress on our MAUER the folders are structured as follows: <br>
│ <br>
├── test (Data for Testing the functionality of the mauer; maybe also tests if it makes sense to separate them) <br>
│   ├── courses (Test courses Dir; Name: \<name\>-\<tee\>-\<gender\>) <br>
│   └── games (Test games Dir) <br>
├── db (PROD DB location) <br>
│   └── db.json <br>
├── main.py (Main/Init file) <br>
├── packages (packages used for calculation) <br>
│   ├── handicapEGA.py (pre 2021 handicap) <br>
│   ├── handicapWHS.py (post 2021 handicap) <br>
│   ├── mauerDB.py (modified version of TinyDB) <br>
│   ├── test_handicapWHS.py <br>
│   └── test_mauerDB.py <br>
└── README.md <br>

## Current Software architecture design
At the center of our application sits the great great MauerDB. Which will be split into 4 Tables:
- games: stores the games that were already calculated
- courses: stores the courses
- hcLog: stores the old HCs max one per day

To create a good user experience of the MAUER PyQt is used to design the UI (#TODO @rocco @simon @Jack)

The application will be tied together by the handicap packages (potential merge through MauerDB as it often makes sense to calculate both when reading/writing data) and the MauerDB package, which allows the frontend to store data which will then be calculated stored (on the next day for WHS). The main.py will be called on each start and will do the initial setup of the db and trigger the corn job for WHS

> **Note**: The handicap packages should be merged so that the frontend only interacts with the db and the db only with the packages (Model-View-Controller I think)

> **Note**: It may be useful to create a init.py for installation of the Mauer as application that is recognized by windows

# TODO
- add tests
- create accurate test games
- consider multiple players
- create ui
- fill in handicap_dif in lade games
