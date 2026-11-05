# Step 6 measured variance

Two sequential unchanged 1000-company runs on main 2351e57, both proof flags OFF, identical frozen inputs and clean production code. This is an observed difference from two runs, not a statistical confidence interval.

| Section | Run A | Run B | B minus A | Absolute noise band |
|---|---:|---:|---:|---:|
| identity | 1000 | 1000 | 0 | 0 |
| people | 997 | 997 | 0 | 0 |
| locations | 774 | 774 | 0 | 0 |
| financials | 999 | 999 | 0 | 0 |
| website | 59 | 57 | -2 | 2 |
| social | 30 | 26 | -4 | 4 |
| jobs | 3 | 3 | 0 | 0 |
| news/activity | 230 | 231 | 1 | 1 |

Gate interpretation: compare later runs with the higher baseline count for each section. A drop is exempt only if its size is within the observed absolute band AND each lost company has a recorded transient failure outside the changed rule. NXDOMAIN, owner conflicts, robots/4xx, and request-cap exhaustion are not automatically transient. Website membership churn is reported separately from net count variance.

| Company / org | A website | B website | Failure on the successful site domain in the other run |
|---|---|---|---|
| CONPLAN AS / 987895276 | - | https://www.conplan.no | dns_timeout; dns_unavailable |
| ARKIDAL AS / 934982762 | - | https://www.arkidal.no | dns_timeout; dns_unavailable |
| ENSURE IT AS / 934620011 | https://www.ensure-it.eu | https://ensure-it.eu | Authority changed only |
| HARVELAND AS / 942393679 | https://harveland-as.no | - | dns_unavailable |
| THE LAB RETRIEVER AS / 926065173 | - | https://thelabretriever.com | dns_unavailable |
| OSLO CHAMBER OF COMMERCE / 938092516 | - | https://chamber.no | dns_timeout; no_such_domain |
| ELEKTROKOMPETANSE AS / 989916319 | - | https://elektrokompetanse.com | dns_unavailable |
| FEIE- OG TILSYNSTJENESTER AS / 993919675 | https://www.tilsyn.no | - | dns_timeout; website_timeout |
| TAKST MÅLENG AS / 995654539 | https://www.takstmaaleng.no | - | dns_unavailable |
| TANGERIN AS / 989145509 | https://www.tangerin.no | - | website_timeout |
| PLUMP AS / 930166030 | https://plump.no | - | dns_timeout; website_timeout |
| ALFA LAGERHOTELL AS / 992868775 | https://alfalagerhotell.no | - | dns_unavailable |
| CL BYGG & EIENDOM AS / 917283109 | https://clbygg.no | - | dns_unavailable |
| MAN WITH A PLAN AS / 931613294 | https://mwap.no | - | Authority changed only |
| ANTISINK AS / 918486666 | https://www.antisink.no | - | dns_unavailable |
| IDESTOVA AS / 982388449 | https://idestova.no | - | no_such_domain; website_timeout |
| LARSZACHARIASSEN AS / 920358411 | https://larszachariassen.no | - | no_such_domain; website_timeout |
| EIMEALT AS / 912667758 | https://eimealt.no | - | no_such_domain; website_timeout |
| NUVE AS / 936094112 | https://nuve.no | - | no_such_domain; website_timeout |
| LAKSESYSTEMER AS / 821962242 | https://laksesystemer.no | - | no_such_domain |
| LEFDAL INSTALLASJON AS / 968545337 | https://lefdal.no | - | dns_timeout; dns_unavailable; website_timeout |
| ECOFRIC AS / 924828099 | - | https://www.ecofric.com | dns_unavailable; website_budget_exhausted; website_timeout |
| BRIDGE TECHNOLOGIES CO AS / 987002808 | https://bridgetech.tv | - | no_such_domain |
| D-PRODUCTION AS / 935861144 | https://www.d-production.no | - | dns_timeout; no_such_domain; website_timeout |
| VS ELEMENT AS / 976758218 | https://vselement.no | - | no_such_domain |
| TECTRAP AS / 920542158 | - | https://www.tectrap.com | dns_unavailable |
| BIKE2WORK AS / 921596154 | - | https://bike2work.no | dns_unavailable |
| STYREGUIDEN AS / 988456292 | - | https://styreguiden.no | dns_unavailable |
| GS ELEKTRO GJØVIK AS / 995445611 | - | https://gsel.no | dns_timeout; dns_unavailable |
| BERGEN VAKTMESTERTJENESTER AS / 990412375 | - | https://bnv.no | dns_unavailable |
| HETLY FRITID AS / 995520982 | - | https://kanobutikken.no | dns_timeout; website_timeout |
| HYGGE TANNHELSE AS / 927152630 | - | https://www.hyggetannhelse.no | dns_unavailable; website_timeout |
| WULLUM EIENDOM AS / 818807562 | - | https://wullumeiendom.no | dns_unavailable |
| NORDRE FOLLO RENSEANLEGG IKS / 971521570 | - | https://nfra.no | dns_timeout; website_timeout |
| SAGA REGNSKAP OG RÅDGIVNING AS / 939725709 | - | https://sagarr.no | website_timeout |
