# Correction and release record

Repository: stallsort

Contract: MarketStallMatch

Corrected release verified: 2026-09-01T09:21:25.826392Z

## Findings applied

This repository was checked against both steward findings from the rejected Boxcomplete and Baggate submissions:

1. A leader-provided digest is not proof of its attached substantive payload. Every result that affects state must be canonicalized, independently compared, and rebound after consensus.
2. A shared permissionless registry with fixed global capacity can be captured or exhausted. Operational catalogs must be explicitly owner-scoped, bounded per catalog, or safely reclaimable.
3. Corrected repository source is insufficient when the submitted Studio/Explorer address still runs an earlier build. The active address, deployed source, ABI, transaction, and evidence URLs must identify one release.

## Contract-specific correction

Profile validation now binds category/resource masks and digest to the attached canonical profile. Application storage is isolated per organizer-owned market, one wallet has one application identity per market, and withdrawn, dismissed, rejected, or accepted records safely release bounded capacity.

## Verified release lock

Current StudioNet address: 0xbf8422e50567d5658F6ac091FAAbE6f86b409EFd

Deployment transaction: 0x1e4a0e80435fbff05dd5131e4e745c0bbbd5e7dfd95f3d5c44dbe8fa897f34a3

Source SHA-256: 5ebc1c7905b40869259b56ce22e57433f072e9c5de6c140d37edc0895abc71fa

Superseded address: 0x24aBD4E3BA55681d4163f84A46cbBB1fc86c540e

The deployment manifest records exact byte-for-byte source readback, exact full ABI/schema equality, successful finalized execution for all 6 release transactions, role-separated external wallets, and the final state observed from StudioNet. The superseded address is historical only and must not be used in a new submission.

## Regression evidence

GenVM lint and strict typecheck: pass

Direct tests: 15 pass

Five-validator integration tests: 1 pass

Leader-payload or post-consensus injection regression tests: pass

Registry isolation and reclaim tests: pass

## Review boundary

No live collection. Category, resource, stall, vendor, and source-reference data are public caller declarations and are not authenticated.

It does not authenticate products, approve vendors, allocate legal space, collect fees, or verify resource and accessibility claims.

This record documents the implemented controls and verified release. It does not promise a particular human review outcome.
