
-- 1. Annual international mobility

SELECT
    year,
    SUM(count) AS total_mobility,
    COUNT(*) AS regional_records
FROM mobility
WHERE same_country = FALSE
GROUP BY year
ORDER BY year;

-- 2. Country-level mobility balance

WITH incoming AS (
    SELECT
        dest_country AS country,
        SUM(count) AS incoming
    FROM mobility
    WHERE same_country = FALSE
    GROUP BY dest_country
),

outgoing AS (
    SELECT
        origin_country AS country,
        SUM(count) AS outgoing
    FROM mobility
    WHERE same_country = FALSE
    GROUP BY origin_country
)

SELECT
    COALESCE(i.country, o.country) AS country,
    COALESCE(i.incoming, 0) AS incoming,
    COALESCE(o.outgoing, 0) AS outgoing,
    COALESCE(i.incoming, 0)
        - COALESCE(o.outgoing, 0) AS net_mobility

FROM incoming i

FULL OUTER JOIN outgoing o
    ON i.country = o.country

ORDER BY net_mobility DESC;

-- 3. Normalized Mobility Balance Index

WITH incoming AS (
    SELECT
        dest_country AS country,
        SUM(count) AS incoming
    FROM mobility
    WHERE same_country = FALSE
    GROUP BY dest_country
),

outgoing AS (
    SELECT
        origin_country AS country,
        SUM(count) AS outgoing
    FROM mobility
    WHERE same_country = FALSE
    GROUP BY origin_country
),

balance AS (
    SELECT
        COALESCE(i.country, o.country) AS country,
        COALESCE(i.incoming, 0) AS incoming,
        COALESCE(o.outgoing, 0) AS outgoing
    FROM incoming i
    FULL OUTER JOIN outgoing o
        ON i.country = o.country
)

SELECT
    country,
    incoming,
    outgoing,
    incoming + outgoing AS total_mobility,
    incoming - outgoing AS net_mobility,

    ROUND(
        (incoming - outgoing)::NUMERIC /
        NULLIF(incoming + outgoing, 0),
        4
    ) AS nmbi

FROM balance

ORDER BY nmbi DESC NULLS LAST;

-- 4. Bilateral directional mobility flows

SELECT
    origin_country,
    dest_country,
    SUM(count) AS mobility_count

FROM mobility

WHERE same_country = FALSE

GROUP BY
    origin_country,
    dest_country

ORDER BY mobility_count DESC;
