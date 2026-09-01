"""Adversarial vendor-profile payload binding regressions."""

import hashlib
import json

from tests.direct.test_market_stall_match import _apply, _market, _screen


def _hash(category_id, resource_ids):
    value = {"category_id": category_id, "resource_ids": sorted(resource_ids)}
    wire = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return "sha256:" + hashlib.sha256(wire.encode("ascii")).hexdigest()


FORGED = {
    "category_id": "FOOD",
    "resource_ids": ["WATER"],
    "resource_mask": 2,
    "profile_sha256": _hash("FOOD", ["POWER"]),
}


def _captured(contract, vm, organizer, vendor):
    market_id = _market(contract, vm, organizer)
    application_id = _apply(contract, vm, vendor, market_id)
    _screen(contract, vm, vendor, application_id)
    return application_id


def test_validator_rejects_changed_profile_with_honest_hash(contract, direct_vm, direct_alice, direct_bob):
    _captured(contract, direct_vm, direct_alice, direct_bob)
    assert direct_vm.run_validator(leader_result=FORGED) is False


def test_validator_rejects_mask_not_derived_from_resources(contract, direct_vm, direct_alice, direct_bob):
    _captured(contract, direct_vm, direct_alice, direct_bob)
    forged = dict(FORGED)
    forged["resource_ids"] = ["POWER"]
    assert direct_vm.run_validator(leader_result=forged) is False


def test_validator_accepts_honest_complete_profile(contract, direct_vm, direct_alice, direct_bob):
    _captured(contract, direct_vm, direct_alice, direct_bob)
    assert direct_vm.run_validator() is True


def test_post_consensus_forgery_preserves_submitted_application(contract, direct_vm, direct_alice, direct_bob, monkeypatch):
    from genlayer import gl

    market_id = _market(contract, direct_vm, direct_alice)
    application_id = _apply(contract, direct_vm, direct_bob, market_id)
    before = contract.get_application(application_id)
    direct_vm.sender = direct_bob
    monkeypatch.setattr(gl.vm, "run_nondet_unsafe", lambda *args: FORGED)
    with direct_vm.expect_revert("profile_hash_mismatch"):
        contract.screen_application(application_id)
    assert contract.get_application(application_id) == before
