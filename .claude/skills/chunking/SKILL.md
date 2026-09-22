---
name: chunking
description: How CompassKB splits articles into retrieval chunks, and how to write or restructure an article so its chunks stand alone. Use when tuning build_index.py, when chunk stats look wrong, or when a correct article keeps returning unhelpful fragments.
---

# Chunking and the retrieval export

`scripts/build_index.py` turns articles into chunks:

1. Only statuses marked `indexed: true` in `taxonomy/statuses.yml` are exported.
   Drafts and archived pages never reach an index.
2. The body splits on **H2 headings** — one section, one chunk.
3. A section over `--max-words` (default 350) splits again on paragraph
   boundaries, with `--overlap-words` (default 50) carried across the seam.
4. Every chunk is prefixed with the article's **title and summary**, so a chunk
   retrieved alone still says what document it belongs to.

```bash
python3 scripts/build_index.py --stats           # size distribution, by category
python3 scripts/build_index.py --out -           # inspect the actual JSONL
```

## The rule this implies for writers

**An H2 section is the unit that gets retrieved, so each one must make sense
with nothing above it.** That is a writing constraint, not a tooling detail:

- Give sections descriptive headings. `## Rotating without downtime` retrieves
  well; `## Notes`, `## Details`, `## Part 2` retrieve as anonymous fragments.
- Do not let a section depend on an unstated antecedent. A section opening with
  "This only works if you did the above" is useless as a standalone chunk —
  name the precondition.
- Define a term in the section that uses it, or link to the definition. Do not
  rely on having defined it four sections earlier.
- Keep procedures whole. A numbered list split across a chunk boundary produces
  a chunk of steps 4–7 with no goal attached. If a procedure runs long, give it
  its own H2 rather than letting it overflow.

## Reading `--stats`

| Symptom | Likely cause | Fix |
|---|---|---|
| Many chunks under ~40 words | Over-sectioned article; H2s used for one-liners | Merge sections, or demote them to H3 (H3 does not split) |
| Chunks pinned at max-words | Long sections splitting mechanically mid-argument | Add real H2 boundaries where the topic actually turns |
| One article dominating chunk count | Page covers too much | Split it into separate articles |
| Chunk count jumps after an edit | Headings changed | Expected — but re-run `run_evals.py`, ranks will have moved |

## Changing the parameters

Defaults live in `build_index.py` (`DEFAULT_MAX_WORDS`, `DEFAULT_OVERLAP_WORDS`).
Before changing them, get a baseline:

```bash
python3 scripts/run_evals.py --k 5 --verbose > /tmp/before.txt
# change the defaults
python3 scripts/run_evals.py --k 5 --verbose > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt
```

Report the recall and MRR from both runs in the PR. A parameter change with no
measurement is a guess, and it moves every ranking in the KB at once.

Bigger chunks give more context per hit and blur what the hit is about; smaller
chunks are sharper but lose the surrounding argument. Prefer fixing the article
— chunking parameters are a blunt instrument applied to every page equally, and
most "bad chunk" complaints are one badly structured article.

## Note on `content_hash`

Each chunk carries a `content_hash`. Downstream indexers use it to skip
re-embedding unchanged chunks. Anything that changes the title or summary
rehashes **every** chunk in that article by design — the prefix is part of the
embedded text. Expect a full re-embed of an article after a title edit.
