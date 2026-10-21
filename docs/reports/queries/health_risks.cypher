// Program Health — every risk and how many requirements it mitigates.
//
// A risk with zero is a register entry that names no requirement: an
// unmitigated hazard as far as the graph can tell, and a release blocker for a
// safety-relevant program.
MATCH (k:risk)
RETURN k.id AS id, k.title AS title,
       COUNT { (k)-[:mitigates]->() } AS mitigations
ORDER BY mitigations, id
