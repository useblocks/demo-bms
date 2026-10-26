// Safety Case — the architecture decisions the requirement's design rests on.
//
// A decision `affects` an architecture element; this returns the decisions
// affecting any element that `satisfies` the requirement, with the Context and
// Consequences paragraph of each decision body. The paragraph is picked by the
// heading that precedes it, so a decision that reorders its four sections still
// resolves the right text.
MATCH (c:req {id: $current_id})<-[:satisfies]-(a:arch)<-[:affects]-(d:decision)
WITH d, collect(DISTINCT a.id) AS archs, split(d.content, '\n\n') AS parts
RETURN d.id AS id, d.title AS title, archs,
       coalesce(head([i IN range(0, size(parts) - 1) WHERE parts[i] = '**Context**' | parts[i + 1]]), '') AS context,
       coalesce(head([i IN range(0, size(parts) - 1) WHERE parts[i] = '**Consequences**' | parts[i + 1]]), '') AS consequences
ORDER BY id
