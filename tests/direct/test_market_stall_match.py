"""Direct tests for vendor profiles and deterministic stall allocation."""

import json


MARKET = json.dumps({
    "categories": [{"id": "FOOD", "description": "Prepared packaged food offered at the community market."}],
    "resources": [{"id": "POWER", "description": "A documented electrical service connection."}, {"id": "WATER", "description": "A documented potable water connection."}],
    "stalls": [{"id": "S1", "category_mask": 1, "resource_mask": 1, "location_rank": 2}],
})


def _market(contract, vm, organizer):
    vm.sender = organizer
    return contract.create_market("SATURDAY", MARKET, "organizer-layout-snapshot")


def _apply(contract, vm, vendor, market_id):
    vm.sender = vendor
    return contract.apply("APP-1", market_id, "Prepared packaged pantry food made for the community market.", "Vendor requests a documented electrical service connection.")


def _screen(contract, vm, vendor, application_id, category="FOOD", resources=None):
    vm.sender = vendor
    vm.mock_llm(r".*Screen a public market-vendor description.*", json.dumps({"category_id": category, "resource_ids": resources if resources is not None else ["POWER"]}))
    return contract.screen_application(application_id)


def test_market_stores_masks(contract, direct_vm, direct_alice):
    market_id = _market(contract, direct_vm, direct_alice)
    assert contract.get_market(market_id)["stalls"][0]["resource_mask"] == 1


def test_vendor_submits_application(contract, direct_vm, direct_alice, direct_bob):
    market_id = _market(contract, direct_vm, direct_alice)
    application_id = _apply(contract, direct_vm, direct_bob, market_id)
    assert contract.get_application(application_id)["state"] == "SUBMITTED"


def test_only_vendor_screens(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    market_id = _market(contract, direct_vm, direct_alice)
    application_id = _apply(contract, direct_vm, direct_bob, market_id)
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only_vendor"):
        contract.screen_application(application_id)


def test_consensus_profile_is_screened(contract, direct_vm, direct_alice, direct_bob):
    market_id = _market(contract, direct_vm, direct_alice)
    application_id = _apply(contract, direct_vm, direct_bob, market_id)
    assert _screen(contract, direct_vm, direct_bob, application_id) == "SCREENED"


def test_organizer_allocates_compatible_stall(contract, direct_vm, direct_alice, direct_bob):
    market_id = _market(contract, direct_vm, direct_alice)
    application_id = _apply(contract, direct_vm, direct_bob, market_id)
    _screen(contract, direct_vm, direct_bob, application_id)
    direct_vm.sender = direct_alice
    assert contract.allocate_next(market_id) == application_id
    assert contract.get_application(application_id)["assigned_stall"] == "S1"


def test_resource_mismatch_has_no_compatible_stall(contract, direct_vm, direct_alice, direct_bob):
    market_id = _market(contract, direct_vm, direct_alice)
    application_id = _apply(contract, direct_vm, direct_bob, market_id)
    _screen(contract, direct_vm, direct_bob, application_id, resources=["WATER"])
    direct_vm.sender = direct_alice
    contract.allocate_next(market_id)
    assert contract.get_application(application_id)["state"] == "NO_COMPATIBLE_STALL"


def test_vendor_accepts_offer(contract, direct_vm, direct_alice, direct_bob):
    market_id = _market(contract, direct_vm, direct_alice)
    application_id = _apply(contract, direct_vm, direct_bob, market_id)
    _screen(contract, direct_vm, direct_bob, application_id)
    direct_vm.sender = direct_alice
    contract.allocate_next(market_id)
    direct_vm.sender = direct_bob
    contract.answer_offer(application_id, True, "Vendor accepts the public stall assignment record.")
    assert contract.matches_assignment(application_id, "ACCEPTED", "S1") is True


def test_bad_profile_preserves_submission(contract, direct_vm, direct_alice, direct_bob):
    market_id = _market(contract, direct_vm, direct_alice)
    application_id = _apply(contract, direct_vm, direct_bob, market_id)
    with direct_vm.expect_revert("[LLM_ERROR] invalid_resource"):
        _screen(contract, direct_vm, direct_bob, application_id, resources=["NOPE"])
    assert contract.get_application(application_id)["state"] == "SUBMITTED"


def test_one_wallet_cannot_fill_market_with_multiple_keys(contract, direct_vm, direct_alice, direct_bob):
    market_id = _market(contract, direct_vm, direct_alice)
    _apply(contract, direct_vm, direct_bob, market_id)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("wallet_already_applied_to_market"):
        contract.apply("APP-2", market_id, "Another prepared packaged pantry food application for the same market.", "Vendor again requests a documented electrical service connection.")
    assert contract.get_market_active_application_count(market_id) == 1


def test_market_capacity_isolated_and_withdrawal_reclaims_slot(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    first_market = _market(contract, direct_vm, direct_alice)
    direct_vm.sender = direct_charlie
    second_market = contract.create_market("SUNDAY", MARKET, "second-organizer-layout-snapshot")
    application_id = _apply(contract, direct_vm, direct_bob, first_market)
    second_application = _apply(contract, direct_vm, direct_bob, second_market)
    assert contract.get_market_active_application_count(first_market) == 1
    assert contract.get_market_active_application_count(second_market) == 1
    direct_vm.sender = direct_bob
    contract.withdraw_application(application_id, "Vendor withdraws this synthetic market application.")
    assert contract.get_market_active_application_count(first_market) == 0
    assert contract.get_market_active_application_count(second_market) == 1
    assert contract.get_application(second_application)["market_id"] == second_market


def test_organizer_can_dismiss_and_reclaim_application_slot(contract, direct_vm, direct_alice, direct_bob):
    market_id = _market(contract, direct_vm, direct_alice)
    application_id = _apply(contract, direct_vm, direct_bob, market_id)
    direct_vm.sender = direct_alice
    contract.dismiss_application(application_id, "Organizer closes this synthetic application record.")
    assert contract.get_application(application_id)["state"] == "DISMISSED"
    assert contract.get_market_active_application_count(market_id) == 0
