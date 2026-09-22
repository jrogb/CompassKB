# Style guide

How CompassKB articles are written. Structure and metadata rules live in
[`front-matter.md`](front-matter.md); this file is about the prose.

## Answer first

Open with what is true. A reader who stops after the first paragraph should not
be misled. Background goes after the answer, or in a `concepts` page that the
article links to.

Do not open with "In this article we will..." — the reader knows where they are.

## Write for someone under pressure

Assume the reader is interrupted, skimming, and slightly annoyed. That means:

- Short paragraphs. One idea each.
- Descriptive H2 headings — they are both navigation and the retrieval chunk
  boundary. `## Rotating without downtime`, never `## Notes` or `## Part 2`.
- Lists for steps and options; prose for reasoning. Not the reverse.
- The important caveat goes *before* the step it applies to, not after.

## Be specific enough to be wrong

Every factual claim should be checkable by a reader who doubts it.

| Instead of | Write |
|---|---|
| "Keys expire fairly quickly." | "Keys expire 90 days after creation." |
| "Contact the platform team." | "Post in `#platform-oncall`; page `platform-oncall` for SEV-1." |
| "This may take a while." | "Typically 2–5 minutes; longer than 15 means it is stuck." |
| "Recent versions support this." | "Supported from v4.2 (2026-03)." |

Vague writing is unfalsifiable, which means it can never be found wrong and
never gets fixed.

## Date anything that will drift

Version numbers, limits, prices, org names, and UI labels all rot. Anchor them:
"as of 2026-09", "gateway default". This tells the next reader what to re-check
and makes `review_after` actionable.

## Use the reader's words

If tickets say "my key stopped working", the article must contain that phrasing
somewhere, even though internally it is "credential expiry". Findability is part
of correctness — an article nobody reaches is not published in any useful sense.
Where the reader's phrasing genuinely does not belong in the prose, put it in
`keywords`.

## Voice

- Second person for instructions: "Run `...`", "You will see...".
- Present tense. "The gateway rejects the request", not "will reject".
- Active voice when someone is responsible: "The gateway rejects it", not
  "it is rejected".
- No hedging as a substitute for research. "Probably", "should generally",
  "in most cases" are only acceptable when the uncertainty is real — and then
  say what determines it.

## Formatting

- `code` for anything typed literally: commands, fields, file paths, values.
- Bold for the word a skimmer must not miss. Never for emphasis in general.
- Tables when there are three or more parallel items with the same attributes.
- Fenced code blocks with a language tag. Show the command *and* what success
  looks like.
- Relative links between articles (`../guides/other.md`) — the validator checks
  them, absolute URLs to internal pages break silently.

## Destructive and risky steps

Any step that deletes, restarts, or cannot be undone gets an explicit warning
immediately above it, saying what it costs and how to get back. Runbooks are
followed at 3am by someone who did not write them.

## What not to write

- No credentials, tokens, keys, internal hostnames, customer data, or personal
  information — including in examples.
- No pasted third-party documentation. Summarise and link.
- No apologising for the docs ("sorry, this is confusing"). Fix it instead.
- No jokes that a reader mid-incident has to parse.
