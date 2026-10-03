# Week 2: a structured-output extractor, measured

Copy this into your `DECISIONS.md` and fill it in.

---

## Week 2

**Run conditions.** model: qwen3:4b-instruct | temperature: 0.0 |
prompt version: `week02-zero-shot-v1` | served locally | date: 2026-08-10 |
scored on: my own machine (replay results are identified separately)

### 1. The output contract

The conventions I chose, and why:

- due_date, when the message states no date: `null`/`None`, because no calendar date was provided.
- due_date, when the message states only a relative expression: `null`/`None`; relative phrases such as "before the end of the month" are not converted into invented dates.
- quote, and what "verbatim" means in my scorer: a short span copied character for character from the source message; the scorer requires the returned string to occur as an exact substring and does not normalize, translate, paraphrase, or tidy it.
- what my scorer does with a record that failed validation: increments `invalid` and counts every field as wrong for that document.

Counting validation failures matters because silently skipping unparseable
records would make the score improve as the model gets worse.

### 2. Zero-shot, per field

| field | correct | of |
| category | 9 | 10 |
| urgency | 9 | 10 |
| due_date | 7 | 10 |
| quote | 8 | 10 |
| invalid records | 0 | 10 |

My prediction, written before block 3: examples will help most on `due_date`
because the zero-shot run invented dates when messages contained only
relative expressions or no date.

### 3. Few-shot

Examples chosen, and the job each one does:

| example | why it is in the block | field it should move |
| EX-02 French facilities request | Demonstrates the facilities-versus-access boundary and an urgent request in French. | category, urgency |
| EX-03 German laptop request | Demonstrates a hardware request, a stated European calendar date, and German input. | category, due_date |
| EX-04 English information-only message | Demonstrates that no action is an `info` request and has no due date. | urgency, due_date |
| EX-05 French billing request | Demonstrates billing classification and a calendar date in a French message. | category, due_date |

| field | zero-shot | few-shot | move |
| category | 9/10 | 9/10 | 0 |
| urgency | 9/10 | 10/10 | +1 |
| due_date | 7/10 | 9/10 | +2 |
| quote | 8/10 | 9/10 | +1 |

### 4. What got worse

No field got worse in the live run. I checked the per-field comparison and
the failure counts: urgency improved by one, due_date by two, and quote by
one, while category stayed at 9/10. The remaining category error was not
fixed; the other improvements represent errors disappearing rather than a
wrong label changing into another wrong label.

The replay fixture tells a different, deliberately simplified story: it
reports 10/10 for both variants and warns that it returns the reference
prompt's answers because the local prompt differs. I therefore treat replay
as scorer development evidence, not as a measurement of this prompt.

### 5. What the examples cost

- extra input tokens per call: 350
- per thousand calls: 350,000
- estimated euros per thousand calls on the small tier: 70.00 EUR, against the
  price list dated 2026-08-10. Estimate, not a measurement.

The estimate uses 350,000 additional input tokens at 0.20 EUR per million
tokens. The local run itself had no monetary charge.

### 6. Ship it or not

I would keep the few-shot variant for now: it improved urgency from 9/10 to
10/10, due_date from 7/10 to 9/10, and quote from 8/10 to 9/10 without
changing category, while adding 350 input tokens per call. Ten records are
not enough for confidence. I would change my mind if a larger held-out set
showed that the gains did not repeat, or if the added examples caused quote
copying errors or a meaningful latency or cost problem.

### Sensitivity variant

Variant assigned: `english_only`. What I changed: replaced the multilingual
few-shot examples with four English examples while keeping the example count.
What moved: category improved from 9/10 to 10/10 (+1), urgency stayed at
10/10, due_date fell from 9/10 to 7/10 (-2), and quote fell from 9/10 to
8/10 (-1). Field errors changed from 3 to 4 for English, 0 to 1 for French,
and remained 0 for German.

The English-only prompt was worse overall, so the multilingual examples are
the better choice. The language slices are small and cannot establish a
general language effect.

### The gold set

Ten cases were written to `artifacts/goldset.json`, tagged by language.

One thing my scorer cannot currently detect: it can verify that a quote is an
exact substring, but it cannot determine whether that substring genuinely
supports the urgency decision. The gold set also records the expected
category, urgency, and due date, not a gold quote span.

### Deferred

The non-replay `role`, `reordered`, and `no_delimiter` sensitivity variants
were not run in the supplied log. The `role` replay run showed no movement,
but replay is not a live measurement because the fixture uses its reference
answers.
