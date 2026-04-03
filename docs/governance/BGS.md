# BGS Entry

project_name: ariaflow
bgs_slice: BGS-State-Modeled-Governed-Verified
decision_reason: >
  Stateful download engine with session/run lifecycle, preflight gates,
  and explicit execution contracts. The scope depends on installation,
  runtime readiness, recovery, and transition legality — requires
  ASM-based state model with preflight governance.
applies_to_scope: "engine execution path: session → run → queue → job lifecycle"
decision_record_path: "./docs/governance/bgs-decision.yaml"
last_reviewed: 2026-04-03

members_used:
  - BISS — boundary classification (11 boundaries, 8 interaction classes)
  - ASM — state model (4 axes: session, run, job, daemon; 6 coherence rules)
  - UIC — preflight gates (aria2_available, queue_readable) + 9 preferences
  - UCC — structured execution results (UCCResult dataclass)
  - TIC — test oracle (330 tests, trace targets across ASM/UIC/UCC)

read_next:
  - "./docs/ARCHITECTURE.md"
  - "./docs/STATES_AND_INTERACTIONS.md"
  - "./docs/governance/asm-state-model.md"
  - "./docs/governance/biss-classification.md"
  - "./docs/governance/tic-oracle.md"
  - "./docs/ARIA2_RPC_WRAPPERS.md"
  - "./src/aria_queue/contracts.py"
  - "./tests/"
