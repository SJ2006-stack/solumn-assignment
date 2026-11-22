# Finish the catalog backfill

The catalog API is local. The client, the backoff helper, and
`python -m sync.cli serve` already speak the protocol in `docs/api.md`.

`sync.pager.collect` and `sync.cache.PageCache` are unfinished, so
`python -m sync.cli run` cannot write the catalog. The morning load is
waiting on this file: it reads the catalog once, first thing, and there is
no second run before the day's orders open — a catalog that is not there
in time is a day running on yesterday's items.

Finish paging and the cache so the command writes `/app/out/items.json`
containing every item id from 1 through `item_count`, in order, each with
its `name`.

How the service behaves — paging, transient responses, and the limits it
runs under — is described in `docs/api.md` and `fixtures/quota.json`.
Use those; they are the contract this tenant's API runs on.

`python -m sync.cli serve` binds `base_url` for a local try. The grader
runs its own server on that same URL.
