CREATE DATABASE IF NOT EXISTS flightradarbot;
USE flightradarbot;

CREATE TABLE IF NOT EXISTS users(
    id BIGINT PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT,
    radius INT,
    min_altitude INT,
    max_altitude INT
);

CREATE TABLE IF NOT EXISTS flights (
    user_id BIGINT,
    flight_id VARCHAR(8),
    timestamp FLOAT NOT NULL,
    PRIMARY KEY (user_id, flight_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);