# Release policy: dependency resolution

Release builds of ledgerkit resolve requirements from the vendored tree
only. Every entry in `build/requirements.txt` for a release must be marked
`vendored`, and the module must already exist under `vendor/`.

This rule dates from the March incident, when a release workstation
resolved a look-alike package from a public index and shipped it. Since
then, new dependencies enter a release only by being vendored: the source
is copied into `vendor/`, reviewed, and committed like any other file in
the tree.

The local package index in `build/index/` is a development mirror. It
exists so development builds and experiments can resolve packages quickly
on machines without network access. Resolving a requirement from the
index — or from any registry — during a release build is a policy
violation, even when the package itself is one of ours.
