# Catalog API

`GET /v1/items?cursor=` returns one page.

- An empty `cursor` starts at item 1.
- A cursor is the id of the last item already returned. The next page starts at that id plus one.
- Each page holds at most `page_size` items.
- An item is `{"id": <int>, "name": "item-NN"}` with the id zero-padded to two digits in the name.
- `next_cursor` is the last id on the page, as a string, or `null` when the page reaches `item_count`.

## Transient responses

The service is shared with other tenants and sheds load under pressure.
The first request for some pages can come back `429` instead of the
page; the same request succeeds when it is made again after a wait.
`sync/backoff.py` holds this codebase's delay contract for a 429: a
numeric `Retry-After` wins, otherwise the delay doubles from a quarter
second and never exceeds 8 seconds. A 429 response is still a response
from the service — it counts toward the request total below like any
other request.

## The request contract

`fixtures/quota.json` records the terms this tenant's API key runs
under: `max_requests` is the total number of requests one backfill run
may make, and `max_in_flight` is the number of requests that may be
outstanding at the same time. The server keeps answering after those
numbers are passed — nothing at the transport layer stops a run — the
numbers are the terms of the key, recorded by the platform team.

In March a backfill client that re-requested pages it had already
received exhausted this tenant's request budget before the morning
load, and the catalog API was throttled for the tenant's other jobs
for an hour. The post-incident note is why the page cache exists in
this codebase: a page that has been fetched once is held in the cache
and served from there when it is needed again.
