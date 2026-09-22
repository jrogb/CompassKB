---
id: example-runbook
title: Example runbook
category: runbooks
status: draft
audiences: [operator]
tags: [incident]
owner: unassigned
created: 2026-01-01
updated: 2026-01-01
review_after: 2026-07-01
summary: Placeholder summary naming the failure this runbook resolves.
---

**Severity:** SEV-? · **Page the owner if:** (condition)

Written to be followed at 3am by someone who did not write it. Every step is an
action with a checkable outcome. No theory above the fold.

## Symptoms

What the operator is looking at that brought them here -- the alert name, the
error string, the graph shape. Make it greppable: paste the literal message.

## Diagnosis

Ordered checks that narrow the cause. Each step says what to run and what the
answer means.

1. Run: `...`
   - Expected: ...
   - If instead you see ...: go to [Remediation](#remediation), step 2.

## Remediation

Numbered, reversible where possible. Say explicitly which steps are destructive
and what they cost.

1. ...

## Verification

How you know it is actually fixed, not just quiet.

## Escalation

Who to wake, on which channel, and what to tell them. Include the information
they will ask for so it is gathered before the call.

## Aftermath

Follow-ups that are not required to stop the bleeding: the ticket to file, the
alert to tune, the article to update.
