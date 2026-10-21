// Program Health — how much of the software-requirement rung is closed.
//
// A software requirement is `implemented` when at least one impl implements
// it, `verified` when at least one test verifies it, and `complete` when both
// hold. One row, so the template can read a single set of counts.
MATCH (s:swreq)
OPTIONAL MATCH (s)<-[:implements]-(i:impl)
OPTIONAL MATCH (s)<-[:verifies]-(t:test)
WITH s, count(DISTINCT i) AS impls, count(DISTINCT t) AS tests
RETURN count(s) AS total,
       sum(CASE WHEN impls > 0 THEN 1 ELSE 0 END) AS implemented,
       sum(CASE WHEN tests > 0 THEN 1 ELSE 0 END) AS verified,
       sum(CASE WHEN impls > 0 AND tests > 0 THEN 1 ELSE 0 END) AS complete
