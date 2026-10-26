// Safety Case — the risks that mitigate the requirement in focus.
//
// A risk register entry is written in four sections (Cause / Effect /
// Mitigation / Residual) separated by blank lines. They are extracted here
// rather than in the template because `content` is Markdown text and Cypher
// can split it on those blank lines, where the template engine has no string
// filter for it. `coalesce` turns an absent section into "" so the template
// never has to guard a null.
MATCH (k:risk)-[:mitigates]->(c:req {id: $current_id})
WITH k, split(k.content, '\n\n') AS parts
RETURN k.id AS id, k.title AS title,
       coalesce(head([p IN parts WHERE p STARTS WITH '**Cause**']), '') AS cause,
       coalesce(head([p IN parts WHERE p STARTS WITH '**Effect**']), '') AS effect,
       coalesce(head([p IN parts WHERE p STARTS WITH '**Mitigation**']), '') AS mitigation,
       coalesce(head([p IN parts WHERE p STARTS WITH '**Residual**']), '') AS residual
ORDER BY id
