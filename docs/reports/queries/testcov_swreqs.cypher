// Test Coverage — every software requirement, with the tests that verify it and
// what their last recorded run said.
//
// Counted per TEST, not per result: a test passes when every result recorded for
// it passed, fails when any did not, and is `not_run` when it has no result at
// all. A software requirement with no verifying test comes back with tests = 0.
MATCH (s:swreq)
OPTIONAL MATCH (s)<-[:verifies]-(t:test)
OPTIONAL MATCH (t)<-[:results_for]-(tr:test_result)
WITH s, t, count(tr) AS runs, sum(CASE WHEN tr.result = 'passed' THEN 1 ELSE 0 END) AS ok
WITH s,
     count(t) AS tests,
     sum(CASE WHEN runs > 0 AND ok = runs THEN 1 ELSE 0 END) AS passed,
     sum(CASE WHEN runs > ok THEN 1 ELSE 0 END) AS failed,
     sum(CASE WHEN t IS NOT NULL AND runs = 0 THEN 1 ELSE 0 END) AS not_run,
     collect(CASE WHEN runs > ok THEN t.id END) AS failing_tests
RETURN s.id AS id, s.title AS title, tests, passed, failed, not_run, failing_tests
ORDER BY id
