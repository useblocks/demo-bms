// Program Health — the safety integrity of every requirement and how much
// recorded evidence reaches it.
//
// `results` counts recorded test outcomes under the requirement (through
// arch -> swreq -> test -> test_result); `failing` counts the non-passing
// ones. Both are zero for a requirement with no chain, which is exactly the
// distinction the template needs: no chain and a chain with no run both show
// as zero evidence, and only the structural-gap query tells them apart.
// `rank` orders D before C before B before A before QM, and the ASIL-less
// requirements last.
MATCH (r:req)
OPTIONAL MATCH (r)<-[:satisfies]-(:arch)<-[:refines]-(:swreq)<-[:verifies]-(:test)<-[:results_for]-(tr:test_result)
WITH r, count(tr) AS results,
     sum(CASE WHEN tr IS NOT NULL AND tr.outcome <> 'passed' THEN 1 ELSE 0 END) AS failing
RETURN r.id AS id, r.title AS title, coalesce(r.asil, '') AS asil,
       results, failing,
       CASE r.asil WHEN 'D' THEN 0 WHEN 'C' THEN 1 WHEN 'B' THEN 2
                   WHEN 'A' THEN 3 ELSE 4 END AS rank
ORDER BY rank, id
