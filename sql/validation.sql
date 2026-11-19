
-- Database validation

SELECT
    COUNT(*) AS total_records,
    SUM(count) AS total_mobility,

    COUNT(*) FILTER (
        WHERE same_country = FALSE
    ) AS international_records,

    SUM(count) FILTER (
        WHERE same_country = FALSE
    ) AS international_mobility

FROM mobility;


-- Validate annual aggregation

WITH annual AS (
    SELECT
        year,
        SUM(count) AS mobility_count
    FROM mobility
    WHERE same_country = FALSE
    GROUP BY year
)

SELECT
    COUNT(*) AS number_of_years,
    SUM(mobility_count) AS total_mobility
FROM annual;


-- Validate bilateral aggregation

WITH bilateral AS (
    SELECT
        origin_country,
        dest_country,
        SUM(count) AS mobility_count
    FROM mobility
    WHERE same_country = FALSE
    GROUP BY origin_country, dest_country
)

SELECT
    COUNT(*) AS directional_connections,
    SUM(mobility_count) AS total_mobility
FROM bilateral;
