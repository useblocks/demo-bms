// Safety Case — the common-cause peers of the requirement in focus.
//
// Every OTHER requirement that one of the SAME risks mitigates. If a risk
// materialises these requirements are in scope together, so they share a
// mitigation budget and a change to one is a change to the others' safety
// argument. Ordered worst ASIL first, which is how a safety review reads them:
// the `rank` column exists only to put D before C before B before A before QM,
// because the ASIL strings do not sort by severity.
MATCH (k:risk)-[:mitigates]->(c:req {id: $current_id})
MATCH (k)-[:mitigates]->(peer:req)
WHERE peer.id <> $current_id
WITH peer, collect(DISTINCT k.id) AS via
RETURN peer.id AS id, peer.title AS title, coalesce(peer.asil, '') AS asil,
       via,
       CASE peer.asil WHEN 'D' THEN 0 WHEN 'C' THEN 1 WHEN 'B' THEN 2
                      WHEN 'A' THEN 3 ELSE 4 END AS rank
ORDER BY rank, id
