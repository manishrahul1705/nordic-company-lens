from ..workers import offload
from ..models.synthesis import Synthesis,Generator,Unknown
from ..models.evidence import digest
from .template import generate


class Service:
    def __init__(self):
        self.metrics={'calls':0,'cache_hits':0,'input_tokens':0,'output_tokens':0,'estimated_usd':0,'fallbacks':0}

    async def summarize(self,envelope):
        try:base=await offload(generate,envelope)
        except Exception:
            result=Synthesis(generator=Generator(input_sha256=digest([envelope.organisation_number,'template_error'])))
            result.checks.fallback_used=True
            result.checks.rejections=[{'section':'synthesis','reason':'template_generation_error'}]
            result.sections.unknowns=[Unknown(family='synthesis',state='failed',reason='Summary generation could not be completed; source results remain available.')]
            self.metrics['fallbacks']+=1
            return result
        return base
