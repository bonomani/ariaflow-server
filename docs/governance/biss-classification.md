# BISS Classification — Ariaflow

## Boundary Inventory

| Boundary | Type | Direction | Classification | Notes |
|---|---|---|---|---|
| aria2 RPC | tool-to-tool | outbound | execution | Engine → aria2 daemon via JSON-RPC |
| HTTP API | system-to-user | inbound | query / command | External clients → engine REST API |
| Queue file | system-to-storage | internal | state persistence | JSON file read/write for queue state |
| Declaration file | system-to-storage | internal | contract persistence | UCC declaration stored as JSON |
| Config directory | system-to-filesystem | internal | configuration | Engine config and state directory |
| Bonjour/mDNS | system-to-network | outbound | discovery | Service advertisement on local network |
| Homebrew | system-to-package-manager | external | installation | brew install/upgrade lifecycle |

## Interaction Classes

- **execution**: the engine delegates download work to aria2 via RPC
- **query/command**: external clients read state or issue commands via HTTP
- **state persistence**: queue and declaration files are the source of truth
- **discovery**: Bonjour advertises the service for local network clients
- **installation**: Homebrew manages the install/upgrade lifecycle
