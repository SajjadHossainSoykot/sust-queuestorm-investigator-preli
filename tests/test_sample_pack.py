import json
from pathlib import Path
import pytest
from app.investigator import analyze_ticket
from app.schemas import AnalyzeTicketRequest

SAMPLE_PACK_PATH = Path(__file__).resolve().parents[1] / "samples" / "public_sample_cases.json"

def load_cases():
    with open(SAMPLE_PACK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["cases"]

@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c["id"])
def test_sample_case(case):
    input_data = case["input"]
    expected = case["expected_output"]
    
    # Run the investigator logic
    req = AnalyzeTicketRequest(**input_data)
    res = analyze_ticket(req)
    
    # Assert matching attributes
    assert res.ticket_id == expected["ticket_id"], f"Failed ticket_id on {case['id']}"
    assert res.relevant_transaction_id == expected["relevant_transaction_id"], f"Failed relevant_transaction_id on {case['id']}. Got: {res.relevant_transaction_id}, Expected: {expected['relevant_transaction_id']}"
    assert res.evidence_verdict == expected["evidence_verdict"], f"Failed evidence_verdict on {case['id']}. Got: {res.evidence_verdict}, Expected: {expected['evidence_verdict']}"
    assert res.case_type == expected["case_type"], f"Failed case_type on {case['id']}. Got: {res.case_type}, Expected: {expected['case_type']}"
    assert res.severity == expected["severity"], f"Failed severity on {case['id']}. Got: {res.severity}, Expected: {expected['severity']}"
    assert res.department == expected["department"], f"Failed department on {case['id']}. Got: {res.department}, Expected: {expected['department']}"
    assert res.human_review_required == expected["human_review_required"], f"Failed human_review_required on {case['id']}. Got: {res.human_review_required}, Expected: {expected['human_review_required']}"
