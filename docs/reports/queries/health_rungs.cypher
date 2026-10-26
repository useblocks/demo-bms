// Program Health — the population of each rung of the V.
//
// The `type` counts are the whole graph; the template orders them by the
// V-model rather than by size, so the funnel reads top-down.
MATCH (n)
RETURN n.type AS type, count(*) AS n
ORDER BY n DESC, type
