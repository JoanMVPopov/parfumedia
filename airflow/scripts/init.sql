-- init.sql: Ensure required tables exist

-- Table for Backlog model
CREATE TABLE IF NOT EXISTS etl_backlog (
    id SERIAL PRIMARY KEY,
    link TEXT NOT NULL,
    attempts INTEGER DEFAULT 0
);

-- Table for Perfume model
CREATE TABLE IF NOT EXISTS etl_perfume (
    id SERIAL PRIMARY KEY,
    link TEXT NOT NULL,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255) NOT NULL,
    rel_year INTEGER NOT NULL,
    rel_decade INTEGER NOT NULL,
    notes TEXT[] DEFAULT '{}',  -- Array field for notes
    chart_categories TEXT[] DEFAULT '{}',  -- Array field for chart_categories
    chart_numbers INTEGER[] DEFAULT '{}',  -- Array field for chart_numbers
    scent FLOAT NOT NULL,
    longevity FLOAT NOT NULL,
    sillage FLOAT NOT NULL,
    bottle FLOAT NOT NULL,
    value_for_money FLOAT NOT NULL
);