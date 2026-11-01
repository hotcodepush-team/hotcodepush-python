# Changelog

## [0.5.0](https://github.com/hotcodepush-team/hotcodepush-python/compare/v0.4.0...v0.5.0) (2026-11-01)


### ⚠ BREAKING CHANGES

* HotCodePushError.code carries a code newer than the client as it is instead of unexpected_response, and is typed str.

### Features

* pass an unknown API error code through ([#10](https://github.com/hotcodepush-team/hotcodepush-python/issues/10)) ([5e86b60](https://github.com/hotcodepush-team/hotcodepush-python/commit/5e86b606d20833720d011a5e90c3b7002e3571a0))


### Documentation

* align CLAUDE.md with the handbook's shared lines ([#11](https://github.com/hotcodepush-team/hotcodepush-python/issues/11)) ([1e956d9](https://github.com/hotcodepush-team/hotcodepush-python/commit/1e956d91ef957a8084fa4b9efd706038b35aba65))

## [0.4.0](https://github.com/hotcodepush-team/hotcodepush-python/compare/v0.3.0...v0.4.0) (2026-11-01)


### ⚠ BREAKING CHANGES

* release conditions carry raw attribute values and device ids ([#7](https://github.com/hotcodepush-team/hotcodepush-python/issues/7))

### Features

* release conditions carry raw attribute values and device ids ([#7](https://github.com/hotcodepush-team/hotcodepush-python/issues/7)) ([e9c975e](https://github.com/hotcodepush-team/hotcodepush-python/commit/e9c975eef7840eea6b4e4d26409c56c00e06a756))

## [0.3.0](https://github.com/hotcodepush-team/hotcodepush-python/compare/v0.2.1...v0.3.0) (2026-10-31)


### ⚠ BREAKING CHANGES

* the API after the contract audit, one release list, qr-code, the renames, and the client alignments ([#5](https://github.com/hotcodepush-team/hotcodepush-python/issues/5))

### Features

* the API after the contract audit, one release list, qr-code, the renames, and the client alignments ([#5](https://github.com/hotcodepush-team/hotcodepush-python/issues/5)) ([1c5412c](https://github.com/hotcodepush-team/hotcodepush-python/commit/1c5412c0adb4a6e2189cbdb4624277af5977260c))

## [0.2.1](https://github.com/hotcodepush-team/hotcodepush-python/compare/v0.2.0...v0.2.1) (2026-10-31)


### Documentation

* rewrite README [skip ci] ([8864795](https://github.com/hotcodepush-team/hotcodepush-python/commit/8864795c0c025111386ee542ba618364f71bfab9))

## [0.2.0](https://github.com/hotcodepush-team/hotcodepush-python/compare/v0.1.0...v0.2.0) (2026-10-25)


### ⚠ BREAKING CHANGES

* HotCodePushError.code carries the API's lowercase codes, not_found rather than E_NOT_FOUND, and unexpected_response rather than E_UNEXPECTED_RESPONSE; Framework is react_native rather than react-native, and AudienceWarning.code is fingerprint_unknown or unsupported_condition_share. A caller comparing the old values must change them. The API answers the new spellings to every client version, so a comparison against "E_NOT_FOUND" never matches again, whichever client you pin.

### Features

* every catalog value of the client is lowercase snake_case ([b67c1a9](https://github.com/hotcodepush-team/hotcodepush-python/commit/b67c1a92a28b9b1de578dc94ff333c1d9b773ffa))


### Documentation

* the README installs from PyPI ([5142bdb](https://github.com/hotcodepush-team/hotcodepush-python/commit/5142bdb9606b96609efd4e2d45260816d1015a1a))

## 0.1.0 (2026-10-23)


### Features

* the app, release, device and notification resources ([6a90ac0](https://github.com/hotcodepush-team/hotcodepush-python/commit/6a90ac0dfd390f43dc9001ef4c200198691e9cc3))
* the organization, invitation and user resources ([8dfaae3](https://github.com/hotcodepush-team/hotcodepush-python/commit/8dfaae34a28fc774251e3a890a0e158bab7c16b0))
* the Python client's skeleton, transport and first resources ([95ff9f0](https://github.com/hotcodepush-team/hotcodepush-python/commit/95ff9f0cf4680cbe49004a8f3e3460adb5fd479c))


### Bug Fixes

* the contract test covers dict responses, one embed model ([58c1ad6](https://github.com/hotcodepush-team/hotcodepush-python/commit/58c1ad6b191046791a68689368864222ad61e228))
