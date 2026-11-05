// Test Coverage — every system requirement, seen from the END of its chain:
// req <- satisfies - arch <- refines - swreq <- verifies - test <- results_for - test_result
//
// `swreqs` counts the software requirements below the requirement and
// `swreqs_tested` the ones with at least one test, so `swreqs_tested = swreqs`
// (and `swreqs > 0`) means the requirement is covered by tests all the way down.
// `results` and `failed` count the recorded runs of those tests. DISTINCT keeps a
// software requirement reached through two architecture elements from counting
// twice.
MATCH (r:req)
OPTIONAL MATCH (r)<-[:satisfies]-(:arch)<-[:refines]-(s:swreq)
WITH DISTINCT r, s
OPTIONAL MATCH (s)<-[:verifies]-(t:test)
OPTIONAL MATCH (t)<-[:results_for]-(tr:test_result)
WITH r, s, count(DISTINCT t) AS s_tests, count(tr) AS s_runs,
     sum(CASE WHEN tr.result <> 'passed' THEN 1 ELSE 0 END) AS s_failed
RETURN r.id AS id, r.title AS title, coalesce(r.asil, '') AS asil,
       count(s) AS swreqs,
       sum(CASE WHEN s_tests > 0 THEN 1 ELSE 0 END) AS swreqs_tested,
       sum(s_tests) AS tests, sum(s_runs) AS results, sum(s_failed) AS failed
ORDER BY id
