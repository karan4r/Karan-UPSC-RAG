import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class IntentResult:
    intent: str
    confidence: float
    signals: list[str]


FRESH_GRAD_PATTERNS = [
    r"just passed college",
    r"just finished college",
    r"just completed (?:my )?graduation",
    r"fresh(?:ly)? graduate",
    r"fresh out of college",
    r"completed (?:my )?degree",
    r"recently graduated",
    r"passed college",
]

WORKING_PATTERNS = [
    r"working professional",
    r"full[- ]time job",
    r"while working",
    r"i'?m working",
    r"job and upsc",
]

COLLEGE_STUDENT_PATTERNS = [
    r"still in college",
    r"in (?:my )?(?:2nd|3rd|second|third) year",
    r"final year (?:of )?college",
    r"currently in college",
]

REPEAT_ATTEMPT_PATTERNS = [
    r"(?:2nd|3rd|second|third|fourth) attempt",
    r"repeat(?:ed)? attempt",
    r"failed (?:again|multiple)",
]

COURSE_PATTERNS = [
    r"suggest (?:a )?course",
    r"recommend (?:a )?(?:course|batch)",
    r"which course",
    r"what course",
    r"join (?:a )?(?:course|batch)",
]

BACKUP_PATTERNS = [
    r"backup plan",
    r"plan b",
    r"alternative exam",
    r"other exam",
    r"along with upsc",
    r"if upsc doesn'?t work",
    r"safety net",
    r"parallel exam",
]

UPSC_PATTERNS = [
    r"upsc",
    r"civil services",
    r"cse",
    r"ias",
    r"ips",
    r"prelims",
    r"mains",
    r"civil service",
]

MENTAL_HEALTH_PATTERNS = [
    r"depress",
    r"anxiety",
    r"anxious",
    r"stress(ed)?",
    r"mental health",
    r"hopeless",
    r"can'?t cope",
    r"broken me",
    r"suicid",
    r"self[- ]harm",
    r"overwhelmed emotionally",
    r"emotionally",
]

FAILURE_PATTERNS = [
    r"fail(ed|ure)?",
    r"didn'?t clear",
    r"not selected",
    r"couldn'?t qualify",
    r"result",
    r"unsuccessful",
]

ACADEMIC_PATTERNS = [
    r"\bexplain\b",
    r"\bnotes\b",
    r"what is",
    r"what are",
    r"significance of",
    r"causes of",
    r"reasons for",
    r"describe",
    r"syllabus",
    r"topic",
    r"article \d",
    r"fundamental",
    r"parliament",
    r"rbi grade",
    r"revolt",
    r"movement",
    r"reform",
    r"act of \d",
]


def _matches(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text, re.I) for p in patterns)


def _collect_signals(text: str) -> list[str]:
    signals = []
    if _matches(FRESH_GRAD_PATTERNS, text):
        signals.append("fresh_graduate")
    if _matches(WORKING_PATTERNS, text):
        signals.append("working_professional")
    if _matches(COLLEGE_STUDENT_PATTERNS, text):
        signals.append("still_in_college")
    if _matches(REPEAT_ATTEMPT_PATTERNS, text):
        signals.append("repeat_attempt")
    if _matches(COURSE_PATTERNS, text):
        signals.append("course_request")
    if _matches(BACKUP_PATTERNS, text):
        signals.append("backup_plan")
    if _matches(UPSC_PATTERNS, text):
        signals.append("upsc_context")
    if _matches(MENTAL_HEALTH_PATTERNS, text):
        signals.append("mental_health")
    if _matches(FAILURE_PATTERNS, text):
        signals.append("exam_failure")
    if _matches(ACADEMIC_PATTERNS, text):
        signals.append("academic")
    return signals


def classify_intent(query: str) -> IntentResult:
    text = query.lower().strip()
    signals = _collect_signals(text)

    # Priority: mental health > fresh grad course > backup > academic
    if "mental_health" in signals and "upsc_context" in signals:
        return IntentResult("mental_health_upsc_distress", 0.95, signals)

    if "mental_health" in signals and (
        "exam_failure" in signals or "upsc_context" in signals
    ):
        return IntentResult("mental_health_upsc_distress", 0.9, signals)

    if (
        "fresh_graduate" in signals
        and "course_request" in signals
        and "working_professional" not in signals
        and "still_in_college" not in signals
        and "repeat_attempt" not in signals
    ):
        return IntentResult("suggest_course_fresh_graduate_only", 0.92, signals)

    if "course_request" in signals and "fresh_graduate" not in signals:
        return IntentResult("course_clarification_needed", 0.75, signals)

    if "backup_plan" in signals and "upsc_context" in signals:
        return IntentResult("backup_plan_while_upsc", 0.9, signals)

    if "backup_plan" in signals:
        return IntentResult("backup_plan_while_upsc", 0.7, signals)

    if "academic" in signals or _matches(UPSC_PATTERNS, text):
        return IntentResult("notes_or_explain_topic", 0.8, signals)

    return IntentResult("general", 0.3, signals)


def get_clarification_message(intent: str) -> Optional[str]:
    if intent == "course_clarification_needed":
        return (
            "That batch is recommended specifically for students who have **just finished college**. "
            "Could you confirm — have you recently completed your graduation, or are you still in college / working full-time?"
        )
    return None
