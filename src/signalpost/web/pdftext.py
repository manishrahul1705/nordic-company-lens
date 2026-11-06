"""Isolated, text-only PDF nomination extraction. No OCR and no ownership proof."""
import io
import json
import re
import sys
import time
from .policy import domain,normalize_url,FREE_MAIL,SOCIAL,DIRECTORIES


def domains(text):
    result=[]
    pattern=r'(?:https?://|www\.)[a-zA-Z0-9æøåÆØÅ.-]+|[\w.+-]+@([a-zA-Z0-9æøåÆØÅ.-]+\.[a-zA-Z]{2,})|\b(?:[a-zA-Z0-9-]+\.)+(?:no|com|net|org|eu|io)\b'
    for match in re.finditer(pattern,text):
        value=match.group(1) or match.group().rstrip('.,;)')
        host=domain(normalize_url(value) or '')
        if host and host not in FREE_MAIL|SOCIAL|DIRECTORIES|{'brreg.no','nav.no','w3.org','xbrl.org','ifrs.org','schema.org'} and host not in result:result.append(host)
        if len(result)==6:break
    return result


def extract(body):
    from pypdf import PdfReader
    if not body.startswith(b'%PDF') or len(body)>8*1024*1024:return {'state':'not_pdf_or_size_cap','domains':[]}
    try:
        reader=PdfReader(io.BytesIO(body),strict=False)
        if reader.is_encrypted or len(reader.pages)>100:return {'state':'encrypted_or_page_cap','domains':[]}
        started=time.monotonic();parts=[]
        for page in reader.pages:
            if time.monotonic()-started>6:return {'state':'parse_timeout','domains':[]}
            text=page.extract_text() or '';parts.append(text)
        text='\n'.join(parts)
        return {'state':'text' if len(text.strip())>=30 else 'scanned_or_empty','text_characters':len(text),'domains':domains(text) if len(text.strip())>=30 else []}
    except Exception:return {'state':'unreadable_pdf','domains':[]}


if __name__=='__main__':
    print(json.dumps(extract(sys.stdin.buffer.read(8*1024*1024+1))))
