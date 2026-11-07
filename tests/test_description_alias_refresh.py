"""Transport aliases cannot create company-description changes; actual changes stay distinct."""
import pytest
from signalpost.runner import placeholder,update
from signalpost.sources.extract import Source,Section,add
from signalpost.sources.blobstore import BlobStore
from signalpost.models.evidence import digest
from signalpost.refresh.diff import apply,align_description_aliases
ORG='923609016'

def snapshot(url,text='Identical company description',identity='verified-company'):
    env=placeholder(ORG,'test','2026-11-07T00:00:00Z',('website',))
    raw=('<meta name="description" content="'+text+'">').encode()
    source=Source(url,raw,'0'*64,'2026-11-07T00:00:00Z');section=Section()
    add(section,source,ORG,'website','official_website',{'final_url':'https://example.no','identity_level':'VERIFIED'},'website',span=text,source_class='company_owned')
    field='website_description.meta_description.'+digest(url)[:16]
    add(section,source,ORG,'website',field,{'text':text,'kind':'meta_description','self_description':True,'identity_level':'VERIFIED','identity_claim_id':identity},'meta:description',span=text,source_class='company_owned')
    update(env,'website',section);env.run.refresh['website']={'checked_urls':[url]}
    return env

@pytest.mark.parametrize('url',['https://www.example.no/en','http://www.example.no/en','http://example.no/en'])
def test_same_verified_page_description_keeps_previous_id_and_current_source(tmp_path,url):
    old=snapshot('https://example.no/en');new=snapshot(url);blobs=BlobStore(tmp_path)
    apply(old,None,blobs);before=next(c for c in old.claims if c.field.startswith('website_description.'))
    apply(new,old.model_dump(mode='json'),blobs)
    after=next(c for c in new.claims if c.field.startswith('website_description.'))
    assert after.id==before.id and after.field==before.field and after.value==before.value
    assert next(e for e in new.evidence if e.id==after.evidence_ids[0]).source_url==url
    assert not new.changes and not new.run.refresh['observation_changes']

@pytest.mark.parametrize('url,text,identity',[
 ('https://www.example.no/other','Identical company description','verified-company'),
 ('https://www.other.no/en','Identical company description','verified-company'),
 ('https://www.example.no/en','Changed company description','verified-company'),
 ('https://www.example.no/en','Identical company description','different-company-proof'),
 ('https://blog.example.no/en','Identical company description','verified-company')])
def test_different_page_text_host_or_identity_is_never_aliased(url,text,identity):
    old=snapshot('https://example.no/en');new=snapshot(url,text,identity)
    original=next(c for c in new.claims if c.field.startswith('website_description.')).id
    align_description_aliases(new,{c.field:c for c in old.claims},{e.id:e for e in old.evidence},{e.id:e for e in new.evidence})
    assert next(c for c in new.claims if c.field.startswith('website_description.')).id==original
