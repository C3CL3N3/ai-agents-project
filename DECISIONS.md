# Decisions

# Week 1: the stack, the first call, and what it costs

Copy this into your `DECISIONS.md` and fill it in. Keep the headings. In
week 13 this becomes a section of your project report that you do not have
to write.

---

## Week 1

**Run conditions.** Everything below was produced on:

- machine: Asus Zenbook; Intel Core Ultra 9 185H processor; 32 GB RAM; Intel Arc Graphics
- model: qwen3:4b-instruct
- served by: Ollama, one request at a time, locally
- date: 2026-09-17

Every number in this file is meaningless without those four lines, so they
are stated once here and referred to rather than repeated.

### 1. Machine and model set

I am running the required model set: `qwen3:4b-instruct`.

I did not yet run the optional models; I will pull them before week 9 when the vision work begins.

### 2. The first call

| | |
| finish reason | stop |
| prompt tokens | 24 |
| completion tokens | 45 |
| elapsed | 3.24730416400007 s |

Because the finish reason was `stop`, I treated the response as complete. If
it were a truncation, I would reject it as incomplete and retry or report the
failure rather than use it as a final answer.

The answer was: "To register a change of address, visit your local
government website or contact your municipal office to obtain the necessary
forms. Complete the form with your new address and submit it in person or by
mail, depending on your location."

### 3. Variance

| cell | distinct (recording) | distinct (mine) | median latency |
| closed_short, t=0.0 | 1/12 | 1/6 | 0.22 s |
| closed_short, t=1.0 | 1/12 | 1/6 | 0.20 s |
| open_list, t=0.0 | 1/12 | 1/6 | 2.69 s |
| open_list, t=1.0 | 11/12 | 6/6 | 2.52 s |

Which cell still returns a single answer at temperature 1.0, and why that one:

The `closed_short` cell still returns a single answer at temperature 1.0 because the prompt is tightly constrained and the answer is effectively fixed: the capital of Luxembourg is a single factual answer, so temperature does not create meaningful variation.

Which cells a test asserting exact string equality would pass on and what that tells me about testing this system:

Exact equality would pass reliably for `closed_short` at both temperatures and for `open_list, t=0.0` in these runs. It would not be reliable for `open_list, t=1.0`, where all six local outputs differed. This shows that tests should assert a structured contract or acceptable properties for open-ended output, not exact text unless the output is constrained.

**The sentence that carries into week 10.**
At temperature 0 the model repeated the same output across runs, but at temperature 1.0 open-ended prompts could still produce multiple valid answers, so exact string equality is reliable only when the output space is constrained.

### 4. The cold start

- cold call: 7.99 s
- warm call: 0.19 s
- ratio: 41.39x

What this implies for a system that uses more than one model, and what I will do about it:

The 41.39x difference means that loading a model can dominate request latency. This shows that switching models inside a single workflow imposes a large latency penalty because the first request must load the model from disk. For a system that needs more than one model, I would keep each model resident for the task it serves and avoid swapping models mid-request; I would route by task instead of reloading a different model each time.

### 5. Cost, estimated

A 200-case golden set, at the token cost of my long case:

| | one run | nightly for the semester |
| small tier | 0.03352 EUR | 3.29 EUR |
| large tier | 2.49120 EUR | 244.14 EUR |

Estimates against the price list dated 2026-08-10, not measurements. The long case used 38 input tokens and 200 output tokens per case; the semester estimate assumes 200 cases nightly for 7 nights per week over 14 weeks. Running locally, my actual monetary cost was zero.

I would run the small tier nightly because its estimated semester cost is low enough for repeated checks. I would run the large tier before a release when additional quality is worth the much higher cost. I would not use the large tier nightly because the recurring estimate is about 244.14 EUR versus 3.29 EUR for the small tier.

### Deferred

/

## Week 2

**Run conditions.** model: qwen3:4b-instruct | temperature: 0.0 |
prompt version: `week02-zero-shot-v1` | served locally | date: 2026-10-03 |
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
were not run on this machine.
