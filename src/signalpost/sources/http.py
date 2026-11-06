from ..workers import offload
import asyncio
import email.utils
import random
import time
from urllib.parse import urlsplit
from dataclasses import dataclass
import httpx
from ..budget import SourceFailure
from ..models.evidence import utc_now

ALLOWED_HOSTS = {"data.brreg.no"}


def allow(url):
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS or parts.username or parts.password or parts.port not in (None, 443):
        raise SourceFailure("url_refused", "Only HTTPS data.brreg.no:443 is permitted")
    return parts.hostname


@dataclass
class Response:
    body: bytes
    status: int
    url: str
    retrieved_at: str
    sha: str


class Http:
    def __init__(self, client, config, budget, blobs):
        self.client, self.config, self.budget, self.blobs = client, config, budget, blobs
        self.semaphores = {host: asyncio.Semaphore(config.host_concurrency) for host in ALLOWED_HOSTS}

    async def download_once(self,url,org,max_bytes=8*1024*1024):
        """One bounded official document request; no implicit retry."""
        host=allow(url);self.budget.check()
        async with self.semaphores[host]:
            event=self.budget.reserve(url,host,org);begin=time.monotonic()
            try:
                timeout=min(self.config.request_timeout,max(.001,self.budget.deadline-time.monotonic()))
                async with self.client.stream('GET',url,timeout=timeout,follow_redirects=False) as response:
                    event['status']=response.status_code
                    if response.is_redirect:raise SourceFailure('url_refused')
                    chunks=[];size=0
                    async for chunk in response.aiter_bytes():
                        self.budget.check();size+=len(chunk)
                        if size>max_bytes:raise SourceFailure('body_cap')
                        chunks.append(chunk)
                    body=b''.join(chunks)
                sha=await offload(self.blobs.put,body);event['content_sha256']=sha
                return Response(body,response.status_code,url,utc_now(),sha)
            except (httpx.HTTPError,SourceFailure) as exc:
                event['error']=getattr(exc,'code',type(exc).__name__)
                raise SourceFailure(getattr(exc,'code','network_error')) from exc
            finally:event['runtime_ms']=round((time.monotonic()-begin)*1000)

    async def get(self, url, org):
        host = allow(url)
        attempts = 3 if "/regnskapsregisteret/" in url else 2
        for attempt in range(attempts):
            self.budget.check()
            response = None
            async with self.semaphores[host]:
                event = self.budget.reserve(url, host, org)
                begin = time.monotonic()
                try:
                    timeout = min(self.config.request_timeout, max(0.001, self.budget.deadline - time.monotonic()))
                    response = await self.client.get(url, timeout=timeout, follow_redirects=False)
                    event["status"] = response.status_code
                    sha = await offload(self.blobs.put,response.content)
                    event["content_sha256"] = sha
                    result = Response(response.content, response.status_code, url, utc_now(), sha)
                    if response.is_redirect:
                        raise SourceFailure("url_refused", "Redirects are refused; target not requested")
                    if response.status_code not in {429, 500, 502, 503, 504} and response.status_code < 500:
                        return result
                    if attempt == attempts - 1:
                        return result
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    event["error"] = type(exc).__name__
                    if attempt == attempts - 1:
                        raise SourceFailure("timeout" if isinstance(exc, httpx.TimeoutException) else "network_error") from exc
                except asyncio.CancelledError:
                    event["error"] = "deadline"
                    raise
                finally:
                    event["runtime_ms"] = round((time.monotonic() - begin) * 1000)
            delay = random.uniform(0.1, 0.3) * (2 ** attempt)
            if response is not None:
                retry = response.headers.get("Retry-After")
                if retry:
                    try:
                        delay = max(delay, float(retry))
                    except ValueError:
                        try:
                            delay = max(delay, email.utils.parsedate_to_datetime(retry).timestamp() - time.time())
                        except (ValueError, TypeError, OverflowError):
                            pass
            if time.monotonic() + delay >= self.budget.deadline:
                raise SourceFailure("deadline")
            await asyncio.sleep(delay)
