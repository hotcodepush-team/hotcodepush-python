# Breaking Changes

This is a comprehensive list of the breaking changes introduced in the minor version releases while the client is on `0.x`.

## Versions

- [Version 0.8.x](#version-08x)

## Version 0.8.x

### Flat Signature Fields

`apps.bundles.create` takes the signature as two arguments, `signature` and `signature_key_id`, instead of one `BundleSignature`, which is removed:

```diff
  client.apps.bundles.create(
      app_id=app_id,
-     signature=BundleSignature(key_id=key_id, value=value),
+     signature=value,
+     signature_key_id=key_id,
      ...
  )
```

### Renamed `is_in_use` Filter

`apps.bundles.list` and `apps.bundles.count` take `is_unused` instead of `is_in_use`, with the opposite meaning. `is_unused=True` lists the bundles no release and no binary uses, the ones retention will expire:

```diff
- client.apps.bundles.list(app_id=app_id, is_in_use=False)
+ client.apps.bundles.list(app_id=app_id, is_unused=True)
```

### Removed `source` Filter

`apps.bundles.list` and `apps.bundles.count` no longer take `source`. The list holds the uploaded bundles. The bundle a binary ships is read through the binary with `relations=["bundle"]`.

### Minimum Version

The API refuses versions below **0.8.0** with `client_update_required`. Update the client before the next call.
