from ..workers import offload
from ..budget import SourceFailure
import asyncio
from ..models.envelope import Error
from .extract import Section, add, finish, decode, response_source, get

URL = "https://data.brreg.no/regnskapsregisteret/regnskap/"
PATHS = {
    "revenue": ("resultatregnskapResultat", "driftsresultat", "driftsinntekter", "sumDriftsinntekter"),
    "operating_result": ("resultatregnskapResultat", "driftsresultat", "driftsresultat"),
    "result_before_tax": ("resultatregnskapResultat", "ordinaertResultatFoerSkattekostnad"),
    "net_result": ("resultatregnskapResultat", "aarsresultat"),
    "equity": ("egenkapitalGjeld", "egenkapital", "sumEgenkapital"),
    "total_assets": ("eiendeler", "sumEiendeler"),
    "total_liabilities": ("egenkapitalGjeld", "gjeldOversikt", "sumGjeld"),
    'paid_in_equity':('egenkapitalGjeld','egenkapital','innskuttEgenkapital','sumInnskuttEgenkaptial'),
    'retained_equity':('egenkapitalGjeld','egenkapital','opptjentEgenkapital','sumOpptjentEgenkapital'),
    'current_liabilities':('egenkapitalGjeld','gjeldOversikt','kortsiktigGjeld','sumKortsiktigGjeld'),
    'long_term_liabilities':('egenkapitalGjeld','gjeldOversikt','langsiktigGjeld','sumLangsiktigGjeld'),
    'equity_and_liabilities':('egenkapitalGjeld','sumEgenkapitalGjeld'),
    'non_current_assets':('eiendeler','anleggsmidler','sumAnleggsmidler'),
    'current_assets':('eiendeler','omloepsmidler','sumOmloepsmidler'),
    'cash_and_bank':('eiendeler','sumBankinnskuddOgKontanter'),
    'receivables':('eiendeler','sumFordringer'),'investments':('eiendeler','sumInvesteringer'),
    'inventories':('eiendeler','sumVarer'),'goodwill':('eiendeler','goodwill'),
    'sales_income':('resultatregnskapResultat','driftsresultat','driftsinntekter','salgsinntekter'),
    'salary_expenses':('resultatregnskapResultat','driftsresultat','driftskostnad','loennskostnad'),
    'operating_expenses':('resultatregnskapResultat','driftsresultat','driftskostnad','sumDriftskostnad'),
    'financial_income':('resultatregnskapResultat','finansresultat','finansinntekt','sumFinansinntekter'),
    'financial_expenses':('resultatregnskapResultat','finansresultat','finanskostnad','sumFinanskostnad'),
    'other_interest_expense':('resultatregnskapResultat','finansresultat','finanskostnad','annenRentekostnad'),
    'group_interest_expense':('resultatregnskapResultat','finansresultat','finanskostnad','rentekostnadSammeKonsern'),
    'financial_result':('resultatregnskapResultat','finansresultat','nettoFinans'),
    'tax_expense':('resultatregnskapResultat','ordinaertResultatSkattekostnad'),
    'total_comprehensive_result':('resultatregnskapResultat','totalresultat'),
}


async def fetch(org, http):
    response = await http.get(URL + org, org)
    return await offload(extract,org,response,http.blobs)


def extract(org,response,blobs):
    data, error = decode(response, "accounts")
    if error:
        return error
    if not isinstance(data, list):
        raise SourceFailure("malformed_accounts")
    section = Section()
    if not data:
        add(section, response_source(response), org, "accounts", "accounts.latest", None, "/")
        return finish(section)
    indexed = [(index, row) for index, row in enumerate(data) if isinstance(row, dict) and row.get("regnskapstype") == "SELSKAP"]
    if not indexed:
        add(section, response_source(response), org, "accounts", "accounts.latest", None, "/")
        section.errors.append(Error(section="accounts", code="entity_accounts_unavailable", message="Only consolidated or unknown account types returned; entity financials not published"))
        from .fact_depth import accounts
        accounts(section,org,data,response_source(response))
        return finish(section)
    indexed.sort(key=lambda pair: (str(get(pair[1], ("regnskapsperiode", "tilDato")) or ""), str(pair[1].get("journalnr") or ""), pair[0]), reverse=True)
    index, record = indexed[0]
    entity = record.get("virksomhet", {})
    reported_org = entity.get("organisasjonsnummer") if isinstance(entity, dict) else None
    if str(reported_org) != org:
        raise SourceFailure("wrong_company", "Accounts do not explicitly match the requested orgnr")
    seen_years = set()
    selected = []
    for idx, row in indexed:
        row_entity = row.get("virksomhet", {})
        row_org = row_entity.get("organisasjonsnummer") if isinstance(row_entity, dict) else None
        if not row_org or str(row_org) != org:
            continue
        period = row.get("regnskapsperiode") or {}
        end = period.get("tilDato")
        year = str(end)[:4] if end else None
        if not year or year in seen_years:
            continue
        seen_years.add(year)
        selected.append((idx, row, year, end, period))
    for item_idx, (idx, rec, year, end, period) in enumerate(selected):
        is_latest = (item_idx == 0)
        reporting = {"fiscal_year": year, "period_start": period.get("fraDato"), "period_end": end,
                     "currency": rec.get("valuta"), "unit": rec.get("enhet"), "account_type": rec.get("regnskapstype")}
        reported_identity = dict(reporting)
        confirmed = reporting['unit'] is None and reporting['currency'] == 'NOK'
        if confirmed:
            reporting.update({'unit': 'NOK', 'source_unit': None, 'unit_basis': 'four_exact_parent_2025_ratios_within_0.995_1.005'})
        for name, path in PATHS.items():
            value = get(rec, path)
            if value is None and name not in {'revenue','operating_result','result_before_tax','net_result','equity','total_assets','total_liabilities'}:
                continue
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
                raise SourceFailure("malformed_financial_value", name)
            field_name = ("accounts." + name) if is_latest else f"accounts.history.{year}.{name}"
            add(section, response_source(response), org, "accounts", field_name, value,
                f"/{idx}/" + "/".join(path), reporting=reporting, effective=end, id_reporting=reported_identity)
            if confirmed:
                # Calibration describes the unit policy, not this company's
                # reported amount. Cite only its exact registry response.
                section.claims[-1].reasons['unit'] = 'whole_NOK_confirmed_by_four_ratio_calibration_no_multiplier'
            if reporting["unit"] is None:
                section.claims[-1].reasons["unit"] = "scale_not_declared_by_source_or_reviewed_openapi"
                section.claims[-1].reasons["unit_crosscheck"] = "NOK_calibration_not_applied_to_other_or_missing_currencies"
    from .fact_depth import accounts
    accounts(section,org,data,response_source(response))
    return finish(section)
