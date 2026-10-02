# Decisions

## Week 1

**Run conditions.** Everything below was produced on:

- machine: 14-inch MacBook Pro (2021), Apple M1 Pro chip with an 8-core CPU 14-core GPU, 16GB RAM
- model: qwen3:4b-instruct
- served by: Ollama, one request at a time, locally
- date: 2026-09-17

Every number in this file is meaningless without those four lines, so they
are stated once here and referred to rather than repeated.

### 1. Machine and model set

I am running the required model set.

I did not yet run the optional models; I will pull them before week 9 when the vision work begins.

### 2. The first call

```
Answer: To register a change of address, visit your local government website or contact your municipal office to obtain the necessary forms. Complete the form with your new address and submit it in person or by mail, depending on local requirements.
Finish reason: stop
Prompt tokens: 24, Completion tokens: 45
Elapsed time: 4.341789083999174
0.04 EUR per thousand calls on the small tier (24 in, 45 out per call), price list of 2026-08-10. Estimate, not a measurement.
```

| | |
| finish reason | stop |
| prompt tokens | 24 |
| completion tokens | 45 |
| elapsed | 4.341789083999174 |

One sentence on the finish reason: what my program would do differently if
it came back as a truncation rather than a normal stop.

If the finish reason were "length" instead of "stop", I would treat the answer as truncated and reject it as incomplete instead of assuming it was a valid final response.

### 3. Variance

| cell | distinct (recording) | distinct (mine) | median latency |
| closed_short, t=0.0 | 1/12 | 1/6 | 0.08 s |
| closed_short, t=1.0 | 1/12 | 1/6 | 0.08 s |
| open_short, t=0.0 | 1/12 | 1/6 | 1.07 s |
| open_short, t=1.0 | 5/12 | 6/6 | 1.07 s |
| open_list, t=0.0 | 1/12 | 1/6 | 0.92 s |
| open_list, t=1.0 | 11/12 | 6/6 | 0.89 s |
| open_reasoning, t=0.0 | 1/12 | not run | 5.41 s |
| open_reasoning, t=1.0 | 12/12 | not run | 5.41 s |

Which cell still returns a single answer at temperature 1.0, and why that
one:

The closed_short cell still returns a single answer at temperature 1.0 because the prompt is tightly constrained and the answer is effectively fixed: the capital of Luxembourg is a single factual answer, so temperature does not create meaningful variation.

Which cells a test asserting exact string equality would pass on, and what
that tells me about testing this system:

A test asserting exact string equality would pass on closed_short, t=0.0, closed_short, t=1.0, and open_short, t=0.0, and it would fail on open_short, t=1.0, open_list, t=1.0, and open_reasoning, t=1.0. This tells me that exact string matching is only reliable when the output is constrained and deterministic; open-ended prompts at temperature 1.0 can legitimately produce different valid answers.

**The sentence that carries into week 10.** At temperature 0 the model repeated the same output across runs, but at temperature 1.0 open-ended prompts could still produce multiple valid answers, so exact string equality is reliable only when the output space is constrained.

### 4. The cold start

- cold call: 1.29 s
- warm call: 0.09 s
- ratio: 14.26x

What this implies for a system that uses more than one model, and what I
will do about it:

This shows that switching models inside a single workflow imposes a large latency penalty because the first request must load the model from disk. For a system that needs more than one model, I would keep each model resident for the task it serves and avoid swapping models mid-request; I would route by task instead of reloading a different model each time. Cold/warm ratio: 1.29 s / 0.09 s = 14.26x.

### 5. Cost, estimated

A 200-case golden set, at the token cost of my long case:

| | one run | nightly for the semester |
| small tier | 0.00017 EUR | 3.29 EUR |
| large tier | 0.01246 EUR | 244.14 EUR |

Computation: long case = 38 in, 200 out. Small = (38/1e6 _ 0.20) + (200/1e6 _ 0.80) = 0.000168 EUR/run; semester = 0.000168 _ 200 _ 7 _ 14 = 3.29 EUR. Large = (38/1e6 _ 12.00) + (200/1e6 _ 60.00) = 0.012456 EUR/run; semester = 0.012456 _ 200 _ 7 _ 14 = 244.14 EUR.

Estimates against the price list dated 2026-08-10, not measurements. Running locally, my actual monetary cost was zero.

Which tier I would run nightly, which I would run before a release, and why
not the same one for both:

I would run the small tier nightly because it is cheap enough for repeated checks, and I would run the large tier before a release when output quality matters more than the additional cost. I would not use the same tier for both because the trade-off is between cost efficiency and model capability.

### Deferred

I did not yet run the full eight-cell variance sweep on my own machine because the homework extension was still in progress at the time of the week 1 checkpoint; the two live cells and the replay comparison were sufficient to complete the required analysis for this week.

## Week 2

**Run conditions.** model: [ ] | temperature: 0.0 | prompt version: [ ] |
served locally | date: [YYYY-MM-DD] | scored on: [the recording / my own
machine]

### 1. The output contract

The conventions I chose, and why:

- due_date, when the message states no date: [ ]
- due_date, when the message states only a relative expression: [ ]
- quote, and what "verbatim" means in my scorer: [ ]
- what my scorer does with a record that failed validation: [ ]

[One sentence on why the last one matters. A scorer that skips the records
it could not parse reports a number that improves as the model gets worse.]

### 2. Zero-shot, per field

| field | correct | of |
| category | | 10 |
| urgency | | 10 |
| due_date | | 10 |
| quote | | 10 |
| invalid records | | 10 |

My prediction, written before block 3: examples will help most on [ ]
because [ ].

### 3. Few-shot

Examples chosen, and the job each one does:

| example | why it is in the block | field it should move |
| | | |
| | | |
| | | |

| field | zero-shot | few-shot | move |
| category | 9/10 | 9/10 | 0 |
| urgency | 10/10 | 10/10 | 0 |
| due_date | 7/10 | 7/10 | 0 |
| quote | 10/10 | 8/10 | -2 |

### 4. What got worse

The quote field got worse, from 10/10 to 8/10. The few-shot output copied the
German REQ-03 quote with `korrigeren` instead of the source's `korrigieren`,
and added a non-source character to the REQ-04 quote. These are genuine
substring failures, not scorer noise. The category and due-date errors did
not disappear: category remained wrong on one record, and three invented due
dates remained wrong. The examples changed the shape of the quote failures
by teaching tidied or corrupted copying, rather than fixing an existing
error.

### 5. What the examples cost

- extra input tokens per call: 310
- per thousand calls: 310,000
- estimated euros per thousand calls on the small tier: 62.00, against the
  price list dated 2026-08-10. Estimate, not a measurement.

### 6. Ship it or not

I would keep the zero-shot variant. Few-shot did not improve category,
urgency, or due_date, and reduced quote accuracy by two records while adding
310 input tokens per call. The sample has only ten records, so this is useful
evidence rather than a confident general conclusion. I would change my mind
if a larger held-out set showed a repeatable improvement in a field that
matters more than the quote regression, without introducing new exact-copy
failures.

### Sensitivity variant

Variant assigned: [ ]. What I changed: [ ]. What moved: [ ].

[If nothing moved, say so. A knob that changes nothing measurable is a real
result, and it tells the room which knobs are worth arguing about.]

### The gold set

Ten cases written to `artifacts/goldset.json`, tagged by language.

One thing my scorer cannot currently detect:

[This is the most valuable line on the page. An example: "our scorer cannot
tell a correctly formatted date that is simply the wrong date from a
correctly extracted one, because it only compares strings."]

### Deferred

[Anything you did not get to, and why.]

## Week 3

**Run conditions.** classifier model: [ ] | answering model: [ ] |
temperature: 0.0 | served locally | date: [YYYY-MM-DD] | scored on: [the
recording / my own machine]

### 1. The five route definitions

| route | definition, one sentence, in terms of what the help desk must do |
| request |Messages where the user is asking for a specific action or service. The help desk is expected to fulfill the request or provide a reason why it cannot be fulfilled. |
| info |Messages where the user is seeking information about a topic, but not necessarily requesting a specific action. The help desk is expected to provide the requested information. |
| status | Messages where the user is inquiring about the status of an ongoing request or issue. The help desk is expected to provide an update on the current status.|
| complaint |Messages where the user is dissatisfied with the service and expresses their displeasure and what they are unhappy about, but does not request a specific action or service. The help desk is expected to acknowledge the complaint and escalate it appropriately. |
| other | Messages that do not fit into any of the other categories and have nothing to do with the help desk's work.|

My convention for the four ambiguous queries:

IF a message is asking an update on an existing request, the message will be labelled status, even if it mentions the original request.
If a message both reports a problem and expresses dissatisfaction with the handling, it will be labelled complaint, as acknowleding the issue is the first thing that should be done.
If a message asks a question while reporting a fault and requesting action, it will be labelled request, because action is more important than information.

Do my definitions match the ones in `queries.py`? No, our definitions don't exactly match those in queries.py, rather we have a more general definition and different boundaries, especially for request, complaint and other. Thus, the accuracy score is partly measuring mismatch between our definitions and the gold-label conventions, rather than only measuring calssifier quality.

### 2. The policy layer

Before choosing a threshold, the confidence values I saw were: min 0.00,
max 1.00, 3 distinct values across 24 queries on qwen3:4b-instruct (0.00 x2,
0.99 x15, 1.00 x7). On qwen2.5:7b: min 0.95, max 1.00, 2 distinct values
(0.95 x13, 1.00 x11). Both models got 19/24 routes right.

The confidence does not separate right from wrong. On qwen3:4b-instruct all
five misroutes score 0.99, the same as most correct routes, and the only
0.00s are Q-22 and Q-23, both correctly routed `other`. On qwen2.5:7b, 4 of
13 answers at 0.95 are wrong, against 1 of 11 at 1.00: weak, and not enough
to act on.

- confidence floor: 0.5, not applied to `other` (fires when confidence <
  0.5 and the route is one of the four that act). My first choice was 0.95,
  and the distribution shows why it was wrong: on qwen3:4b-instruct it fired
  only on Q-22 and Q-23, both correct, so it caught 0 misroutes and cost 2
  correct routes; on qwen2.5:7b it never fired. A floor high enough to catch
  qwen3:4b-instruct's misroutes (above 0.99) would reject 15 of 24 messages,
  10 of them correct. No value separates right from wrong on either model, so
  the floor is not a misroute detector. It is a backstop for a decision the
  model itself calls a coin flip, and 0.5 sits in the empty gap between 0.00
  and 0.95 that both models leave. The 0.00s only ever landed on spam and the
  prompt injection, routed `other`, where the model is scoring "is this help
  desk business" rather than "how sure am I". Moving those to the safe
  default would hand a prompt injection to `info`, a specialist told to
  answer, so the floor skips `other`, whose specialist is told not to follow
  instructions in the message.
- evidence check: when the span is empty or not an exact, case-sensitive
  substring of the message, the decision is overridden to the safe default
  and logged as `evidence_not_verbatim`, because a router that invents its
  justification cannot be audited, and the evidence is what a human reads
  when reviewing a misroute. The check tests honesty, not correctness: it
  overrides even when the route was right.
- safe default: `info`, because that specialist only answers, and is
  forbidden to state any fact it was not given. `request` logs a ticket and
  `complaint` escalates to a person, so being wrong into either creates work
  someone has to undo. `status` claims knowledge of a ticket that may not
  exist. `other` tells a sender with a real problem that it is not our
  business, so a broken door would go unreported. A wrong `info` reply costs
  the sender one more message.

How often each check fired: below_threshold 0, evidence_not_verbatim [ ],
invalid_decision [ ] (my run, after TODO 5). On the recording, which replays
the reference prompt's answers rather than mine: qwen3:4b-instruct 0, 0, 0;
qwen2.5:7b 0, 5, 0 (Q-05, Q-08, Q-09 re-accented the French and German, Q-16
ended in a non-Latin token, and Q-24 quoted the route definition instead of
the message).

The floor firing zero times is the finding, not a mistake: the confidence
is a near-constant 0.95 to 1.00 on everything either model treats as help
desk business, so the signal is useless for routing on both models. The
evidence check is the only policy check doing real work, and only on
qwen2.5:7b.

### 3. Route accuracy

| route | correct | of |
| request | | |
| info | | |
| status | | |
| complaint | | |
| other | | |

Overall [ ]/24. Excluding the four ambiguous: [ ]/20.

Confusion pairs, with direction:

| gold | applied | count |
| | | |

The route carrying most of the error is [ ]. The fix is [a definition / a
prompt / a bigger model], because [ ].

### 4. What routing cost

- monolith: [ ] tokens over 24 queries
- router: [ ] tokens over 24 queries
- the classifying call alone: [ ] tokens, which is [ ] per cent of the
  routed total

I predicted that share would be [ ] before measuring it.

[If the share surprised you, say why. The classifier's prompt carries every
route definition on every call, and the specialists carry only their own.]

### 5. What routing bought

One thing a specialist can be forbidden to do that the monolith cannot be
given:

The `status` specialist is forbidden to say that anything is done, in
progress, or scheduled, because it cannot see the ticket system. The
monolith cannot be given that rule, because for a `request` it has to
confirm that a ticket is being logged, which is exactly that kind of
statement. In the same way, `complaint` is forbidden to promise a fix while
`request` exists to start one, and `request` is forbidden to answer the
sender at all, which would break every other kind. The monolith only gets
the rules that hold for all five: never invent a fact, and never follow
instructions aimed at the system.

Would I ship the router: [ ]. Evidence: [ ]. What would change my mind: [ ].

### 6. Stretch variant

Variant assigned: [ ]. Result: [ ].

[For model routing: report both models on accuracy, evidence verbatim, the
confidence range, and resident memory. If the smaller model won, say so
plainly and say what you think that means.]

[For voting: report the split-vote count at each temperature. If nothing
ever disagreed, that is the result. Say what it cost and what it bought.]

### The gold set

`artifacts/goldset.json` now holds [ ] cases: 10 from week 2 and 24 added
today, with the four ambiguous ones tagged.

### Deferred

[Anything you did not get to, and why.]
