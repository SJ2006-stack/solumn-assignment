# Support report

`/app/out/report.json`:

```json
{
  "schema": 1,
  "host": {"hostname": "...", "os": "linux", "cpu_count": 4},
  "disk": {"filesystems": [{"mount": "/", "size_bytes": 0, "used_bytes": 0}]}
}
```

Filesystems are sorted by mount. `used_bytes` is less than or equal to `size_bytes`. Mounts are absolute paths.
