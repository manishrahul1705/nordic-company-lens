"""Reviewer explanations written after inspecting the ten candidates per type.

These are case-specific judgments, not a generated claim acceptance rule.
write_review.py verifies that the final measured values still match the inspected
values before applying these notes to final evidence records.
"""
NOTES = {
 'group_structure': {
  '991247610': 'The node identifies ROLIDBAKKEN itself as 991247610 and explicitly names SFR BARNEHAGER AS, 938641862, as its parent. The higher SFR HOLDING root and sibling nurseries are excluded.',
  '935327423': 'The EDSVIK node names ADVOKATFIRMAET SKOG AS, 934152530, in parentNavn/parentOrganisasjonsnummer. The relationship is stated, rather than guessed from the company names.',
  '879309182': 'The node at children/163 is explicitly KV 2 EIENDOM, 879309182, and names AKA AS, 919513195, as parent. Position 163 is a locator, not the basis for the relationship.',
  '928657523': 'VIVIFY GRUPPEN, 928657523, explicitly reports VIVIFY HOLDING AS, 928652750, as parent. Similar names alone were not used as evidence.',
  '994919482': 'The requested bakery node explicitly names BAKERMESTER KLAUSEN GRUPPEN AS, 998060486, as parent. The nested tree root is not substituted for this direct parent.',
  '981508734': 'KLEVEN MARITIME CONTRACTING AS, 992145501, explicitly has parentOrganisasjonsnummer=981508734 and parentNavn=MYKLEBUST MARITIME AS in MYKLEBUST\'s own lookup. This supports a registered direct subsidiary.',
  '882749762': 'NOTECH AS, 957503365, explicitly names NOTEK HOLDING AS, 882749762, as parent in NOTEK\'s lookup. The different spelling is retained exactly; no name-based identity inference is needed.',
  '922069212': 'KARLSEN BEGRAVELSESBYRÅ AS, 922388172, explicitly names KARLSEN AS, 922069212, as parent in the requested company\'s lookup.',
  '921678851': 'FS MANAGEMENT AS, 930469009, explicitly has parentOrganisasjonsnummer=921678851 and parentNavn=H1 CAPITAL AS in H1\'s own registry lookup.',
  '935955033': 'RANA ENTREPRENØR AS, 950271728, explicitly names ELLINGSEN HOLDING AS, 935955033, as parent in ELLINGSEN\'s lookup. The registered date and literal 100 % basis are preserved.',
 },
 'signatur': {
  '912823970': 'The own-company registered basis lists Arne-Johan Nikolaisen and Volker Wolframm with SIFE, and preserves both sentences: chair alone; managing director and chair jointly. It does not flatten the two people into independent signers or resolve away the registered alternatives.',
  '918049215': 'The registered text requires two board members jointly. The claim retains the number two and joint condition, without inventing an individually authorized person.',
  '919948493': 'The own-company registered basis names Sergio Felisberto Quilambo with SIGN and explicitly states Daglig leder alene. Both the named basis and the alone condition are retained.',
  '982410851': 'The registered text permits the managing director and chair each separately. Hver for seg is preserved, rather than changed into a joint-signature requirement.',
  '981508734': 'The complete text retains chair alone OR two board members jointly, including the requirement that at least one is shareholder-elected. No condition is dropped.',
  '916049153': 'The own-company basis explicitly states Styrets leder alene. The claim reports the registered role wording without inferring the holder from an ordinary role appointment.',
  '882749762': 'The own-company basis explicitly states Styrets leder alene. It is a registered signing declaration, not an inference from NOTEK\'s board record.',
  '936276075': 'The registered text requires two board members jointly. Both the count and joint requirement are retained verbatim.',
  '936312055': 'The basis explicitly states that board members sign each separately. The claim preserves each separately rather than assuming the board must act jointly.',
  '995541432': 'The registered wording requires one board member jointly with the chair OR managing director. Both the joint requirement and the alternative partner are preserved.',
 },
 'prokura': {
  '912823970': 'The registered basis names Arne-Johan Nikolaisen and Volker Wolframm with POHV, and states chair and deputy chair each separately. This is procuration from the prokura endpoint, distinct from the company\'s joint signature basis.',
  '919948493': 'The own-company procuration basis names Sergio Felisberto Quilambo with PROK and explicitly states Daglig leder alene. The claim retains both pieces of registered evidence.',
  '936312055': 'The prokura record explicitly says Styrets medlemmer hver for seg. This role-based wording is retained without adding names from a separate board record.',
  '919653477': 'The registered person-role basis names Håvard Hauge with PROK. No alone or joint condition is invented where the registered basis supplies no additional free text.',
  '919038438': 'The prokura basis explicitly states Daglig leder alene. The claim does not infer a named managing director from ordinary role appointments.',
  '921338732': 'The own-company prokura record explicitly requires two board members jointly. The unusual-looking grant is supported by this record itself; it is not replaced by an assumed standard rule for a housing cooperative.',
  '915707238': 'The own-company prokura basis explicitly states Daglig leder alene, and the published value preserves exactly that registered authority wording.',
  '924061847': 'The registered prokura basis explicitly states Styrets leder alene. The claim reports the registered role-level grant rather than naming a person by inference.',
  '922069212': 'The own-company prokura basis states Styrets medlemmer hver for seg. The each-separately condition is preserved, and no individual board list is substituted.',
  '987454709': 'The prokura basis explicitly states Daglig leder alene. The claim retains that exact declaration from the requested company\'s record.',
 },
}
