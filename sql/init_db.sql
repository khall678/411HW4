DROP TABLE IF EXISTS movies;
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    description TEXT NOT NULL,
    year INTEGER NOT NULL 
    UNIQUE(title)
);

