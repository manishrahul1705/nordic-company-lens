import json
from signalpost.site import recorded_state_reasons, evidence_panel

def test_recorded_reasons_use_only_actual_codes_and_escape_markup():
    row={'errors':[{'section':'website','code':'website_candidates','message':json.dumps([{'reason':'parked'},{'reason':'different_legal_entity'},{'reason':'unrecognised'}])}]}
    original=json.dumps(row,sort_keys=True)
    output=recorded_state_reasons(row,'website')
    assert 'parked or for sale' in output and 'different publisher' in output
    assert 'unrecognised' not in output
    assert recorded_state_reasons(row,'activity')==''
    assert json.dumps(row,sort_keys=True)==original

def test_absence_without_recorded_reason_does_not_invent_one():
    assert recorded_state_reasons({'errors':[]},'website')==''
    assert recorded_state_reasons({'errors':[{'section':'website','code':'website_candidates','message':'bad json'}]},'website')==''
