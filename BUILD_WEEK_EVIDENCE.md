# Build Week evidence and scope

## Eligibility boundary

WriteAIBook existed before OpenAI Build Week. The eligible extension began after
the event cutoff on **July 13, 2026 at 9:00 AM PDT**.

The first qualifying product change moved the Pro generation path from its
previous model to GPT-5.6 Terra on the official OpenAI API, with an exact
same-model OpenRouter fallback. Subsequent qualifying work connected the free
first chapter to durable generation, continuation, recovery, and feedback.

## Qualifying production changes

| Date | Production PR | Contribution |
| --- | ---: | --- |
| Jul 13 | #176 | GPT-5.6 Terra routing and same-model failover |
| Jul 14 | #183 | Pro-first welcome chapter and first-book journey |
| Jul 14 | #188 | Durable generation recovery and canon boundaries |
| Jul 14 | #190 | Bounded repair for near-limit prose |
| Jul 15 | #189 | Manuscript continuity and attribution fixes |
| Jul 16 | #194 | Preserve usable prose after exhausted quality repair |
| Jul 16 | #196 | Per-book quality ratings |
| Jul 19 | #204 | Post-chapter continuation and premise integrity |
| Jul 20 | #208 | End-to-end auth, progress, continuation, cost, and race tests |

These identifiers refer to the private production history. The runnable,
sanitized implementations of the central contracts are published in this
repository so review does not require private access.

## Contract-to-code map

| Build Week contract | Public code | Public regression test |
| --- | --- | --- |
| Official Terra first | `build_week_reference/provider_contract.py` | `test_pro_chain_prefers_official_openai` |
| Same-model failover | `build_week_reference/provider_contract.py` | `test_pro_failover_preserves_model_family` |
| Terra capability handling | `build_week_reference/provider_contract.py` | `test_terra_removes_unsupported_sampling_controls` |
| Durable continuation state | `build_week_reference/continuation_contract.py` | `test_continuation_preserves_canon` |
| Delta-only billing | `build_week_reference/continuation_contract.py` | `test_continuation_bills_only_new_chapters` |
| Bounded recovery | `build_week_reference/continuation_contract.py` | `test_only_small_quality_misses_can_preserve_output` |

## Codex evidence

- Primary Codex session: `019f5cdb-d63e-7ff2-9165-41e8f12a763f`
- Primary objective: move Pro generation to GPT-5.6 Terra on the official
  OpenAI API while preserving the same model on fallback.
- Codex was also used for pipeline tracing, implementation, regression design,
  browser-race reproduction, code review, and end-to-end validation.

## Explicit exclusions

- The original product and its pre-Build Week generator are not claimed as new.
- SEO, lifecycle marketing, administration, analytics, and pricing experiments
  are outside the judging story.
- Production usage totals establish that the extension serves a real audience;
  they are not represented as work created during Build Week.
