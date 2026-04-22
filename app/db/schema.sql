CREATE TABLE clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    short_code VARCHAR(32) NOT NULL UNIQUE,
    country VARCHAR(120),
    is_target BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    preferred_name VARCHAR(255),
    position VARCHAR(120) NOT NULL DEFAULT 'unknown',
    shirt_number INTEGER,
    nationality VARCHAR(120),
    date_of_birth DATE,
    source VARCHAR(255) NOT NULL DEFAULT 'unassigned',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs (id)
);

CREATE INDEX idx_players_club_id ON players (club_id);
CREATE INDEX idx_players_full_name ON players (full_name);

CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id VARCHAR(255) UNIQUE,
    competition VARCHAR(255),
    season VARCHAR(64),
    match_date DATETIME NOT NULL,
    home_club_id INTEGER NOT NULL,
    away_club_id INTEGER NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    venue VARCHAR(255),
    source VARCHAR(255) NOT NULL DEFAULT 'unassigned',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (home_club_id) REFERENCES clubs (id),
    FOREIGN KEY (away_club_id) REFERENCES clubs (id)
);

CREATE INDEX idx_matches_match_date ON matches (match_date);
CREATE INDEX idx_matches_home_club_id ON matches (home_club_id);
CREATE INDEX idx_matches_away_club_id ON matches (away_club_id);

CREATE TABLE stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    minutes_played INTEGER,
    goals INTEGER NOT NULL DEFAULT 0,
    assists INTEGER NOT NULL DEFAULT 0,
    yellow_cards INTEGER NOT NULL DEFAULT 0,
    red_cards INTEGER NOT NULL DEFAULT 0,
    shots INTEGER NOT NULL DEFAULT 0,
    passes_completed INTEGER NOT NULL DEFAULT 0,
    source VARCHAR(255) NOT NULL DEFAULT 'unassigned',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches (id),
    FOREIGN KEY (player_id) REFERENCES players (id),
    FOREIGN KEY (club_id) REFERENCES clubs (id),
    CONSTRAINT uq_stats_match_player UNIQUE (match_id, player_id)
);

CREATE INDEX idx_stats_match_id ON stats (match_id);
CREATE INDEX idx_stats_player_id ON stats (player_id);
CREATE INDEX idx_stats_club_id ON stats (club_id);
