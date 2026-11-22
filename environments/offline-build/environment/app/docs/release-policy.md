# Dependency resolution: the March incident and current practice

In March, a release workstation resolved a look-alike package from a
public index and shipped it in a ledgerkit build. The package was one
of ours in name only. The build went out before anyone noticed, and
the release had to be recalled and rebuilt from a clean tree.

Since that rebuild, ledgerkit releases have been assembled from the
vendored tree. A dependency that ships in a release is copied into
`vendor/`, reviewed there, and committed like any other file in the
tree, and the entries in `build/requirements.txt` for a release are
the ones marked `vendored`. That is the whole of the current
practice: if it ships, it was vendored and reviewed first.

The local package index in `build/index/` is a development mirror. It
is maintained so development builds and experiments can resolve
packages quickly on machines without network access, and the
development workflow (see `scripts/bootstrap.sh`) still resolves
decimalx-ext from it.
