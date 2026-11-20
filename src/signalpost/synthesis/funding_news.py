"""Cited funding and publisher-attributed news frames, checked by existing sentence_error."""
from collections import defaultdict
from ..models.synthesis import Sentence


def funding_sentence(envelope):
    claims=sorted((c for c in envelope.claims if c.availability=='available' and c.family=='funding' and c.evidence_ids),key=lambda c:c.field)
    if not claims:return None
    research=[c for c in claims if c.field.startswith('research.')]
    aid=[c for c in claims if c.field.startswith('state_aid.')]
    parts=[];used=[]
    if research:
        projects=[]
        for c in research:
            v=c.value;amount=v['total_project_award']['amount']
            projects.append('«'+v['title']+'» (total project award '+amount+')')
        parts.append('research projects with '+research[0].value['funder']+': '+ '; '.join(projects)+'; amounts are total project awards, potentially shared with collaborators')
        used+=research
    if aid:
        grouped=defaultdict(list)
        for c in aid:
            v=c.value;recipient=v['recipient_orgnr']
            scope='registered recipient subunit '+recipient if v.get('matched_via') else 'legal recipient this company ('+recipient+')'
            if v.get('specified_subunit_orgnr'):scope+='; specified recipient subunit '+v['specified_subunit_orgnr']
            grouped[v['instrument_type']].append((scope,c))
        groups=[]
        for instrument,records in sorted(grouped.items()):
            groups.append(instrument+': '+', '.join(sorted({scope for scope,c in records})))
            used += [c for scope,c in records]
        parts.append('state aid by instrument: '+'; '.join(groups))
    if not used:return None
    result=Sentence(text='funding snapshot: '+'; '.join(parts)+'.',claim_ids=[c.id for c in used])
    from .validate import sentence_error
    error=sentence_error(result,envelope)
    if error:raise ValueError('Funding synthesis rejected: '+error)
    return result


def news_sentences(envelope):
    from .validate import permitted,sentence_error
    claims=sorted((c for c in envelope.claims if c.availability=='available' and c.field.startswith('news_item.') and not c.carried_forward and permitted(c,envelope)),key=lambda c:(c.value['date'],c.value['url']),reverse=True)[:3]
    out=[]
    for c in claims:
        v=c.value;meaning=v.get('date_kind','')
        label='last modification date' if meaning.startswith('sitemap') else 'update date' if meaning=='feed update' else 'publication date'
        result=Sentence(text='published by the company: «'+v['title']+'» ('+label+' '+v['date']+').',claim_ids=[c.id])
        error=sentence_error(result,envelope)
        if error:raise ValueError('News synthesis rejected: '+error)
        out.append(result)
    return out
