# Repository Workflow

This repository is the source repo for `ariaflow`.

Working rules:

- Treat the WSL checkout as the source repo.
- Make edits and commits in WSL.
- Use Git to sync any companion repo or mirror.
- Keep release state aligned across the source repo and the Homebrew tap.

Release workflow:

- Make the code change in `ariaflow`.
- Run the local test suite before tagging.
- Bump the package version in `pyproject.toml` and `src/aria_queue/__init__.py`.
- Commit the version bump on `master`.
- Create and push the tag, for example `v0.1.1-alpha.13`.
- Publish a GitHub release from that tag.
- Verify the release is `isDraft: false` and `isPrerelease: true` for alpha releases.
- Update the Homebrew tap repo to point at the new tag and asset hash.
- Push the tap repo after the formula update.

Homebrew notes:

- The tap repo is the install surface for macOS users.
- When the release asset changes, update:
  - the formula `url`
  - the formula `sha256`
  - the formula `version`
- Do not leave the tap pointing at an older alpha tag after a new prerelease is published.

Verification:

- Check the source release on GitHub.
- Check the Homebrew formula version in the tap repo.
- On macOS, verify with:
  - `brew tap bonomani/ariaflow`
  - `brew upgrade ariaflow`
  - `ariaflow --version`

If this file conflicts with a direct user instruction, follow the user instruction.
