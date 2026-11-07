from pathlib import Path
from html.parser import HTMLParser
import re,json
class Visible(HTMLParser):
 def __init__(self):super().__init__();self.raw=0;self.body=False;self.text=[]
 def handle_starttag(self,t,a):
  if t=='body':self.body=True
  if t in {'script','style'}:self.raw+=1
 def handle_endtag(self,t):
  if t in {'script','style'}:self.raw-=1
  if t=='body':self.body=False
 def handle_data(self,s):
  if self.body and not self.raw:self.text.append(s)
root=Path(r'C:\Users\Manish\Downloads\agent-site-new\site');bad=[];count=0
for f in root.rglob('*.html'):
 p=Visible();p.feed(f.read_text(encoding='utf-8'));text=' '.join(p.text);hits=[text[max(0,m.start()-35):m.end()+35] for m in re.finditer(r'T\d\d:\d\d',text)]
 if hits:bad.append({'file':str(f.relative_to(root)),'hits':hits[:4]})
 count+=1
 if count%250==0:print('Scanned',count,flush=True)
result={'html_pages_scanned':count,'pages_with_iso_timestamp_text':len(bad),'examples':bad[:20]};Path('bench/reports/offline-polish/timestamp-scan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
