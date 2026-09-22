## What changed for the reader

<!-- The new answer, not the diff. What will someone now find that they could
     not before, or what were they previously told that was wrong? -->

## How I know it is true

<!-- A person, a ticket, a command you ran, code you read, a date.
     "Confirmed with the platform team on 2026-09-18" is a source.
     "Seems right" is not. Required for anything touching content/. -->

## What I deliberately left out

<!-- Scope you chose not to cover, so the reviewer does not report it as a gap. -->

## Checks

- [ ] `python3 scripts/validate.py --strict` passes
- [ ] `python3 -m pytest tests/ -q` passes
- [ ] New articles have an eval case in `evals/queries/` using a real phrasing
- [ ] No credentials, customer data, internal hostnames, or personal information
- [ ] Any new taxonomy term is justified below and ships with the article that needs it

<!-- If this changes a previously published answer, say so explicitly here:
     someone acted on the old one. It also needs a CHANGELOG entry under
     `Corrected`. -->
