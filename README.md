# MarketStallMatch

A reusable market layout where validators map vendor descriptions to category and resource masks, then code allocates the lowest-surplus compatible free stall in application order for vendor acceptance.

The repository is standalone and the contract is reusable: one deployment can hold multiple independent records for unrelated callers. It has no frontend and moves no funds.

## Native mechanism

vendor profile consensus -> bitmap compatibility -> deterministic least-surplus allocation -> vendor acceptance.

## Actors

market organizer, vendors, GenLayer validators.

## Source boundary

No live collection. Category, resource, stall, vendor, and source-reference data are public caller declarations and are not authenticated.

## Safety boundary

It does not authenticate products, approve vendors, allocate legal space, collect fees, or verify resource and accessibility claims.

All inputs and results are public. Untrusted public data is delimited in prompts and cannot change the closed response schema. A malformed or non-consensus model result fails without committing the intended state transition.

## Verification

    genvm-lint check contracts/market_stall_match.py
    genvm-lint typecheck contracts/market_stall_match.py --strict
    python -m pytest tests/direct -q -p no:cacheprovider
    python tests/run_glsim.py --port 4000 --validators 5 --no-browser
    python -m pytest tests/integration -q -s -p no:cacheprovider

See ARCHITECTURE.md, SECURITY.md, SOURCE_PROVENANCE.md, AUDIT.md, SUBMISSION_CHECKLIST.md, and deployments/studionet.json.

MIT licensed.

<!-- correction-release-start -->
## Corrected release integrity

The full twelve-repository correction audit applied both steward findings to this contract. Profile validation now binds category/resource masks and digest to the attached canonical profile. Application storage is isolated per organizer-owned market, one wallet has one application identity per market, and withdrawn, dismissed, rejected, or accepted records safely release bounded capacity.

The current StudioNet release is `0xbf8422e50567d5658F6ac091FAAbE6f86b409EFd`. Its source bytes and full schema were read back from StudioNet and matched this repository exactly. Use `CORRECTION.md`, `REVIEW_RESPONSE.txt`, and the commit-pinned `deployments/studionet.json` for submission evidence; do not reuse the superseded address `0x24aBD4E3BA55681d4163f84A46cbBB1fc86c540e`.
<!-- correction-release-end -->
