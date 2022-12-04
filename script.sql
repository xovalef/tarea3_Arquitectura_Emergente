CREATE TABLE admin
(
    username TEXT PRIMARY KEY,
    password TEXT
);

CREATE TABLE company(
    id INTEGER PRIMARY KEY,
    company_name TEXT,
    company_apy_key TEXT);


CREATE TABLE location
(
    id INTEGER PRIMARY KEY,
    location_name TEXT,
    location_country TEXT,
    location_city TEXT,
    location_meta TEXT
);

CREATE TABLE company_location
(
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    location_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES company(id)
    FOREIGN KEY(location_id) REFERENCES location(id)  
);

CREATE TABLE sensor
(
    id INTEGER PRIMARY KEY,
    sensor_name TEXT,
    sensor_category TEXT,
    sensor_meta TEXT,
    sensor_api_key TEXT
    
);

CREATE TABLE location_sensor
(
    id INTEGER PRIMARY KEY,
    location_id INTEGER,
    sensor_id INTEGER,
    FOREIGN KEY(location_id) REFERENCES location(id),
    FOREIGN KEY(sensor_id) REFERENCES sensor(id)
);

CREATE TABLE sensor_data
{
    id INTEGER PRIMARY KEY,
    sensor_id INTEGER,
    data TEXT,
    FOREIGN KEY(sensor_id) REFERENCES sensor(id)
};