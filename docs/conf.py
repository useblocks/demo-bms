"""Sphinx configuration — the ubTrace export of this project.

This repository has TWO consumers of the same sources:

* ``ubc`` (the ubCode CLI and the IDE extension) parses ``specs/**/*.rst`` plus
  the one-line codelinks markers in ``src/`` and ``tests/`` and compiles them
  into ``needs.json``;
* ``sphinx-build -b ubtrace`` (this file) parses the SAME sources and compiles
  them into the ubTrace artefact that ``upload_ubtrace.sh`` ships to
  team.useblocks.com.

Neither one owns the ontology: the need types, the link types and the extra
options are declared exactly once, in ``ubproject.toml``, and both sides read
them from there — ``needs_from_toml`` for the needs, ``src_trace_config_from_toml``
for the code markers. Changing a type in ``ubproject.toml`` therefore changes
both consumers, and there is no second copy of the data model to keep in sync.

This directory, ``docs/``, is the Sphinx source directory AND the ubCode project
root (``ubproject.toml`` is here). The code it traces lives beside it, in
``../src`` and ``../tests``, and finds its way back to this configuration through
``../src/ubproject.redirect.toml`` and ``../tests/ubproject.redirect.toml``.
Build from the repository root, with the
``ubtrace`` extra (see ../pyproject.toml)::

    uv run --extra ubtrace sphinx-build -b ubtrace docs _build/ubtrace
    UBTRACE_INGEST_TOKEN=<token> bash upload_ubtrace.sh

``uv run --extra ubtrace sphinx-build -b html docs _build/html`` renders the same
sources as an ordinary site, which is the faster loop while editing.
"""

import os
import shutil

# -- Project information --------------------------------------------------------

project = "BMS — Battery Management System"
copyright = "2026, useblocks GmbH"
author = "useblocks GmbH"
version = "0.1.0"

# -- General configuration ------------------------------------------------------

extensions = [
    "myst_parser",  # the Markdown-authored stream, specs/isolation-monitoring/
    "sphinx_needs",
    "sphinx_codelinks",  # materialises the one-line markers in src/ and tests/
    "sphinxcontrib.mermaid",  # the `.. mermaid::` component diagrams
    "ubt_sphinx",  # the `ubtrace` builder
]

# Sphinx builds every `.rst` and `.md` file it finds under the source directory,
# whether or not it is in a toctree. Because the source directory is docs/ and
# nothing but documentation lives here, the list is the Sphinx default plus the
# build output and ubc's cache — no virtualenv, no worktrees, no host directories
# to keep excluding by name as the repository grows.
exclude_patterns = [
    "_build",
    "reports/_build",  # `ubc report` output; the templates and snapshots beside it are not pages
    ".ub_cache",
    "Thumbs.db",
    ".DS_Store",
]

# -- sphinx-needs / sphinx-codelinks -------------------------------------------
# Both read their structural configuration out of ubproject.toml, so ubCode and
# Sphinx agree on the data model by construction. Do not re-declare need types,
# links or extra options here — declare them in ubproject.toml.
needs_from_toml = "ubproject.toml"
src_trace_config_from_toml = "ubproject.toml"

# Presentation only: the link type is obvious from the ontology, so the tables
# stay readable without repeating it in every cell.
needs_show_link_type = False
needs_show_link_title = False

# NOTE: do NOT set `needs_json_remove_defaults = True` here.
#
# It looks like the right fix for the Elasticsearch problem described in
# tools/import_test_results.py (the run label written as "" on every need that
# has no test run), and it does close that hole — but it opens a worse one.
# ubt-coverage discovers custom link types PER NEED, by looking for a
# `<name>_back` key on the same need whose outgoing links it is counting
# (`discover_custom_link_bases` in rust/ubt-coverage/src/needs.rs). Removing
# defaults strips the empty `affects_back: []` from a `decision`, the empty
# `mitigates_back` from a `risk` and so on — so their outgoing custom links
# become invisible to the coverage engine.
#
# Measured with ubt-coverage against this project's own artefact:
#
#   remove_defaults OFF: 206 edges, orphan_both = 0 for every type
#   remove_defaults ON : 123 edges, orphan_both = 5 decisions, 5 risks,
#                        50 test_results, 1 req
#
# The 83 lost edges are exactly the custom outgoing ones (19 traces_to,
# 50 results_for, 7 affects, 7 mitigates). The graph/tree stays correct either
# way — the relations extractor discovers link types corpus-wide — but the
# coverage engine reports most of the project as orphaned.
#
# So the empty string is dealt with at the source instead: the run label is
# formatted so Elasticsearch never types the field as a date. See
# `_run_label` in tools/import_test_results.py.

# NO `suppress_warnings`, AND THAT IS THE POINT — `-W --keep-going` gates this build,
# so every warning must be fixed at its source rather than hidden. Two entries used to
# live here and both were removed by fixing the cause:
#
#   `needs.deprecated` — sphinx-needs mapped `[[needs.extra_options]]` onto its own
#   deprecated `needs_extra_options`. ubproject.toml now declares those nine fields as
#   `[needs.fields.<name>]`, so nothing deprecated is reached.
#
#   `sn_schema_warning.network_contains_too_few` — emitted by five `coverage-*-back`
#   rules in schemas.json that duplicated the five `direction = "both"` trace edges.
#   Backward coverage is `ubc agent gaps`'s job, so the rules were deleted and this
#   entry went with them.
#
# Before adding an entry here, check whether the warning has a source you can remove
# instead. A suppression that hides a real finding from `-W` also hides it from every
# reader of the export.

# -- Mermaid --------------------------------------------------------------------
# The default "raw" output emits a <div> that the browser renders with
# mermaid.js. Scripts do NOT run in the ubTrace export, so a raw diagram is
# blank there. When the mermaid CLI (`mmdc`, from @mermaid-js/mermaid-cli) is on
# PATH, pre-render to SVG instead so the diagrams survive the export; without it
# the build still succeeds and only the three component diagrams degrade.
mermaid_output_format = "svg" if shutil.which("mmdc") else "raw"

# `mmdc` drives a headless Chromium through puppeteer, whose sandbox needs
# unprivileged user namespaces. Ubuntu 23.10+ (so ubuntu-latest on GitHub
# Actions) restricts those via AppArmor, and Chromium then aborts with "No
# usable sandbox!" — three failed renders, three warnings, and under `-W` a
# failed publish. mermaid-puppeteer.json passes `--no-sandbox` to make the
# render work in that environment; the only content it renders is the three
# diagrams in this repository's own sources.
mermaid_params = [
    "-p",
    os.path.join(os.path.dirname(__file__), "mermaid-puppeteer.json"),
]

# -- Diagrams -------------------------------------------------------------------
# `traceability.rst` renders the per-stream chains as `needflow` diagrams
# through graphviz (`flow_engine` in ubproject.toml). Without `dot` on PATH
# sphinx-needs cannot produce them, so fail here with something readable
# instead of at the first directive.
if shutil.which("dot") is None:
    raise RuntimeError(
        "graphviz 'dot' executable not found on PATH. The needflow diagrams on "
        "traceability.rst are rendered with it (see flow_engine in "
        "ubproject.toml). Install graphviz (macOS: 'brew install graphviz', "
        "Debian/Ubuntu: 'apt-get install graphviz') and retry."
    )

# -- HTML -----------------------------------------------------------------------
html_theme = "furo"
html_title = "BMS"
# The ubTrace builder warns (fatal under -W) when logo/favicon are unset; the
# same minimal battery mark serves as both.
html_logo = "_static/bms-logo.svg"
html_favicon = "_static/bms-logo.svg"

# -- ubTrace export -------------------------------------------------------------
# ubt_sphinx writes its output into the ingest layout
#   _build/ubtrace/<organization>/<project>/<version>/
# and `upload_ubtrace.sh` DISCOVERS that path rather than re-declaring it, so
# these three values are the single source for where the artefact is published;
# changing one here is enough. `ubtrace_version` is overridden per build in CI
# (`-D ubtrace_version=<tag>`), which is how a release tag publishes as its own
# version alongside `main`.
ubtrace_organization = "useblocks-rollout"
ubtrace_project = "rollout-demo-bms"
ubtrace_version = "main"

ubtrace_theme_options = {
    "repo_url": "https://github.com/useblocks/rollout-demo-bms",
    # The sources sit one level down from the repository root.
    "edit_uri": "edit/main/docs/",
    "view_source_uri": "blob/main/docs/",
    "logo": {
        "desktop": "_static/bms-logo.svg",
        "mobile": "_static/bms-logo.svg",
    },
}
