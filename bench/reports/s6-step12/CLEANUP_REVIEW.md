# Step 12 cleanup: review of every addition

Saved Step 11 evidence only. Four new website links and three new social URLs: **7 correct, 0 wrong, 0 unsure**. Social availability increases by two companies because Control Solutions contributes two URLs. No social destinations were fetched. No company-specific runtime exceptions were introduced.

| Company / orgnr | Item | Verdict | Ownership / attribution |
|---|---|---|---|
| KN ELEKTRO AS / 823147112 | [https://knelektro.no](https://knelektro.no) | correct | Correct: exact KN Elektro AS identity plus registered Roresanden 109, 4885 Grimstad; Insite Media AS is explicitly credited as the website developer, not publisher. |
| KN ELEKTRO AS / 823147112 | [https://www.facebook.com/KN-Elektro-As-104194150969215](https://www.facebook.com/KN-Elektro-As-104194150969215) | correct | Correct: publisher metadata on the verified KN Elektro site nominates this company-named Facebook profile; it is not a share link or agency credit. |
| LOFOTPOSTEN AS / 968386085 | [https://www.lofotposten.no](https://www.lofotposten.no) | correct | Correct: footer explicitly says Utgitt av Lofotposten AS and the registry phone matches; generic publisher-prefix fix prevents the own publisher being treated as foreign. |
| CONTROL SOLUTIONS AS / 926490060 | [https://www.control-solutions.no](https://www.control-solutions.no) | correct | Correct: publisher footer shows own organisation number 926 490 060 and business contact/address; title CONTROL SOLUTION AS is a singular/plural spelling variant of registered CONTROL SOLUTIONS AS, with the same AS legal form. |
| CONTROL SOLUTIONS AS / 926490060 | [https://www.facebook.com/ControlSolutionsAS](https://www.facebook.com/ControlSolutionsAS) | correct | Correct: ControlSolutionsAS Facebook link appears in the header of the own-orgnr-verified site and matches the legal name. |
| CONTROL SOLUTIONS AS / 926490060 | [https://www.instagram.com/control_solution_as](https://www.instagram.com/control_solution_as) | correct | Correct: control_solution_as Instagram link is in the same verified header and matches the declared singular brand/title spelling. |
| GS ELEKTRO GJØVIK AS / 995445611 | [https://gsel.no](https://gsel.no) | correct | Correct: footer explicitly names GS Elektro Gj?vik AS and own organisation number 995 445 611; split GS ELEKTRO / GJ?VIK AS HTML nodes form the complete publisher identity. Registry output remains unchanged. |

Proof excerpts, retrieval dates, source URLs and exact SHA-256: [cleanup-new-items.json](cleanup-new-items.json). The affected four complete company outputs passed the independent schema/evidence/synthesis verifier: 552 claims, 23 source blobs and 47 cited sentences; zero unverified values.

No prior published claim ID was removed from the incremental saved-snapshot projection. Existing Wikidata socials are retained, because the real runner emits them after website collection; calling the collector helper alone must not erase them.
