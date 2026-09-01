import hashlib
import json
from pathlib import Path

from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address


def _ok(receipt):
    assert tx_execution_succeeded(receipt), json.dumps(receipt, default=str)


def _context(fragment, response):
    validators = get_validator_factory().batch_create_mock_validators(
        5,
        mock_llm_response={"nondet_exec_prompt": {fragment: json.dumps(response)}},
    )
    return {
        "validators": [validator.to_dict() for validator in validators],
        "genvm_datetime": "2026-08-25T12:00:00Z",
    }


def _deploy(contract_file, owner_account):
    factory = get_contract_factory(
        contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / contract_file
    )
    receipt = factory.deploy_contract_tx(
        args=[],
        account=owner_account,
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    _ok(receipt)
    return factory, extract_contract_address(receipt)


def _send(method, args, context=None):
    if context is None:
        receipt = method(args=args).transact(
            wait_transaction_status=TransactionStatus.FINALIZED
        )
    else:
        receipt = method(args=args).transact(
            transaction_context=context,
            wait_transaction_status=TransactionStatus.FINALIZED,
        )
    _ok(receipt)
    return receipt


def test_five_validator_profile_and_stall_allocation_flow():
    organizer_account, vendor_account = create_accounts(2)
    factory, address = _deploy("market_stall_match.py", organizer_account)
    organizer = factory.build_contract(address, account=organizer_account)
    vendor = factory.build_contract(address, account=vendor_account)
    market_id = f"{str(organizer_account.address).lower()}:SATURDAY"
    application_id = f"{market_id}:{str(vendor_account.address).lower()}"
    market = json.dumps({
        "categories": [{"id": "FOOD", "description": "Prepared packaged food offered at the community market."}],
        "resources": [{"id": "POWER", "description": "A documented electrical service connection."}, {"id": "WATER", "description": "A documented potable water connection."}],
        "stalls": [{"id": "S1", "category_mask": 1, "resource_mask": 1, "location_rank": 2}],
    })
    _send(organizer.create_market, ["SATURDAY", market, "organizer-layout-snapshot"])
    _send(vendor.apply, ["APP-1", market_id, "Prepared packaged pantry food made for the community market.", "Vendor requests a documented electrical service connection."])
    _send(
        vendor.screen_application,
        [application_id],
        _context("Screen a public market-vendor description", {"category_id": "FOOD", "resource_ids": ["POWER"]}),
    )
    _send(organizer.allocate_next, [market_id])
    _send(vendor.answer_offer, [application_id, True, "Vendor accepts the public stall assignment record."])
    assert vendor.matches_assignment(args=[application_id, "ACCEPTED", "S1"]).call() is True
