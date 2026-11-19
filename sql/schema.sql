
CREATE TABLE IF NOT EXISTS mobility (

    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    od_id TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,

    year INTEGER NOT NULL
        CHECK (year BETWEEN 2014 AND 2023),

    count BIGINT NOT NULL
        CHECK (count > 0),

    origin_country VARCHAR(2)
        GENERATED ALWAYS AS (LEFT(origin, 2)) STORED,

    dest_country VARCHAR(2)
        GENERATED ALWAYS AS (LEFT(destination, 2)) STORED,

    same_region BOOLEAN
        GENERATED ALWAYS AS (origin = destination) STORED,

    same_country BOOLEAN
        GENERATED ALWAYS AS (
            LEFT(origin, 2) = LEFT(destination, 2)
        ) STORED,

    CONSTRAINT unique_mobility_route
        UNIQUE (origin, destination, year),

    CONSTRAINT valid_region_codes
        CHECK (
            LENGTH(origin) >= 2
            AND LENGTH(destination) >= 2
        ),

    CONSTRAINT valid_od_id
        CHECK (od_id = origin || '_' || destination)
);
