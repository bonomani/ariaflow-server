# Release

`ariaflow` is the source repo for the headless engine and the Homebrew-driven
release flow.

## Preferred Flow

Run the helper from a clean checkout on `main`:

```bash
python3 scripts/release.py --dry-run
python3 scripts/release.py --push
```

The helper will:

- validate that `pyproject.toml` and `src/aria_queue/__init__.py` agree
- refuse to reuse an existing tag
- run `py_compile` and `python3 -m unittest discover -s tests -v` unless `--no-tests` is used
- bump the package version
- commit the version bump
- create the matching `vX.Y.Z` tag
- push `main` and tags when `--push` is given

The helper promotes an alpha package version to the matching stable release.
Once the repo is already on a stable version, it bumps the patch version
automatically, for example `0.1.1` to `0.1.2`.

Useful flags:

- `--dry-run`: print the release plan without changing files
- `--version 0.1.2`: set an explicit stable version instead of auto-bumping
- `--no-tests`: skip local tests
- `--allow-dirty`: bypass the clean-tree check

## After Tag Push

The GitHub workflow in `.github/workflows/release.yml` runs automatically on
tag pushes. It will:

- run the test suite again on GitHub Actions
- build the source distribution
- create the GitHub release
- update `bonomani/homebrew-ariaflow/Formula/ariaflow.rb` directly

## Manual Flow

If you do not use the helper, keep the sequence the same:

1. Update the version in `pyproject.toml`.
2. Update `src/aria_queue/__init__.py` to the same version.
3. Run the local test suite.
4. Commit the version bump on `main`.
5. Create the matching tag, for example `v0.1.2`.
6. Push `main` and the tag.

The GitHub workflow only publishes stable tags. Tags containing `-` are ignored
so old alpha tag shapes cannot become normal Homebrew releases by mistake.

## Verification

After release:

- verify the GitHub release is published as a normal release
- verify the Homebrew tap formula updated to the same version
- on macOS, check:

```bash
brew tap bonomani/ariaflow
brew upgrade ariaflow
ariaflow --version
```

## GitHub Secret

Set `ARIAFLOW_TAP_TOKEN` in this repo with write access to
`bonomani/homebrew-ariaflow`. The release workflow uses it to commit the
formula update.

## Tooling Note

The automated release path only needs `git`, Python, and the
`ARIAFLOW_TAP_TOKEN` GitHub secret.
