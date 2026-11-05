// Traceability Coverage — the recorded test evidence reaching every system
// requirement.
//
// A result counts towards a requirement when the chain
// req <- satisfies - arch <- refines - swreq <- verifies - test <- results_for - test_result
// connects them. DISTINCT counts each result once per requirement, however many
// archs or swreqs it reaches it through. A requirement with no chain, and one
// whose tests have no recorded run, both come back with zero results; only the
// structural gaps tell them apart.
MATCH (r:req)
OPTIONAL MATCH (r)<-[:satisfies]-(:arch)<-[:refines]-(:swreq)<-[:verifies]-(:test)<-[:results_for]-(tr:test_result)
WITH DISTINCT r, tr
ORDER BY r.id, tr.id
RETURN r.id AS id, r.title AS title, r.status AS status,
       sum(CASE WHEN tr.result = 'passed' THEN 1 ELSE 0 END) AS passed,
       sum(CASE WHEN tr IS NOT NULL AND tr.result <> 'passed' THEN 1 ELSE 0 END) AS failed,
       collect(CASE WHEN tr.result <> 'passed' THEN tr.id END) AS failing_ids
ORDER BY id
