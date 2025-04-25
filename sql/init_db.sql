DROP TABLE IF EXISTS boxers;
CREATE TABLE boxers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    weight INTEGER NOT NULL CHECK(weight >= 125),
    height INTEGER NOT NULL CHECK(height > 0),
    reach INTEGER NOT NULL CHECK(reach > 0),
    age INTEGER NOT NULL CHECK(18 <= age <= 40),
    UNIQUE(name)
);

