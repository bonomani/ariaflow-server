# GAP: Rename ariaflow → ariaflow-server

## Package & Build
- [ ] `pyproject.toml:6` — `name = "ariaflow"` → `"ariaflow-server"`
- [ ] `pyproject.toml:41` — entry point `ariaflow =` → `ariaflow-server =`
- [ ] `pyproject.toml:32-34` — GitHub URLs `bonomani/ariaflow` → `bonomani/ariaflow-server`
- [ ] `Dockerfile:16` — CMD `ariaflow` → `ariaflow-server`
- [ ] `src/ariaflow.egg-info/` — regenerate after rename

## CLI
- [ ] `src/aria_queue/cli.py:17` — `prog="ariaflow"` → `prog="ariaflow-server"`
- [ ] `README.md:24-42` — all command examples `ariaflow` → `ariaflow-server`

## Service/Daemon Names
- [ ] `src/aria_queue/platform/linux.py:8` — `ariaflow-aria2.service` → `ariaflow-server-aria2.service`
- [ ] `src/aria_queue/platform/windows.py:9` — `ariaflow-aria2` → `ariaflow-server-aria2`
- [ ] `src/aria_queue/platform/launchd.py:9` — `com.ariaflow.aria2` → `com.ariaflow-server.aria2`

## Bonjour/mDNS (KEEP AS-IS)
- `_ariaflow._tcp` — protocol identifier, should NOT change (breaking for discovery)

## Homebrew References
- [ ] `src/aria_queue/install.py:136-137` — `brew install ariaflow` → `brew install ariaflow-server`
- [ ] `src/aria_queue/install.py:145-146` — `brew uninstall ariaflow` → `brew uninstall ariaflow-server`
- [ ] `.github/workflows/macos-install.yml:14-22` — brew tap/install commands
- [ ] `.github/workflows/release.yml` — formula generation references
- [ ] `scripts/homebrew_formula.py` — all URL and name references

## API
- [ ] `src/aria_queue/webapp.py:288` — `"ariaflow"` key in `/api/status` response (CAUTION: may break clients)
- [ ] `src/aria_queue/install.py:216-227,264-265,323-334` — plan/status keys

## Documentation
- [ ] `README.md` — title, command examples, URLs
- [ ] `CONTRIBUTING.md:6-7` — clone URL
- [ ] `SECURITY.md:6,34` — security advisory URLs
- [ ] `docs/PLAN.md` — installation references
- [ ] `docs/ARCHITECTURE.md` — references
- [ ] `docs/ALL_VARIABLES.md` — title and variable refs
- [ ] `openapi.yaml` — schema references
- [ ] `docs/governance/` — all governance docs

## Tests
- [ ] `tests/test_unit.py` — 45+ assertions
- [ ] `tests/test_api.py` — 30+ endpoint tests
- [ ] `tests/test_cli.py` — 30+ CLI tests
- [ ] `tests/test_web.py` — lifecycle mocking
- [ ] `tests/test_scenarios.py` — API scenarios
- [ ] `tests/test_homebrew_formula.py` — formula verification

## Scripts
- [ ] `scripts/publish.py:13` — `REPO = "bonomani/ariaflow"` → `"bonomani/ariaflow-server"`
- [ ] `scripts/homebrew_formula.py` — all references

## Notes
- Python module stays `aria_queue` (no rename needed for internal module)
- Bonjour `_ariaflow._tcp` stays unchanged (protocol identifier)
- API response key `"ariaflow"` rename may break existing frontends — coordinate with ariaflow-dashboard
