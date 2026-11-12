"""A bounded analyst briefing, recomputable entirely from supported local claims."""
import re
from datetime import date
from decimal import Decimal,ROUND_HALF_UP
from urllib.parse import urlsplit
from ..models.evidence import digest,canonical
from ..models.synthesis import AnalystBrief,AnalystSentence,ChangeClaim
from .nace import english_title
FORMS={'AS':'private limited company','ASA':'public limited company','ENK':'sole proprietorship',
       'NUF':'Norwegian branch of a foreign enterprise','SA':'cooperative','FLI':'association','STI':'foundation'}
MONTHS=('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
PLATFORMS={'facebook.com':'Facebook','linkedin.com':'LinkedIn','instagram.com':'Instagram','youtube.com':'YouTube',
           'tiktok.com':'TikTok','x.com':'X','twitter.com':'X','pinterest.com':'Pinterest','vimeo.com':'Vimeo',
           'github.com':'GitHub','flickr.com':'Flickr'}

def short_date(value):
    try:
        d=date.fromisoformat(str(value)[:10]);return f'{d.day} {MONTHS[d.month-1]} {d.year}'
    except ValueError:return None

def money(value,currency="NOK"):
    amount=Decimal(str(value));absolute=abs(amount)
    for scale,word in [(Decimal('1000000000'),'billion'),(Decimal('1000000'),'million')]:
        if absolute>=scale:return currency+' '+format((amount/scale).quantize(Decimal('.1'),rounding=ROUND_HALF_UP),'f')+' '+word
    return currency+' '+format(amount,',f').rstrip('0').rstrip('.') if amount.as_tuple().exponent<0 and '.' in format(amount,',f') else currency+' '+format(amount,',f')

def english_list(items):
    items=list(items)
    return items[0] if len(items)==1 else ', '.join(items[:-1])+' and '+items[-1] if items else ''


def number_claim(c):return c is not None and isinstance(c.value,(int,float)) and not isinstance(c.value,bool)

def major_event(value):
    path=value.get('changed_field','')
    if path=='/navn':return 'a registered name change'
    if path=='/kapital/belop':return 'a share capital change'
    if path=='/forretningsadresse' or path.startswith('/forretningsadresse/'):return 'a business address change'
    if path=='/postadresse' or path.startswith('/postadresse/'):return 'a postal address change'
    if path in {'/konkurs','/underAvvikling','/underTvangsavviklingEllerTvangsopplosning','/slettedato'}:return 'a registered status change'
    if path in {'/roller','/rollegrupper'} or path.startswith(('/roller/','/rollegrupper/')):return 'a registered role change'
    if path in {'/fusjon','/fisjon'}:return 'a merger registration' if path=='/fusjon' else 'a demerger registration'
    return None

def generate(envelope):
    from .validate import permitted
    result=AnalystBrief()
    claims=sorted((c for c in envelope.claims if c.availability=='available' and permitted(c,envelope)),key=lambda c:c.field)
    fields={c.field:c for c in claims}
    def context(field,value,evidence_ids=()):
        c=ChangeClaim(id=digest(['analyst-context',envelope.organisation_number,field,value]),field=field,value=value,evidence_ids=list(evidence_ids))
        result.context_claims.append(c);return c.id
    def state_context(family):
        return context('snapshot.analyst.'+family,{'state':envelope.run.sections.get(family,'not_applicable'),
                       'stale':family in envelope.run.refresh.get('stale_sections',{}),
                       'supported_fields':sorted(c.field for c in claims if c.family==family)})
    def add(kind,text,used,derived=False,count=None):
        ids=list(dict.fromkeys(c if isinstance(c,str) else c.id for c in used))
        result.sentences.append(AnalystSentence(sentence_type=kind,text=text,claim_ids=ids,value_kind='derived' if derived else 'reported',count=count,record_type='workplaces' if count is not None else None))
    name=fields.get('identity.legal_name')
    if name is None:
        add('f','Company identity could not be established from the checked sources.',[state_context('identity')]);return result
    used=[name];org=context('snapshot.analyst.organisation_number',envelope.organisation_number,name.evidence_ids);used.append(org)
    form=fields.get('identity.organisation_form');city=fields.get('identity.municipality')
    text=str(name.value)+' (org. '+envelope.organisation_number+')'
    if form and isinstance(form.value,dict):
        code=str(form.value.get('kode',''));desc=FORMS.get(code)
        text+=' is '+('an ' if desc and desc[:1].lower() in 'aeiou' else 'a ')+(desc or 'registered entity (legal form '+code+')');used.append(form)
    else:text+=' is a registered entity'
    if city and city.value:text+=' in '+str(city.value).title();used.append(city)
    founded=fields.get('identity.founding_date');registered=fields.get('identity.registration_date')
    for c,word in [(founded,'founded'),(registered,'registered')]:
        if c and re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(c.value)):
            text+=', '+word+' in '+str(c.value)[:4];used.append(c);break
    industry=next((c for c in claims if c.field.startswith('identity.nace') and english_title(c.value)),None)
    if industry:
        title=english_title(industry.value).replace('n.e.c.','not elsewhere classified')
        text+=', working in '+title[:1].lower()+title[1:];used.append(industry)
    purpose=fields.get('identity.statutory_purpose')
    if purpose:
        value=' '.join(str(x) for x in purpose.value) if isinstance(purpose.value,list) else str(purpose.value)
        value=' '.join(value.split()).strip().rstrip('.!?')
        if value and len(value.split())<25 and not re.search(r'[.!?]',value):
            text+='; its registered purpose (in Norwegian) is \u00ab'+value+'\u00bb';used.append(purpose)
    lei=fields.get('identity.gleif.lei')
    if lei:
        text+='; it is registered in GLEIF with LEI '+str(lei.value);used.append(lei)
    parent=fields.get('identity.gleif.direct_parent') or fields.get('identity.gleif.ultimate_parent')
    if parent and isinstance(parent.value,dict) and parent.value.get('name'):
        text+='. It is owned by '+parent.value['name']+' (GLEIF)';used.append(parent)
    add('a',text+'.',used)
    # Company-only annual amounts: no currency or unknown-scale conversion.
    financial=[c for c in claims if c.family=='accounts' and not c.field.startswith('accounts.consolidated.') and number_claim(c)
               and (c.reporting_period or {}).get('account_type')=='SELSKAP' and (c.reporting_period or {}).get('currency') in {'NOK','EUR'}
               and (c.reporting_period or {}).get('unit') in {None,(c.reporting_period or {}).get('currency')}]
    years=sorted({str(c.reporting_period.get('fiscal_year')) for c in financial if c.reporting_period.get('fiscal_year')},reverse=True)
    revenue=profit=None;size=[];used=[]
    if years:
        year=years[0]
        currency=next(c.reporting_period['currency'] for c in financial if str(c.reporting_period['fiscal_year'])==year)
        def amount(value):return money(value,currency)
        def metric(label,y):return next((c for c in financial if str(c.reporting_period['fiscal_year'])==y and c.field.rsplit('.',1)[-1]==label and c.reporting_period['currency']==currency),None)
        revenue=metric('revenue',year);profit=metric('net_result',year)
        if revenue and profit and revenue.value==profit.value and profit.value>=0:
            size.append('revenue and annual result were both '+amount(revenue.value));used.extend([revenue,profit])
        else:
            if revenue:size.append('it reported revenue of '+amount(revenue.value));used.append(revenue)
            if profit:size.append(('reported a loss of '+amount(abs(profit.value))) if profit.value<0 else ('an annual result of '+amount(profit.value)));used.append(profit)
        if size:
            text='In FY'+year+' '+(' and '.join(size))
            if not revenue:text='In FY'+year+' it '+(('reported a loss of '+amount(abs(profit.value))) if profit.value<0 else ('reported an annual result of '+amount(profit.value)))
            prior=metric('revenue',str(int(year)-1)) if revenue else None
            comparable=False
            if prior and prior.value>0:
                from ..sources.financial_comparability import FinancialObservation,ComparablePeriodGate
                def obs(c):
                    p=c.reporting_period
                    return FinancialObservation(envelope.organisation_number,str(p['fiscal_year']),p.get('period_start'),p.get('period_end'),p.get('currency'),p.get('unit'),p.get('account_type'),{'revenue':c.value})
                comparable=ComparablePeriodGate().compare(obs(revenue),obs(prior),metric='revenue').comparable
            if comparable:
                pct=((Decimal(str(revenue.value))-Decimal(str(prior.value)))/Decimal(str(prior.value))*100).quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
                if pct:
                    text+=', revenue '+('rose ' if pct>0 else 'fell ')+format(abs(pct),'f')+'% from '+str(prior.reporting_period['fiscal_year']);used.append(prior)
            chosen=revenue or profit
            if chosen.reporting_period.get('unit') is None:text+=' ('+currency+'-denominated reported figures; source scale not declared, no conversion applied)'
            add('b',text+'.',used,derived=bool(comparable))
    if number_claim(fields.get('identity.employees')):
        c=fields['identity.employees'];add('b','It has '+format(c.value,',')+' registered employees.',[c])
    units={str(c.value.get('organisation_number')):c for c in claims if c.field.startswith('subunits.unit.') and isinstance(c.value,dict) and c.value.get('organisation_number')}
    if units:
        cities=sorted({str((c.value.get('address') or {}).get('kommune')).title() for c in units.values() if (c.value.get('address') or {}).get('kommune')},key=str.casefold)
        text='It has '+('one' if len(units)==1 else str(len(units)))+' registered workplace'+('s' if len(units)!=1 else '')
        if cities:
            named=cities[:3]
            if len(cities)>3:named.append(str(len(cities)-3)+' more')
            text+=', in '+english_list(named)
        if envelope.run.sections.get('subunits')!='available' or 'subunits' in envelope.run.refresh.get('stale_sections',{}):text+=' (coverage could not be fully refreshed)'
        add('c',text+'.',list(units.values()),derived=True,count=len(units))
    # Newest significant event across all supported sources; buyer is not winner.
    events=[]
    for c in claims:
        if not isinstance(c.value,dict) or not short_date(c.value.get('date')):continue
        if c.field.startswith('dated_item.'):
            wording='Its latest company-published article is "'+c.value['title'].rstrip('.')+'" ('+short_date(c.value['date'])+').'
        elif c.field.startswith('registry_change.') and major_event(c.value):
            wording='A registry announcement dated '+short_date(c.value['date'])+' records '+major_event(c.value)+', according to the Br\u00f8nn\u00f8ysund Register.'
        elif c.field.startswith('procurement_award.'):
            buyers=c.value.get('buyer') or []
            buyers=[buyers] if isinstance(buyers,str) else buyers
            if c.value.get('matched_role')=='winner' and buyers:
                wording='It won a public contract from '+english_list(buyers)+' ('+short_date(c.value['date'])+', TED).'
            else:wording='A public procurement award dated '+short_date(c.value['date'])+' names it as buyer for "'+c.value['title']+'" (TED).'
        else:continue
        events.append((str(c.value['date'])[:10],c.field,c,wording))
    if events:
        _,_,c,wording=max(events,key=lambda item:(item[0],item[1]));add('d',wording,[c])
    website=fields.get('official_website')
    if website:
        host=(urlsplit(website.value['final_url']).hostname or '').lower()
        if host.startswith('www.'):host=host[4:]
        text='Its verified website is '+host;used=[website];platforms={}
        for c in claims:
            if not c.field.startswith('social_profile.') or not isinstance(c.value,dict):continue
            socialhost=(urlsplit(c.value.get('url','')).hostname or '').lower()
            label=next((v for k,v in PLATFORMS.items() if socialhost==k or socialhost.endswith('.'+k)),None)
            if label:platforms.setdefault(label,c)
        if platforms:text+=', with verified profiles on '+english_list(sorted(platforms));used.extend(platforms[k] for k in sorted(platforms))
        add('e',text+'.',used)
    else:add('e','No company website could be verified.',[state_context('website')])
    gaps=[];used=[]
    if not any(c.family=='accounts' and not c.field.startswith('accounts.consolidated.') and (c.reporting_period or {}).get('account_type')=='SELSKAP' for c in claims):
        gaps.append('Company-only accounts were not available in the checked sources');used.append(state_context('accounts'))
    hiring=envelope.run.sections.get('hiring')
    if hiring=='not_available':gaps.append('no active job ads were found in the checked sources');used.append(state_context('hiring'))
    elif hiring in {'failed','blocked','ambiguous'}:gaps.append('hiring information could not be fully checked');used.append(state_context('hiring'))
    if gaps:
        text='; '.join(gaps);add('f',text[:1].upper()+text[1:]+'.',used)
    # Collapse absent-source checklists only for genuinely sparse registry profiles.
    external=any(c.field.startswith(('identity.gleif.','procurement_award.','dated_item.','hiring.job.','hiring.site_job.')) or c.family=='website' for c in claims)
    if not external and not financial and not number_claim(fields.get('identity.employees')) and len(units)<=1:
        first=[s for s in result.sentences if s.sentence_type=='a']
        substantive=[s for s in result.sentences if s.sentence_type in {'c','d'}]
        if len(substantive)>1:substantive=[s for s in substantive if s.sentence_type=='d']
        gaps=[s for s in result.sentences if s.sentence_type in {'e','f'}]
        if gaps:
            combined=AnalystSentence(sentence_type='f',text='; '.join(s.text.rstrip('.') for s in gaps)+'.',claim_ids=list(dict.fromkeys(cid for s in gaps for cid in s.claim_ids)))
            result.sentences=first+substantive+[combined]
        else:result.sentences=(first+substantive)[:3]
    return result

def validate(brief,envelope):
    expected=generate(envelope)
    if brief.model_dump()!=expected.model_dump():raise ValueError('Unsupported analyst sentence, number, date or citation')
    known={c.id:c for c in envelope.claims if c.availability=='available'}
    contexts={c.id:c for c in brief.context_claims}
    for sentence in brief.sentences:
        if not sentence.claim_ids or any(cid not in known and cid not in contexts for cid in sentence.claim_ids):raise ValueError('Missing analyst citation')
    return brief
