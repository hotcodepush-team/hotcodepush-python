# Breaking Changes

This is a comprehensive list of the breaking changes introduced in the minor version releases while the client is on `0.x`.

## Versions

- [Version 0.9.x](#version-09x)
- [Version 0.8.x](#version-08x)

## Version 0.9.x

### Open Catalogs in Responses

Every catalog field of a returned model is typed `Literal[...] | str`, such as `App.framework` as `Framework | str`. A value newer than your client now arrives as it is. Before, the whole call raised a pydantic `ValidationError`. Method arguments keep their closed types.

Nothing changes at runtime for the values your client knows. Only code checked with mypy or pyright must change, in two cases.

Code that handles every value needs a branch for a value it does not know:

```diff
  match app.framework:
      case "capacitor" | "cordova":
          ...
      case "expo" | "react_native":
          ...
-     case _ as unreachable:
-         assert_never(unreachable)
+     case _:
+         ...
```

A value from a response that goes into a method argument, or into anything typed with the closed alias, must be narrowed first. A `match` on the known values narrows it, and so does a `TypeGuard` function. `==` and `in` do not narrow it under mypy:

```diff
- client.organizations.apps.create(framework=app.framework, ...)
+ match app.framework:
+     case "capacitor" | "cordova" | "expo" | "react_native":
+         client.organizations.apps.create(framework=app.framework, ...)
```

### Unknown Release Conditions

`Release.conditions` is typed as a list of `ReleaseCondition | UnknownCondition`. A condition your client cannot read, such as one of a type newer than your client, arrives as an `UnknownCondition`. It keeps its `type`. Its other fields are in `model_extra`, under the API's camelCase names. Before, the whole call raised a pydantic `ValidationError`.

Code checked with mypy or pyright that handles every condition model needs a branch for `UnknownCondition`. A check of `condition.type` no longer narrows the model, so use `isinstance` or a class pattern:

```diff
  match condition:
      case AttributeCondition():
          ...
+     case UnknownCondition():
+         ...
```

The `conditions` argument of `apps.channels.releases.create` takes only the five known models. When a release holds an `UnknownCondition`, stop and update the client before you pass its conditions on. Never leave the condition out, since that widens the audience.

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
