import hashlib
import json
from types import SimpleNamespace

import pytest

from signalpost.runner import placeholder
from signalpost.sources.extract import Section, Source, add
from signalpost.sources.fact_depth import histories, accounts
from signalpost.sources.registry_activity import publish

ORG = "923609016"

def source(data):
    body=json.dumps(data).encode()
    return Source("https://data.brreg.no/enhetsregisteret/api/enheter/"+ORG,
                  body,hashlib.sha256(body).hexdigest(),"2026-11-20T00:00:00Z")

def test_dated_identity_keeps_source_evidence_and_year_precision():
    env=placeholder(ORG,"ak","2026-11-20T00:00:00Z",("identity","activity"))
    section=Section()
    src=source({"stiftelsesdato":"2020-02-29","sisteInnsendteAarsregnskap":"2025"})
    for field,value,locator in [("founding_date","2020-02-29","/stiftelsesdato"),
                                ("latest_submitted_accounts","2025","/sisteInnsendteAarsregnskap")]:
        add(section,src,ORG,"identity","identity."+field,value,locator)
    env.claims=list(section.claims)
    env.evidence=section.evidence
    publish(env)
    publish(env)
    activity=[c for c in env.claims if c.field.startswith("registry_dated_activity.")]
    assert len(activity)==2
    assert {c.value for c in activity}=={"2020-02-29","2025"}
    assert activity[1].reasons["date_precision"]=="year"
    assert activity[0].evidence_ids==section.claims[0].evidence_ids
    assert env.claims[:2]==section.claims

@pytest.mark.parametrize("raw", [True,False,None,"false"])
def test_audit_status_uses_only_explicit_boolean(raw):
    row={"regnskapstype":"SELSKAP","virksomhet":{"organisasjonsnummer":ORG},
         "regnskapsperiode":{"tilDato":"2025-12-31"},
         "revisjon":{"ikkeRevidertAarsregnskap":raw}}
    section=Section()
    accounts(section,ORG,[row],source([row]))
    status=[c for c in section.claims if c.field.endswith(".audit_status")]
    assert len(status)==(1 if type(raw) is bool else 0)
    if status:
        assert status[0].value==("not_audited" if raw else "audited")
        assert status[0].reporting_period["fiscal_year"]=="2025"
        evidence=next(e for e in section.evidence if e.id in status[0].evidence_ids)
        assert evidence.locator=="/0/revisjon/ikkeRevidertAarsregnskap"

def test_previous_name_preserves_only_source_dates():
    data={"historiskeNavn":[{"navn":"Former AS","fraDato":"2018-01-01"},
                            {"navn":"Another AS","tilDato":"2017-12-31"}]}
    section=Section()
    histories(section,source(data),ORG,"identity","identity",data["historiskeNavn"],"/historiskeNavn")
    assert [c.value for c in section.claims]==data["historiskeNavn"]

