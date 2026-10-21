// Verification Cockpit — where the software requirement sits in the V.
//
// The architecture element it refines, the requirements that element
// satisfies, and the user story those requirements serve. One row per
// (arch, req, story); an architecture element may satisfy several
// requirements, so the template folds them into one breadcrumb and takes the
// worst ASIL as the requirement's own safety level.
MATCH (c:swreq {id: $current_id})-[:refines]->(a:arch)-[:satisfies]->(r:req)
OPTIONAL MATCH (r)-[:traces_to]->(u:user_story)
RETURN a.id AS arch, a.title AS arch_title,
       r.id AS req, r.title AS req_title, coalesce(r.asil, '') AS asil,
       coalesce(u.id, '') AS story, coalesce(u.title, '') AS story_title
ORDER BY r.id
