# WriteAIBook — OpenAI Build Week 2026

**One premise in. One connected, editable manuscript out.**

WriteAIBook plans a book before drafting it, generates Pro prose with
GPT-5.6 Terra, and preserves the same manuscript, story bible, and chapter plan
when the author continues.

- **Live product:** https://writeaibook.com/generate
- **Demo video:** https://youtu.be/0Al1nSh4wNQ
- **Build Week track:** Apps for Your Life

## Why this public repository exists

WriteAIBook is an established production product and its deployment repository
is private. This repository is the public, sanitized code submission for OpenAI
Build Week. It contains dependency-trimmed extracts of the qualifying production
contracts and executable tests, without customer data, credentials, operational
configuration, billing secrets, private analytics, or unrelated business code.

The product predates Build Week. Judges should evaluate the extension built
after **July 13, 2026 at 9:00 AM PDT**, summarized in
[`BUILD_WEEK_EVIDENCE.md`](BUILD_WEEK_EVIDENCE.md).

## What was built during Build Week

1. **GPT-5.6 Terra Pro generation** through the official OpenAI API.
2. **Same-model failover:** if the official route is unavailable, OpenRouter
   serves GPT-5.6 Terra rather than silently downgrading the Pro tier.
3. **Capability-aware requests:** Terra-incompatible legacy sampling controls
   are removed before the request instead of causing predictable HTTP 400s.
4. **Durable generation state:** closing the page does not kill the manuscript.
5. **Connected continuation:** the existing chapters, premise, story bible,
   genre, language, and quality tier remain attached to the same book.
6. **Delta-only billing:** continuation charges only for chapters that have not
   already been generated.
7. **Bounded recovery and strict safety boundaries:** a small quality miss may
   preserve clean prose; refusals, unsafe output, provider exhaustion, and
   unusable artifacts still stop hard.
8. **Per-book feedback** tied to the exact completed artifact.

## How GPT-5.6 Terra is used

The production Pro provider chain is deliberately narrow:

```text
official OpenAI API / gpt-5.6-terra
                    ↓ failover
OpenRouter / openai/gpt-5.6-terra
```

The fallback preserves the model family and the user-facing quality promise.
The reference implementation in
[`build_week_reference/provider_contract.py`](build_week_reference/provider_contract.py)
shows the model identifiers, provider ordering, capability-aware request body,
and same-model invariant.

GPT-5.6 Terra receives the book plan, story bible, canon, chapter position, and
prose instructions. It is not used as a stateless “write the next paragraph”
chat. Every chapter is generated as part of one durable book artifact.

## How Codex was used

Codex was the primary engineering collaborator for the qualifying work. The
primary session ID was:

```text
019f5cdb-d63e-7ff2-9165-41e8f12a763f
```

Codex helped to:

- map the existing asynchronous generation pipeline;
- implement the GPT-5.6 Terra provider transition;
- identify unsupported request parameters and turn the failure into a
  capability check;
- propagate continuation invariants through persistence, billing, API state,
  and browser UI;
- reproduce authentication, progress-polling, and checkout races;
- convert production failures into deterministic regression tests;
- review the eligible scope and verify the complete browser journey.

The product decisions remained human-owned: no hidden quality downgrade,
same-model failover, delta-only continuation billing, bounded quality recovery,
and hard safety stops. Codex helped carry those decisions consistently through
the stack.

## Public reference implementation

```text
build_week_reference/
├── provider_contract.py       # Terra routing and request capabilities
└── continuation_contract.py   # durable canon, delta billing, recovery rules
tests/
└── test_build_week_reference.py
```

Run the self-contained tests with Python 3.12 or newer:

```bash
python -m unittest discover -s tests -v
```

No API key, paid service, database, or production access is required.

## Architecture of the production product

- Python 3.12 and Quart
- SQLAlchemy with durable generation metadata
- Vanilla JavaScript generation interface
- Server-side asynchronous generation jobs
- OpenAI API with same-model OpenRouter fallback
- Editable DOCX artifacts in S3-compatible storage
- Stripe credit billing
- Pytest unit and integration tests
- Playwright browser journeys

## Repository history note

The `bookgenerator-backend/` and `bookgenerator-frontend/` directories are an
older public prototype retained for historical transparency. They are **not**
the current production application and should not be used to evaluate the Build
Week implementation. The root documentation and `build_week_reference/` contain
the current submission materials.

## Privacy and security

This public snapshot intentionally excludes `.env` files, credentials, private
deployment scripts, customer information, generated customer books, internal
analytics, and payment configuration. No access to the private production
repository is required to review or run the code published here.
