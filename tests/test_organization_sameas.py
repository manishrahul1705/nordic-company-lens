import json
import pytest
from signalpost.web.html import Page
from signalpost.web.social import attributed,discover

CONTEXT={'name':'Example AS'}
PROOF={'final_url':'https://example.no','proof_page_url':'https://example.no/'}


def page(node,url='https://example.no/'):
    return Page(('<head><script type="application/ld+json">'+json.dumps(node)+'</script></head>').encode(),url)


@pytest.mark.parametrize('kind',['Organization','LocalBusiness',['Organization','Corporation'],'https://schema.org/Organization'])
def test_company_sameas_is_name_checked_and_localized(kind):
    p=page({'@type':kind,'name':'Example AS','sameAs':['https://www.linkedin.com/company/example','https://instagram.com/agency']})
    result=attributed(p,PROOF,CONTEXT)
    assert list(result)==['https://www.linkedin.com/company/example']
    assert next(iter(result.values())) in p.raw


@pytest.mark.parametrize('node',[
    {'@type':'Product','sameAs':'https://facebook.com/example'},
    {'@type':'Person','sameAs':'https://facebook.com/example'},
    {'sameAs':'https://facebook.com/example'},
    {'@type':'Person','worksFor':{'@type':'Organization','sameAs':'https://facebook.com/example'}},
])
def test_non_company_schema_cannot_publish_social(node):
    assert not attributed(page(node),PROOF,CONTEXT)


def test_foreign_organization_record_rejected_even_if_handle_matches():
    assert not attributed(page({'@type':'Organization','name':'Other AS','sameAs':'https://facebook.com/example'}),PROOF,CONTEXT)


def test_shared_domain_sameas_requires_company_scoped_record():
    proof={'final_url':'https://fus.no','proof_page_url':'https://fus.no/rolidbakken'}
    context={'name':'Rolidbakken FUS Barnehage AS'}
    node={'@type':'LocalBusiness','name':context['name'],'sameAs':'https://facebook.com/Rolidbakken-FUS-Barnehage-AS','url':'https://fus.no/'}
    assert not attributed(page(node,proof['proof_page_url']),proof,context)
    node['url']='https://fus.no/rolidbakken'
    assert len(attributed(page(node,proof['proof_page_url']),proof,context))==1


def test_graph_organization_and_object_uri_sameas():
    node={'@graph':[{'@type':'WebPage','sameAs':'https://facebook.com/other'},
                   {'@type':'Organization','name':'Example AS','sameAs':{'@id':'https://facebook.com/example'}}]}
    assert list(attributed(page(node),PROOF,CONTEXT))==['https://facebook.com/example']
