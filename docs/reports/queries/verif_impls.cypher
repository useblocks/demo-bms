// Verification Cockpit — the implementations that realise the software
// requirement in focus.
//
// `local-url` is the source location codelinks attached to the materialised
// impl need (file URL + line). It is empty for a marker that carried none,
// which the template renders as plain text instead of a dead link.
MATCH (c:swreq {id: $current_id})<-[:implements]-(i:impl)
RETURN i.id AS id, i.title AS title, coalesce(i.`local-url`, '') AS url
ORDER BY id
