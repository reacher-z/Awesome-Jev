## Change

Describe the change and its relevance to Jev, typed decisions, or their research foundations.

## Evidence

Link canonical public sources. State dates or versions, what was checked, and material limitations. For code or presentation-only changes, write “No sources added” and describe validation.

## Checklist

- [ ] I linked canonical public sources (or marked this change as not adding sources).
- [ ] I stated the verification level and relevant limitations.
- [ ] I included dates or versions for changing claims.
- [ ] I checked for credentials, private paths, and unlicensed assets.
- [ ] I ran the checks in CONTRIBUTING.md (`python3 -m unittest discover -s tests`, `python3 scripts/validate.py`, `node scripts/build_site.mjs --check`, `python3 scripts/build_source_index.py --check`) and committed any regenerated site pages or source index.

The automated PR comment performs deterministic provenance and hygiene checks. It is not a human review or a scientific verdict; maintainers decide whether to merge.
