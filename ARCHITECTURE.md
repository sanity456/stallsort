# Architecture

Project: MarketStallMatch

Reusable primitive: vendor profile consensus -> bitmap compatibility -> deterministic least-surplus allocation -> vendor acceptance.

The contract separates caller-attested public inputs, validator-agreed semantic fields, deterministic state transitions, and role-bound final actions. It stores canonical JSON strings in GenVM maps, validates every identifier and bound before consensus, and keeps source references explicitly unverified.

The mechanism is not a renamed assessment record. Its state transitions, role topology, storage layout, deterministic algorithm, and public ABI are specific to this project.

<!-- correction-release-start -->
## Consensus and storage safety boundary

Profile validation now binds category/resource masks and digest to the attached canonical profile. Application storage is isolated per organizer-owned market, one wallet has one application identity per market, and withdrawn, dismissed, rejected, or accepted records safely release bounded capacity.

The on-chain state transition consumes only the canonical value returned by the post-consensus binding boundary. Operational records are isolated by an explicitly selected owner catalog, and fixed capacity is scoped or reclaimable.
<!-- correction-release-end -->
