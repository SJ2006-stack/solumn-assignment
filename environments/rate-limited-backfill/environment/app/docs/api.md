# Catalog API

`GET /v1/items?cursor=` returns one page.

- An empty `cursor` starts at item 1.
- A cursor is the id of the last item already returned. The next page starts at that id plus one.
- Each page holds at most `page_size` items.
- An item is `{"id": <int>, "name": "item-NN"}` with the id zero-padded to two digits in the name.
- `next_cursor` is the last id on the page, as a string, or `null` when the page reaches `item_count`.
- The server answers even after `max_requests`. Callers still have to stay within `max_requests` and `max_in_flight` from `fixtures/quota.json`.
