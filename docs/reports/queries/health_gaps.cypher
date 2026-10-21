// Program Health — the structural gaps the last `ubc agent gaps` run found.
//
// A gap is a missing rung, not a failing test: it is imported as a `gap` need
// by `tools/import_gaps.py` from the committed snapshot. The template links
// the gap to the need it is attributed to.
MATCH (g:gap)
RETURN g.id AS id, g.gap_category AS category, g.gap_need_id AS need_id,
       g.gap_need_type AS need_type, g.gap_link AS link, g.gap_shortfall AS shortfall
ORDER BY need_id
