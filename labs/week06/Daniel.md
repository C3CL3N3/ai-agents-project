# Week 6 remaining executions

Run these commands on the other laptop. Do not run them on the project laptop.

## 1. Run the A2A channel

```bash
cd labs/week06/starter
python 04_a2a_channel.py
```

Record whether these four parts work:

- The agent card is discovered.
- The completed task returns a text artifact.
- The failed task returns a `failed` state.
- The slow task times out while keeping its task ID.
- The non-text artifact is reported as a mismatch.

If the output differs, update the A2A paragraph in
`DECISIONS.md`.

## 2. Measure the cost of `k`

Use the memory store with `k = 3`, then record the token count reported by the
model or tracing tool for one search call.

Replace this field in `DECISIONS.md`:

```text
[REPLACE WITH THE TOKEN COUNT FROM A MANUAL MEMORY RUN]
```

Record the number only if the run actually reports tokens. Do not estimate it.

## 3. Check the store with 400 facts

Create 400 facts for one subject and run a search with `k = 3`. Record:

- Whether the store remains usable.
- How many facts are returned.
- The search time, if it is reported.
- The token count added to the model context, if it is reported.

Replace this field in `DECISIONS.md`:

```text
[REPLACE WITH WHAT HAPPENED AT 400 FACTS]
```

The expected functional property is that no more than three facts are
returned. Replace that statement if the actual run shows a different result.

## 4. Compare memory off and memory on

Run the same task twice:

1. Once without storing or recalling facts.
2. Once with memory enabled and the relevant fact recalled.

Record the following for both runs:

| Mode | Tokens | Turns to finish |
| --- | ---: | ---: |
| Memory off | [record value] | [record value] |
| Memory on | [record value] | [record value] |

Replace the two rows in the Week 6 table in `DECISIONS.md`. Then replace the
sentence below the table with the result you observed:

- Did memory use more tokens?
- Did memory reduce the number of turns?
- Was the trade-off worth it for this task?

## 5. Run the project verifier

From the repository root, run:

```bash
python -m project.verify
```

Record whether it passes and note the reported case count. If it fails, copy
the exact error into your notes and fix the issue before marking Week 6 done.

## 6. Final checklist

- [ ] `04_a2a_channel.py` was run.
- [ ] The A2A result was checked against `DECISIONS.md`.
- [ ] The token cost for `k = 3` was recorded.
- [ ] The 400-fact behavior was recorded.
- [ ] Memory-off tokens and turns were recorded.
- [ ] Memory-on tokens and turns were recorded.
- [ ] The values in `DECISIONS.md` were replaced.
- [ ] `python -m project.verify` passed.
