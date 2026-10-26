// Verification Cockpit — the sibling software requirements of the same
// architecture element, with their closure state.
//
// A verification lead should see the component's whole obligation, not only
// the requirement in focus: one unclosed sibling is the difference between a
// component that is done and one that only looks done from this page. `impls`
// and `tests` count the links, `results` counts recorded runs under them, and
// `failing` counts the non-passing ones.
MATCH (c:swreq {id: $current_id})-[:refines]->(a:arch)<-[:refines]-(sib:swreq)
RETURN a.id AS arch, sib.id AS swreq, sib.title AS title,
       COUNT { (sib)<-[:implements]-() } AS impls,
       COUNT { (sib)<-[:verifies]-() } AS tests,
       COUNT { (sib)<-[:verifies]-()<-[:results_for]-() } AS results,
       COUNT { (sib)<-[:verifies]-()<-[:results_for]-(tr) WHERE tr.result <> 'passed' } AS failing
ORDER BY swreq
