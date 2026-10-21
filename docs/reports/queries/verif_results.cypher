// Verification Cockpit — every test that verifies the software requirement in
// focus, with the outcome of its last recorded run.
//
// A test with no recorded result keeps its row with an empty outcome, so
// "never run" is a state the cockpit can show instead of a test that silently
// disappears. `local-url` is the test source location from the codelinks
// marker.
MATCH (c:swreq {id: $current_id})<-[:verifies]-(t:test)
OPTIONAL MATCH (t)<-[:results_for]-(tr:test_result)
RETURN t.id AS test, t.title AS title,
       coalesce(t.`local-url`, '') AS url,
       CASE WHEN tr IS NULL THEN '' ELSE tr.outcome END AS outcome,
       CASE WHEN tr IS NULL THEN '' ELSE tr.runtime_s END AS runtime,
       CASE WHEN tr IS NULL THEN '' ELSE tr.id END AS result
ORDER BY t.id
