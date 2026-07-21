from __future__ import annotations

import unittest

from build_week_reference.continuation_contract import (
    ManuscriptState,
    RecoveryDecision,
    prepare_continuation,
    recovery_decision,
)
from build_week_reference.provider_contract import (
    OFFICIAL_TERRA_MODEL,
    build_openai_request,
    failover_preserves_model_family,
    pro_provider_chain,
)


class ProviderContractTests(unittest.TestCase):
    def test_pro_chain_prefers_official_openai(self) -> None:
        routes = pro_provider_chain()
        self.assertEqual(routes[0].provider, "openai")
        self.assertEqual(routes[0].model, OFFICIAL_TERRA_MODEL)
        self.assertEqual(routes[1].provider, "openrouter")

    def test_pro_failover_preserves_model_family(self) -> None:
        self.assertTrue(failover_preserves_model_family(pro_provider_chain()))

    def test_terra_removes_unsupported_sampling_controls(self) -> None:
        body = build_openai_request(
            model=OFFICIAL_TERRA_MODEL,
            messages=[{"role": "user", "content": "Write chapter two."}],
            temperature=0.9,
            top_p=0.95,
            response_format={"type": "json_object"},
        )
        self.assertNotIn("temperature", body)
        self.assertNotIn("top_p", body)
        self.assertNotIn("frequency_penalty", body)
        self.assertEqual(body["response_format"], {"type": "json_object"})

    def test_legacy_models_keep_supported_sampling_controls(self) -> None:
        body = build_openai_request(
            model="legacy-compatible-model",
            messages=[{"role": "user", "content": "Write."}],
            temperature=0.6,
            top_p=0.8,
        )
        self.assertEqual(body["temperature"], 0.6)
        self.assertEqual(body["top_p"], 0.8)


class ContinuationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = ManuscriptState(
            job_id="demo-book",
            premise="A cartographer finds roads erased from history.",
            genre="Fantasy",
            language="English",
            quality_tier="Pro",
            story_bible={"lantern": "reveals erased roads"},
            chapters=("Chapter one text",),
            story_chapter_count=12,
        )

    def test_continuation_bills_only_new_chapters(self) -> None:
        plan = prepare_continuation(self.state, requested_total_chapters=4)
        self.assertEqual(plan.billable_chapters, 3)
        self.assertEqual(plan.resume_chapters, ("Chapter one text",))

    def test_continuation_preserves_canon(self) -> None:
        plan = prepare_continuation(self.state, requested_total_chapters=4)
        self.assertEqual(plan.state.job_id, self.state.job_id)
        self.assertEqual(plan.state.premise, self.state.premise)
        self.assertEqual(plan.state.story_bible, self.state.story_bible)
        self.assertEqual(plan.state.quality_tier, "Pro")

    def test_continuation_cannot_discard_existing_chapters(self) -> None:
        with self.assertRaises(ValueError):
            prepare_continuation(self.state, requested_total_chapters=0)

    def test_only_small_quality_misses_can_preserve_output(self) -> None:
        decision = recovery_decision(
            clean_output=True,
            small_quality_miss=True,
            safe=True,
            provider_completed=True,
            artifact_usable=True,
        )
        self.assertEqual(decision, RecoveryDecision.PRESERVE_CLEAN_OUTPUT)

        unsafe = recovery_decision(
            clean_output=True,
            small_quality_miss=True,
            safe=False,
            provider_completed=True,
            artifact_usable=True,
        )
        self.assertEqual(unsafe, RecoveryDecision.FAIL_HARD)


if __name__ == "__main__":
    unittest.main()
