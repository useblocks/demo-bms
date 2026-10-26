// Safety Case — the evidence chain below the requirement in focus.
//
// arch (satisfies the req) -> swreq (refines the arch) -> test (verifies the
// swreq) -> test_result (records the test's last run). The two OPTIONAL MATCHes
// keep a swreq with no test, and a test with no recorded run, in the result as
// a row with an empty id: the template draws those as holes rather than
// silently dropping the software requirement they belong to.
MATCH (c:req {id: $current_id})<-[:satisfies]-(a:arch)<-[:refines]-(s:swreq)
OPTIONAL MATCH (s)<-[:verifies]-(t:test)
OPTIONAL MATCH (t)<-[:results_for]-(tr:test_result)
RETURN a.id AS arch, a.title AS arch_title,
       s.id AS swreq, s.title AS swreq_title,
       coalesce(t.id, '') AS test, coalesce(t.title, '') AS test_title,
       CASE WHEN tr IS NULL THEN '' ELSE tr.outcome END AS outcome,
       CASE WHEN tr IS NULL THEN '' ELSE tr.id END AS result,
       CASE WHEN tr IS NULL THEN '' ELSE tr.runtime_s END AS runtime
ORDER BY a.id, s.id, test
