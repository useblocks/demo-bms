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

Build it with the ``ubtrace`` extra (see pyproject.toml)::

    uv run --extra ubtrace sphinx-build -b ubtrace . _build/ubtrace
    UBTRACE_INGEST_TOKEN=<token> bash upload_ubtrace.sh

``uv run --extra ubtrace sphinx-build -b html . _build/html`` renders the same
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
    "sphinx_needs",
    "sphinx_codelinks",  # materialises the one-line markers in src/ and tests/
    "sphinxcontrib.mermaid",  # the `.. mermaid::` component diagrams
    "ubt_sphinx",  # the `ubtrace` builder
]

# Sphinx builds every `.rst` file it finds under the source directory (this
# repository root), whether or not it is in a toctree. Everything below is
# either build output, a virtualenv, or a cache — never a source.
exclude_patterns = [
    "_build",
    ".venv",
    ".ub_cache",
    ".pytest_cache",
    ".git",
    ".github",
    ".agents",
    ".pharaoh",
    "reports/_build",
    "README.md",
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

# sphinx-needs reads `[[needs.extra_options]]` out of ubproject.toml and maps it
# onto its own deprecated `needs_extra_options` config, so IT emits the
# deprecation — nothing in this repository sets that option. Suppressing it here
# is what keeps `-W` usable as a real gate on NEW warnings; drop this once
# ubCode accepts the `[[needs.fields]]` spelling, so both sides can move
# together.
suppress_warnings = ["needs.deprecated"]

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
    "edit_uri": "edit/main/",
    "view_source_uri": "blob/main/",
    "logo": {
        "desktop": "_static/bms-logo.svg",
        "mobile": "_static/bms-logo.svg",
    },
}
