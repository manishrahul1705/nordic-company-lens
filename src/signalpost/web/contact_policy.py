"""Contact publication filters; never used for website ownership proof."""
import re
import unicodedata
from html.parser import HTMLParser
from types import SimpleNamespace
from urllib.parse import urlsplit

from .candidates import legal_name
from .policy import FREE_MAIL, extract
from .proof import phone

ROLES = frozenset("post postmottak firmapost info kontakt kundeservice service salg sales booking bestilling ordre regnskap faktura admin office hello hei mail support resepsjon contact kontor firma epost e-post hi enquiries inquiries orders order reservasjon drift teknisk marked marketing jobb jobs career karriere hr personal innkjop purchase accounts lonn bilag invoice".split())
STAFF = re.compile(r'(?:^|[\s_/-])(?:staff|team|employee|employees|person|ansatt|ansatte|tilsette|medarbeider|medarbeidere|visittkort|ansattkort)(?:$|[\s_/-])', re.I)
CONTACT = re.compile(r'contact|kontakt|footer|company.info|company.contact', re.I)
GIVEN = frozenset('ole ola per jan anne kari lars knut bjorn bj\u00f8rn geir tor tore terje hans arne erik eirik tom odd svein morten rune rolf vidar anny edith john paul'.split())


def key(value):
    text=str(value or '').casefold().replace('\u00e6','ae').replace('\u00f8','o')
    return ''.join(c for c in unicodedata.normalize('NFKD',text) if c.isascii() and c.isalnum())


class Regions(HTMLParser):
    def __init__(self,page,context):
        super().__init__(convert_charrefs=True)
        self.page=page;self.context=context;self.stack=[];self.regions=[];self.people=set()
        self.offsets=[0]
        for line in page.raw.split('\n')[:-1]:self.offsets.append(self.offsets[-1]+len(line)+1)
        self.feed(page.raw);self.close()
        for frame in self.stack:frame['end']=len(page.raw);self.regions.append(frame)

    def position(self):
        line,col=self.getpos();return self.offsets[line-1]+col

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);label=' '.join(attrs.get(k,'') or '' for k in ('class','id','itemtype'))
        frame={'tag':tag,'start':self.position(),'end':len(self.page.raw),'contact':tag in {'footer','address'} or bool(CONTACT.search(label)),
               'staff':bool(STAFF.search(label)) or 'schema.org/Person' in label,'text':[],
               'footer':tag=='footer' or bool(re.search(r'footer|(?:^|[ _-])foot(?:$|[ _-])',label,re.I)),
               'named':bool(re.search(r'a-navn|person.name|staff.name|employee.name',label,re.I))}
        if re.search(r'job.?title|stilling|position.title',label,re.I) and self.stack:
            self.stack[-1]['staff']=True
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(frame)

    def handle_data(self,text):
        if any(f['tag'] in {'script','style','noscript','template'} for f in self.stack):return
        for frame in self.stack:
            if frame['tag'] in {'h1','h2','h3','h4','h5','h6','strong','p'} or frame['named']:frame['text'].append(text)

    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag']!=tag:continue
            frame=self.stack[i];frame['end']=self.position()+len(tag)+3
            text=' '.join(frame['text']).strip()
            if tag in {'h1','h2','h3','h4','h5','h6','strong','p'} or frame['named']:
                parent=next((f for f in reversed(self.stack[:i]) if f['tag'] in {'div','section','article','li','td','address','footer'}),None)
                words=re.findall(r"[^\W\d_]+",text,re.UNICODE)
                if parent and key(text) in {'navn','name','tittelavdeling','stilling'}:
                    parent['staff']=True
                is_name=(2<=len(words)<=5 and all(w[:1].isupper() for w in words)
                         and not CONTACT.search(text) and legal_name(text)!=legal_name(self.context.get('name'))
                         and not re.search(r'\b(?:AS|ASA|Kontakt|Contact|Telefon|Phone|Email|Epost|V\u00e5re|Our|\u00c5pningstider)\b',text,re.I))
                if is_name and parent:
                    parent['staff']=True;self.people.add(key(text))
                    self.people.add(key(words[0][:1]+''.join(words[1:])))
                if parent and CONTACT.search(text):parent['contact']=True
            for closed in self.stack[i:]:
                closed['end']=frame['end'];self.regions.append(closed)
            self.stack=self.stack[:i];break


def email_allowed(address,context,target_domain,regions):
    address=address.strip().casefold();registered=str(context.get('email') or '').strip().casefold()
    if address and address==registered:return True
    if address.count('@')!=1:return False
    local,host=address.rsplit('@',1)
    root=extract(host).top_domain_under_public_suffix or host
    if root in FREE_MAIL or root!=target_domain:return False
    if local in ROLES:return True
    # Positive allowlist rejects all other personal/unknown locals by default.
    compact=key(local)
    label=extract(host).domain
    company=key(legal_name(context.get('name')))
    if compact not in {key(label),company} or not compact:return False
    if '.' in local:return False
    parts=re.split(r'[._-]+',local)
    common_person = any(compact.startswith(g) and len(compact)>len(g)+2
                        and re.search(r'(?:sen|son|berg|vik|haug|lund|heim|lie|dal|rud|gaard)$',compact[len(g):]) for g in GIVEN)
    if compact in GIVEN or common_person or compact in regions.people or (len(parts)>1 and (parts[0] in GIVEN or len(parts[0])==1)):
        return False
    return True


def phone_allowed(number,page,context,span,regions):
    if number in {phone(str(context.get(k) or '')) for k in ('phone','mobile')}:
        return True
    path=urlsplit(page.url).path
    pos=page.raw.find(span) if span else -1
    if pos<0:return False
    matches=[m for m in re.finditer(r'(?<!\d)(?:\+47|0047)?(?:[ .()-]*\d){8}(?!\d)',span) if phone(m.group())==number]
    if not matches:return False
    pos+=matches[0].start()
    containing=[f for f in regions.regions if f['start']<=pos<f['end']]
    if any(f['staff'] for f in containing):return False
    if STAFF.search(path) and not any(f['footer'] for f in containing):return False
    return any(f['contact'] for f in containing) or bool(re.search(r'/(?:kontakt[^/]*|contact[^/]*)(?:/|$)',path,re.I))


def filter_carried_contacts(envelope,blobs):
    """Historical contacts obey publication policy too, without touching proof."""
    if not any(c.carried_forward and c.field.startswith('contact.') for c in envelope.claims):return
    claims={c.field:c for c in envelope.claims if c.availability=='available'}
    get=lambda field:claims.get('identity.'+field)
    context={key:(get(field).value if get(field) else None) for key,field in
             [('name','legal_name'),('email','registered_email'),('phone','registered_phone'),('mobile','registered_mobile')]}
    proof=claims.get('official_website')
    evidence={e.id:e for e in envelope.evidence};removed=set();cache={}
    for claim in envelope.claims:
        if not claim.carried_forward or not claim.field.startswith('contact.') or claim.availability!='available':continue
        kind=claim.field.split('.')[1];keep=False
        for ref in claim.evidence_ids:
            e=evidence.get(ref)
            if e is None:continue
            target=extract(urlsplit(proof.value['final_url']).hostname or '').top_domain_under_public_suffix if proof else extract(urlsplit(e.source_url).hostname or '').top_domain_under_public_suffix
            if kind=='email':
                # Roles and exact registered emails need no page-name inference.
                keep=email_allowed(claim.value,context,target,SimpleNamespace(people=set()))
                if keep and (claim.value.casefold()==str(context.get('email') or '').casefold() or claim.value.split('@')[0].casefold() in ROLES):break
            elif kind=='phone' and claim.value in {phone(context.get(k)) for k in ('phone','mobile')}:
                keep=True;break
            else:keep=False
            try:
                from .html import Page
                key=(e.content_sha256,e.source_url)
                if key not in cache:
                    page=Page((blobs.directory/e.content_sha256).read_bytes(),e.source_url)
                    cache[key]=(page,Regions(page,context))
                page,regions=cache[key]
                keep=email_allowed(claim.value,context,target,regions) if kind=='email' else phone_allowed(claim.value,page,context,e.claim_span,regions)
            except (OSError,ValueError):keep=False
            if keep:break
        if not keep:removed.add(claim.field)
    if removed:
        envelope.claims=[c for c in envelope.claims if c.field not in removed]
        envelope.changes=[c for c in envelope.changes if c.field not in removed]
        if hasattr(envelope.profile,'values'):
            envelope.profile.values={c.field:c.value for c in envelope.claims}
        else:envelope.profile.claims=envelope.claims
