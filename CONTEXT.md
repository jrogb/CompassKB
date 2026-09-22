# CompassKB

The knowledge system used by the Admin Company's staff to answer "what is the
correct procedure here?" without having to ask a manager.

## Language

### Organisation

**Group**:
The set of companies whose administration is performed centrally — eight
transport, eight property, two investment, and the Admin Company itself.
_Avoid_: the business, the company

**Operating Company**:
A company in the Group whose finance and administration is performed on its
behalf by the Admin Company.
_Avoid_: entity, subsidiary, opco

**Admin Company**:
The single company in the Group whose staff perform finance and administration
for every Operating Company.
_Avoid_: head office, shared services, admin department

**Admin Staff**:
An employee of the Admin Company who performs administrative work on behalf of
one or more Operating Companies. Every CompassKB user is Admin Staff.
_Avoid_: user, clerk, operator

### Knowledge

**SOP**:
A document describing the correct way to perform a recurring administrative
task.
_Avoid_: procedure document, work instruction, process doc, policy

**Tacit Knowledge**:
Procedural knowledge held by a manager and transmitted verbally, which no
current SOP correctly records.
_Avoid_: tribal knowledge, institutional knowledge

**Owner**:
The manager who is accountable for an SOP being correct, and whose expertise
Admin Staff would otherwise have consulted directly.
_Avoid_: author, approver, maintainer, subject matter expert

**Onboarding**:
The workflow that takes a single SOP off the legacy file server, captures what
its Owner actually does today, and ends with a verified SOP and no legacy copy.
_Avoid_: migration, import, ingestion

**Knowledge Gap**:
A question CompassKB could not answer from a Verified SOP, recorded so that
Onboarding is prioritised by what Admin Staff actually ask.
_Avoid_: miss, unanswered query, unknown

**Seed Map**:
The mapping of subject areas to Owners, established before any SOP is Verified,
which lets CompassKB name who to ask while it still knows nothing.
_Avoid_: ownership matrix, routing table

### SOP lifecycle

**Captured**:
An SOP that has been taken off the legacy file server but whose Owner has not
yet confirmed it. CompassKB knows it exists and will not answer from it.

**Verified**:
An SOP whose Owner has confirmed it describes what they would tell someone
today. Only Verified SOPs are answerable.
_Avoid_: approved, published, live

**Stale**:
A Verified SOP past its review date. Still answerable, but every answer drawn
from it says so.

## Relationships

- The **Admin Company** performs administration for every **Operating Company**
- **Admin Staff** are employed by the **Admin Company** and act on behalf of
  **Operating Companies**
- An **SOP** describes a task performed by **Admin Staff**
- Today, **Tacit Knowledge** is trusted by **Admin Staff** and **SOPs** are not
- **Onboarding** converts one Owner's **Tacit Knowledge** into a **Verified** SOP
- Every **SOP** has exactly one **Owner**; an **Owner** holds many **SOPs**
- An SOP moves **Captured** → **Verified** → **Stale**, and is only answerable
  from **Verified** onwards
- A **Knowledge Gap** is attributed to an **Owner** via the **Seed Map**
- **Knowledge Gaps** prioritise which SOP is **Onboarded** next

## Example dialogue

> **Dev:** "Jane asks how to raise a purchase order for a supplier. We have an
> SOP for it on the file server — can CompassKB answer?"
>
> **Domain expert:** "Not from that. It's **Captured** at best. Nobody's looked
> at it in years."
>
> **Dev:** "So what makes it answerable?"
>
> **Domain expert:** "Her manager is the **Owner**. When he's read it and said
> 'yes, that's what I'd tell her', it's **Verified** — and then we delete the
> copy on the old server so there's only one."
>
> **Dev:** "And if he verified it two years ago?"
>
> **Domain expert:** "Then it's **Stale**. She still gets the answer, but she
> gets told it's overdue for review."
>
> **Dev:** "And if there's no SOP for it at all?"
>
> **Domain expert:** "Then it's a **Knowledge Gap**. She gets told it's Derek's
> area — the **Seed Map** knows that much — and we log it. Enough people ask,
> that SOP gets **Onboarded** next."

## Flagged ambiguities

- "SOP" was used to mean both the stale documents on the legacy file server and
  the verified procedures CompassKB serves — resolved: those are the **Captured**
  and **Verified** states of the same SOP, and only the latter is answerable.
