#!/usr/bin/env python3
"""End-to-end tests for all curated query types."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generation.rag_chain import RAGChatbot

TEST_CASES = [
    {
        "name": "Fresh grad course recommendation",
        "query": "I just passed college and I want to prepare for UPSC and give my attempt next year. Suggest a course for me.",
        "expect_intent": "suggest_course_fresh_graduate_only",
        "must_contain": ["pw.live", "comprehensive", "1-year"],
        "must_not_contain": ["nextleap", "1-800-891-4416"],
    },
    {
        "name": "Working professional course (no PW link)",
        "query": "I'm working full-time and want to prepare for UPSC. Suggest a course for me.",
        "expect_intent": "course_clarification_needed",
        "must_contain": ["just finished college"],
        "must_not_contain": ["pw.live/study-v2/batches/6a1a72e589d72a57936e540b"],
    },
    {
        "name": "Backup plan while UPSC",
        "query": "I am preparing for UPSC but want a backup plan. What should I do?",
        "expect_intent": "backup_plan_while_upsc",
        "must_contain": ["RBI", "State PSC", "nextleap.app"],
        "must_not_contain": ["1-800-891-4416"],
    },
    {
        "name": "Mental health after UPSC failure",
        "query": "I failed UPSC again and I'm feeling depressed and anxious.",
        "expect_intent": "mental_health_upsc_distress",
        "must_contain": ["Feel the emotion", "Emotional Intelligence", "1-800-891-4416", "Tele MANAS"],
        "must_not_contain": ["pw.live", "nextleap"],
    },
    {
        "name": "Academic - Fundamental Duties",
        "query": "Explain Fundamental Duties for UPSC",
        "expect_intent": "notes_or_explain_topic",
        "must_contain": ["Fundamental Duties"],
        "must_not_contain": [],
    },
    {
        "name": "Academic - Parliament notes",
        "query": "Provide notes on Indian Parliament for prelims",
        "expect_intent": "notes_or_explain_topic",
        "must_contain": ["Parliament"],
        "must_not_contain": [],
    },
]


def run_tests():
    bot = RAGChatbot()
    passed = 0
    failed = 0

    print("=" * 60)
    print("UPSC RAG Chatbot — Test Suite")
    print("=" * 60)

    for case in TEST_CASES:
        print(f"\n▶ {case['name']}")
        print(f"  Q: {case['query'][:80]}...")

        result = bot.chat(case["query"])
        answer = result["answer"]
        intent = result["intent"]
        errors = []

        if intent != case["expect_intent"]:
            errors.append(f"Intent: expected {case['expect_intent']}, got {intent}")

        for text in case["must_contain"]:
            if text.lower() not in answer.lower():
                errors.append(f"Missing required text: {text}")

        for text in case["must_not_contain"]:
            if text.lower() in answer.lower():
                errors.append(f"Should NOT contain: {text}")

        if errors:
            failed += 1
            print("  ✗ FAILED")
            for e in errors:
                print(f"    - {e}")
            print(f"  Mode: {result['mode']} | Confidence: {result['confidence']}")
            print(f"  Answer preview: {answer[:200]}...")
        else:
            passed += 1
            print(f"  ✓ PASSED (intent={intent}, mode={result['mode']})")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{passed + failed} passed")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
