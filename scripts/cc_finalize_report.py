"""Offline final report enrichment; no network calls."""
import collections,hashlib,json,subprocess,time
from osm_check import org
from signalpost.web.policy import domain,normalize_url
from signalpost.identity.orgnr import valid
import signalpost.web.proof as proof_module
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'bench/reports/cc-proto'
def main():
 s=json.loads((OUT/'summary.json').read_text(encoding='utf8'));query=json.loads((OUT/'columnar-query.json').read_text(encoding='utf8'))
 rows=[json.loads(x) for x in (OUT/'raw/warc-results.jsonl').read_text(encoding='utf8').splitlines() if x.strip()];results={x['key']:x for x in rows}
 parsed=[x for x in results.values() if x.get('fetched') and 'error' not in x]
 attempted=len(results);s['processed_records']=attempted;s['parsed_records']=len(parsed);s['records_fetched']=sum(bool(x.get('fetched')) for x in results.values())
 s['successful_warc_range_payload_MB']=sum(x.get('compressed_bytes',0) for x in rows)/1e6
 s['MB_downloaded_scope']='Successful WARC range payloads; excludes failed/aborted attempts, HTTP overhead and uninstrumented DuckDB projected Parquet traffic.'
 s['parquet_network_MB']=None
 s['pipeline_resume_wall_seconds']=None;s['pipeline_resume_wall_seconds_note']='Not retained separately across resumptions; wall_seconds measures the complete columnar retry task.';s['wall_seconds']=time.time()-datetime.fromisoformat(json.loads((OUT/'columnar-run.json').read_text(encoding='utf8'))['task_started_utc'].replace('Z','+00:00')).timestamp();s['wall_seconds_scope']='Whole columnar retry task from2026-11-11T05:14:31Z, including setup, retries, archive processing, live review and report preparation.'
 s['source_sample']={'selected_index_records':query.get('records_selected'),'selected_domains':query.get('domains_selected'),'parquet_files_probed':len(query['files_queried']),'nonempty_parquet_files':[p for p,c in query.get('rows_per_file',{}).items() if c>0],'scope':'One nonempty Parquet file supplies sample;129 earlier files returned zero filtered rows; not a representative .no crawl sample. Fixed-seed shuffle of selected records before WARC processing.'}
 cc_candidates=[json.loads(x) for x in (OUT/'candidates.jsonl').read_text(encoding='utf8').splitlines() if x.strip()]
 osm_candidates=[json.loads(x) for x in (ROOT/'bench/reports/osm-check/candidates.jsonl').read_text(encoding='utf8').splitlines() if x.strip()]
 assert all(valid(x['orgnr']) and valid(x['parent_orgnr']) and len(x['snippet'])<=120 for x in cc_candidates)
 cc_pd={(x['parent_orgnr'],x['domain']) for x in cc_candidates}
 osm_pd={(x['parent_orgnr'],domain(normalize_url(x['website']))) for x in osm_candidates if normalize_url(x['website'])}
 s['osm_overlap']['domains']=len({d for _,d in cc_pd}&{d for _,d in osm_pd})
 s['osm_overlap']['same_parent_and_domain_pairs']=len(cc_pd&osm_pd)
 m=s.get('universe',{}).get('matches');n=s.get('universe',{}).get('size',411160);total=s.get('records_selected',20000)
 factor=total/attempted if attempted else None
 if m is not None:s['osm_overlap']['universe_parent_companies']=m-s['osm_overlap']['new_universe_matches']
 s['extrapolation']={'observed_matched_parents':m,'partial_to_selected_record_factor':factor,'selected_sample_linear_scenario':min(n,m*factor) if m is not None and factor else None,'full_no_flat_file_linear_scenario':min(n,m*factor*300/len(query['files_queried'])) if m is not None and factor else None,'method':'Illustrative linear scenario only: observed matched parents * selected records / processed records *300 total WARC Parquet files /130 probed files; cap at universe size. Not a defensible statistical full-.no estimate.','limitations':['File order is not random; .no data may be clustered, so other-TLD zero files are not exchangeable sampling units.','No complete .no eligible-page/domain denominator was measured.','Distinct-company discovery saturates, two records per domain and limit20000 bias selection; missing parser outcomes further limit extrapolation.'],'recommended_interpretation':'Observed universe matches and expected per1000 describe this partial run only. More pages may add candidates or invalidate domains under the three-org rule; this is not a guaranteed lower bound or a forecast of verified websites.'}
 if s['extrapolation']['full_no_flat_file_linear_scenario'] is not None:s['extrapolation']['full_no_flat_file_expected_per_1000_scenario']=1000*s['extrapolation']['full_no_flat_file_linear_scenario']/n
 reviews=json.loads((OUT/'live-review.json').read_text(encoding='utf8')) if (OUT/'live-review.json').exists() else []
 requests=json.loads((OUT/'live-requests.json').read_text(encoding='utf8')) if (OUT/'live-requests.json').exists() else []
 last={};minimum=None
 for r in requests:
  h=urlsplit(r['url']).hostname;t=r['at_monotonic']
  if h in last:
   diff=t-last[h];assert diff>=1,(h,diff);minimum=diff if minimum is None else min(minimum,diff)
  last[h]=t
 for r in reviews:
  assert len(r['pages'])<=3
  for p in r['pages']:
   if p.get('body_sha256'):assert hashlib.sha256((OUT/'raw'/(p['body_sha256']+'.html')).read_bytes()).hexdigest()==p['body_sha256']
 selected=[json.loads(x) for x in (OUT/'raw/columnar-selected.jsonl').read_text(encoding='utf8').splitlines() if x.strip()]
 counts=collections.Counter(x['domain'] for x in selected);assert len(selected)<=20000 and max(counts.values(),default=0)<=2
 validation={'selected_index_records':len(selected),'selected_index_domains':len(counts),'max_selected_records_per_domain':max(counts.values(),default=0),'saved_live_request_count':len(requests),'minimum_observed_same_host_spacing_seconds':minimum,'maximum_pages_requested_per_site':max((len(x['pages']) for x in reviews),default=0),'live_body_hashes':'all passed','protected_code_and_dependencies':subprocess.check_output(['git','diff','abc33af','--name-only','--','src','tests','pyproject.toml','uv.lock'],cwd=ROOT,text=True).strip() or 'unchanged','main':subprocess.check_output(['git','rev-parse','main'],cwd=ROOT,text=True).strip(),'fix-large-company-site':subprocess.check_output(['git','rev-parse','fix-large-company-site'],cwd=ROOT,text=True).strip()}
 assert validation['protected_code_and_dependencies']=='unchanged'
 assert validation['main']=='abc33afc6f72258883da41478345b04784f30cb1';assert validation['fix-large-company-site']=='405eafccbd3d59df97121c337e6e90c03ea0f841'
 validation['proof_module_path']=str(Path(proof_module.__file__).resolve())
 validation['candidate_checks']='all orgnrs/parents mod-11 valid; snippets <=120 characters'
 validation['selected_index_sha256']=hashlib.sha256((OUT/'raw/columnar-selected.jsonl').read_bytes()).hexdigest()
 s['validation']=validation
 s['records_not_attempted']=max(0,s['records_selected']-attempted)
 s['parse_error_records']=sum(bool(x.get('compressed_bytes')) and 'error' in x for x in results.values())
 s['licence_notes']={'common_crawl':s['terms'],'brreg':'NLOD 2.0; credit Br\u00f8nn\u00f8ysundregistrene; cached official subunit bulk only.','universe':'Cached Builderr challenge input; no licence statement in JSONL, raw file not redistributed.','osm_comparison':'ODbL 1.0; \u00a9 OpenStreetMap contributors; existing candidates used only to compute overlap.'}
 s['parser_history']='210 early archive parse errors retained from before support for normalized HTTP encoding headers; later parsing uses the corrected measurement decoder. Failed parsing is not classified as no-orgnr evidence.'
 s['live_review']['outcomes']=dict(collections.Counter('proof_pass' if r['passes'] else 'transport_or_policy_unavailable' if not any(p.get('status')==200 for p in r['pages']) else 'no_accepted_proof_or_owner_conflict' for r in reviews))
 (OUT/'summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(OUT/'columnar-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
 print(json.dumps({k:s[k] for k in ['status','records_fetched','parsed_records','successful_warc_range_payload_MB','pages_with_orgnr','pairs','distinct_orgnrs','distinct_domains','universe','osm_overlap','bench100_match_count','live_review','extrapolation']},ensure_ascii=True,indent=2))
if __name__=='__main__':main()
