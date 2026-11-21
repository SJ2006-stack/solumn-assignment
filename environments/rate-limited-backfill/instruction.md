# Finish the catalog backfill

The catalog API is local. `fixtures/quota.json` sets `base_url`, `page_size`, `item_count`, `max_requests`, and `max_in_flight`. The client, the backoff helper, and `python -m sync.cli serve` already speak the protocol in `docs/api.md`.

`sync.pager.collect` and `sync.cache.PageCache` are unfinished, so `python -m sync.cli run` cannot write the catalog.

Finish paging and the cache so the command writes `/app/out/items.json` containing every item id from 1 through `item_count`, in order, each with its `name`. Use the cache so a page that was already fetched is not requested again. Keep the run inside `max_requests` and `max_in_flight` from the quota file.

`python -m sync.cli serve` binds `base_url` for a local try. The grader runs its own server on that same URL.
