// Program Health — the variant the index was built for.
//
// `chemistry` is a variant field, resolved from the `variant_data_file` the
// build ran with (`variants/nmc.json` by default, `variants/lfp.json` for the
// alternative). The requirement that carries it is the one whose rendered cell
// voltage window changes between the two profiles, so this is the one place
// the page shows which 150 % slice it is reporting on.
MATCH (r:req)
WHERE r.chemistry <> ''
RETURN r.id AS id, r.chemistry AS chemistry
ORDER BY id
