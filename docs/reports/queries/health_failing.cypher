// Program Health — the recorded outcomes that are not `passed`, with the whole
// chain each one reaches.
//
// This is the release-blocking half of the evidence: every structural gate can
// be green while these say the system does not do what a requirement says.
// The chain is test -> swreq -> arch -> req -> user_story, so the reader sees
// how far up the V one failing operator reaches.
MATCH (tr:testcase)-[:results_for]->(t:test)-[:verifies]->(s:swreq)
      -[:refines]->(a:arch)-[:satisfies]->(r:req)-[:traces_to]->(u:user_story)
WHERE tr.result <> 'passed'
RETURN tr.id AS result, tr.result AS outcome,
       t.id AS test, s.id AS swreq, a.id AS arch, r.id AS req, u.id AS story
ORDER BY result
