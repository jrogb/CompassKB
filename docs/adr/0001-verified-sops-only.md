---
status: accepted
---

# Verified SOPs only, and the legacy copy is deleted at verification

SOPs currently live on a hosted Microsoft file server. They are disorganised to
the point that Admin Staff do not reference them at all — they ask a manager
instead. The documents are therefore not merely untidy but **unverified**:
because nobody has used them, nobody knows which ones still describe reality.

**Decision.** CompassKB will not answer from an SOP until a named Owner — the
manager whose expertise staff currently rely on — has confirmed it matches what
they would tell someone today. Verification records the Owner and the date. The
legacy copy is deleted at verification (not at capture), so that from that
moment exactly one copy of the SOP exists.

A **Captured** SOP is never surfaced to the person asking, not even with a
warning attached. Caveats are ignored by someone in a hurry who just wants the
GL account, so a caveated wrong answer is still a wrong answer that gets acted
on. Unverified documents are visible only to whoever runs Onboarding, as
prioritisation signal.

The reasoning is that CompassKB's only real asset is trust. An Admin Staff
member who is given a wrong procedure once will go back to asking their manager
and will not return, and a confidently-worded wrong answer about a GL account or
a tax default is worse than no answer, because it gets acted on. Requiring a
manager's signature converts the knowledge staff already trust into the
knowledge CompassKB serves, rather than hoping the old documents happen to be
right.

## Considered options

**Index everything now, verify later.** Rejected. It would give full coverage in
days instead of months, but CompassKB would launch by answering from exactly the
documents staff have already learned to distrust — reproducing the current
problem with a more authoritative-sounding interface.

This alternative will look attractive again once rollout feels slow, which is
why it is recorded here. Revisiting it should be a deliberate decision to trade
trust for coverage, not a quiet shortcut taken under delivery pressure.

## Consequences

- Rollout speed is rate-limited by manager attention, not by engineering. The
  onboarding workflow must therefore cost a manager an *approval*, not an
  *authorship* — whoever runs the migration interviews the manager and drafts
  the correction; the manager reads and signs.
- For an extended period CompassKB will not know most things. How it behaves
  when it cannot answer is a product-defining problem, not an edge case.
- Deleting the legacy copy is irreversible. It happens only after a named person
  has accepted accountability for the replacement.
