"""Tests for src.core.query_processor module."""

import pytest

from src.core.query_processor import (
    EntityExtraction,
    IntentCategory,
    QueryAnalysis,
    QueryProcessor,
    create_query_processor,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def processor():
    """Return a CPU-only QueryProcessor with default memory limit."""
    return QueryProcessor(device="cpu")


@pytest.fixture
def processor_custom_limit():
    """Return a CPU-only QueryProcessor with a custom memory limit."""
    return QueryProcessor(device="cpu", memory_limit_mb=32)


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------

class TestInit:
    """Tests for QueryProcessor.__init__."""

    def test_default_device_cpu(self, processor):
        assert processor.device == "cpu"

    def test_explicit_cpu_device(self):
        qp = QueryProcessor(device="cpu")
        assert qp.device == "cpu"

    def test_default_memory_limit(self, processor):
        assert processor.memory_limit_mb == 15

    def test_custom_memory_limit(self, processor_custom_limit):
        assert processor_custom_limit.memory_limit_mb == 32

    def test_initial_query_count_zero(self, processor):
        assert processor._query_count == 0

    def test_initial_memory_usage_zero(self, processor):
        assert processor._memory_usage == 0.0

    def test_intent_patterns_populated(self, processor):
        assert len(processor.intent_patterns) > 0

    def test_entity_patterns_populated(self, processor):
        assert len(processor.entity_patterns) > 0

    def test_normalization_rules_populated(self, processor):
        assert len(processor.normalization_rules) > 0


# ---------------------------------------------------------------------------
# _normalize_query tests
# ---------------------------------------------------------------------------

class TestNormalizeQuery:
    """Tests for QueryProcessor._normalize_query."""

    def test_lowercases_text(self, processor):
        assert processor._normalize_query("HELLO WORLD") == "hello world"

    def test_strips_whitespace(self, processor):
        result = processor._normalize_query("  hello  ")
        assert result == "hello"

    def test_collapses_multiple_spaces(self, processor):
        result = processor._normalize_query("hello    world")
        assert "  " not in result

    def test_removes_politeness_markers(self, processor):
        result = processor._normalize_query("Could you please find my file")
        # "could you" and "please" should be removed
        assert "please" not in result
        assert "could you" not in result

    def test_removes_filler_words(self, processor):
        result = processor._normalize_query("um I need uh help")
        assert "um" not in result.split()
        assert "uh" not in result.split()

    def test_empty_string(self, processor):
        result = processor._normalize_query("")
        assert result == ""

    def test_only_whitespace(self, processor):
        result = processor._normalize_query("   ")
        assert result == ""

    def test_preserves_question_mark(self, processor):
        result = processor._normalize_query("What is AI?")
        assert "?" in result

    def test_preserves_exclamation_mark(self, processor):
        result = processor._normalize_query("Help!")
        assert "!" in result


# ---------------------------------------------------------------------------
# _classify_intent tests
# ---------------------------------------------------------------------------

class TestClassifyIntent:
    """Tests for QueryProcessor._classify_intent."""

    def test_question_intent(self, processor):
        intent, conf = processor._classify_intent("what is machine learning")
        assert intent == IntentCategory.QUESTION
        assert conf > 0

    def test_search_intent(self, processor):
        intent, conf = processor._classify_intent("search for restaurants")
        assert intent == IntentCategory.SEARCH
        assert conf > 0

    def test_reminder_intent(self, processor):
        intent, conf = processor._classify_intent("remind me to buy milk")
        assert intent == IntentCategory.REMINDER
        assert conf > 0

    def test_schedule_intent(self, processor):
        intent, conf = processor._classify_intent("schedule a meeting for monday")
        assert intent == IntentCategory.SCHEDULE
        assert conf > 0

    def test_greeting_intent(self, processor):
        intent, conf = processor._classify_intent("hello how are you")
        assert intent == IntentCategory.GREETING
        assert conf > 0

    def test_help_intent(self, processor):
        intent, conf = processor._classify_intent("help me with this problem")
        assert intent == IntentCategory.HELP
        assert conf > 0

    def test_calculate_intent(self, processor):
        intent, conf = processor._classify_intent("calculate 2 + 3")
        assert intent == IntentCategory.CALCULATE
        assert conf > 0

    def test_definition_intent(self, processor):
        intent, conf = processor._classify_intent("define photosynthesis")
        assert intent == IntentCategory.DEFINITION
        assert conf > 0

    def test_unknown_intent_for_gibberish(self, processor):
        intent, conf = processor._classify_intent("xyzzy plugh")
        assert intent == IntentCategory.UNKNOWN
        assert conf == 0.0

    def test_confidence_capped_at_one(self, processor):
        # Many question markers to push score up
        intent, conf = processor._classify_intent("what who when where why how? what? who?")
        assert conf <= 1.0

    def test_empty_query_returns_unknown(self, processor):
        intent, conf = processor._classify_intent("")
        assert intent == IntentCategory.UNKNOWN
        assert conf == 0.0


# ---------------------------------------------------------------------------
# _extract_entities tests
# ---------------------------------------------------------------------------

class TestExtractEntities:
    """Tests for QueryProcessor._extract_entities."""

    def test_extracts_date_word(self, processor):
        entities = processor._extract_entities("I need this tomorrow")
        types = [e.entity_type for e in entities]
        assert "DATE" in types

    def test_extracts_day_of_week(self, processor):
        entities = processor._extract_entities("meeting on monday")
        date_entities = [e for e in entities if e.entity_type == "DATE"]
        assert any("monday" in e.text.lower() for e in date_entities)

    def test_extracts_time(self, processor):
        entities = processor._extract_entities("call at 3:00 pm")
        types = [e.entity_type for e in entities]
        assert "TIME" in types

    def test_extracts_number(self, processor):
        entities = processor._extract_entities("buy 5 apples")
        types = [e.entity_type for e in entities]
        assert "NUMBER" in types

    def test_extracts_email(self, processor):
        entities = processor._extract_entities("send to user@example.com")
        types = [e.entity_type for e in entities]
        assert "EMAIL" in types

    def test_extracts_phone(self, processor):
        entities = processor._extract_entities("call 555-123-4567")
        types = [e.entity_type for e in entities]
        assert "PHONE" in types

    def test_entity_has_correct_structure(self, processor):
        entities = processor._extract_entities("meet tomorrow")
        assert len(entities) > 0
        e = entities[0]
        assert isinstance(e, EntityExtraction)
        assert isinstance(e.text, str)
        assert isinstance(e.entity_type, str)
        assert isinstance(e.start_pos, int)
        assert isinstance(e.end_pos, int)
        assert isinstance(e.confidence, float)
        assert isinstance(e.metadata, dict)

    def test_no_entities_for_simple_text(self, processor):
        entities = processor._extract_entities("hello world")
        # Numbers like word-length matches may still appear; just ensure no crash
        assert isinstance(entities, list)

    def test_entity_positions_valid(self, processor):
        query = "tomorrow at 5:00 pm"
        entities = processor._extract_entities(query)
        for e in entities:
            assert 0 <= e.start_pos < e.end_pos <= len(query)

    def test_extracts_month_date(self, processor):
        entities = processor._extract_entities("deadline is january 15")
        date_entities = [e for e in entities if e.entity_type == "DATE"]
        assert len(date_entities) > 0


# ---------------------------------------------------------------------------
# _extract_keywords tests
# ---------------------------------------------------------------------------

class TestExtractKeywords:
    """Tests for QueryProcessor._extract_keywords."""

    def test_filters_stopwords(self, processor):
        keywords = processor._extract_keywords("i am looking at the results")
        assert "i" not in keywords
        assert "am" not in keywords
        assert "the" not in keywords

    def test_returns_list(self, processor):
        keywords = processor._extract_keywords("machine learning algorithms")
        assert isinstance(keywords, list)

    def test_max_ten_keywords(self, processor):
        long_query = " ".join(f"keyword{i}" for i in range(30))
        keywords = processor._extract_keywords(long_query)
        assert len(keywords) <= 10

    def test_excludes_short_words(self, processor):
        keywords = processor._extract_keywords("go to it")
        # Words with length <= 2 should be excluded
        for kw in keywords:
            assert len(kw) > 2

    def test_keywords_are_lowercase(self, processor):
        keywords = processor._extract_keywords("Machine Learning Algorithms")
        for kw in keywords:
            assert kw == kw.lower()

    def test_empty_query_returns_empty(self, processor):
        keywords = processor._extract_keywords("")
        assert keywords == []

    def test_content_words_preserved(self, processor):
        keywords = processor._extract_keywords("python programming tutorial")
        assert "python" in keywords
        assert "programming" in keywords
        assert "tutorial" in keywords


# ---------------------------------------------------------------------------
# _analyze_sentiment tests
# ---------------------------------------------------------------------------

class TestAnalyzeSentiment:
    """Tests for QueryProcessor._analyze_sentiment."""

    def test_positive_sentiment(self, processor):
        result = processor._analyze_sentiment("this is great and wonderful")
        assert result == "positive"

    def test_negative_sentiment(self, processor):
        result = processor._analyze_sentiment("this is terrible and awful")
        assert result == "negative"

    def test_neutral_sentiment(self, processor):
        result = processor._analyze_sentiment("schedule a meeting for next week")
        assert result == "neutral"

    def test_mixed_defaults_to_neutral(self, processor):
        result = processor._analyze_sentiment("great but terrible")
        assert result == "neutral"

    def test_empty_query_is_neutral(self, processor):
        result = processor._analyze_sentiment("")
        assert result == "neutral"

    def test_single_positive_word(self, processor):
        result = processor._analyze_sentiment("love")
        assert result == "positive"

    def test_single_negative_word(self, processor):
        result = processor._analyze_sentiment("hate")
        assert result == "negative"


# ---------------------------------------------------------------------------
# _determine_priority tests
# ---------------------------------------------------------------------------

class TestDeterminePriority:
    """Tests for QueryProcessor._determine_priority."""

    def test_reminder_is_high(self, processor):
        priority = processor._determine_priority(IntentCategory.REMINDER, [])
        assert priority == "high"

    def test_schedule_is_high(self, processor):
        priority = processor._determine_priority(IntentCategory.SCHEDULE, [])
        assert priority == "high"

    def test_deadline_is_high(self, processor):
        priority = processor._determine_priority(IntentCategory.DEADLINE, [])
        assert priority == "high"

    def test_help_is_low(self, processor):
        priority = processor._determine_priority(IntentCategory.HELP, [])
        assert priority == "low"

    def test_system_info_is_low(self, processor):
        priority = processor._determine_priority(IntentCategory.SYSTEM_INFO, [])
        assert priority == "low"

    def test_question_without_time_is_normal(self, processor):
        priority = processor._determine_priority(IntentCategory.QUESTION, [])
        assert priority == "normal"

    def test_time_entity_makes_high(self, processor):
        time_entity = EntityExtraction(
            text="3:00 pm",
            entity_type="TIME",
            start_pos=0,
            end_pos=7,
            confidence=0.8,
            metadata={},
        )
        priority = processor._determine_priority(IntentCategory.QUESTION, [time_entity])
        assert priority == "high"

    def test_date_entity_makes_high(self, processor):
        date_entity = EntityExtraction(
            text="tomorrow",
            entity_type="DATE",
            start_pos=0,
            end_pos=8,
            confidence=0.8,
            metadata={},
        )
        priority = processor._determine_priority(IntentCategory.SEARCH, [date_entity])
        assert priority == "high"

    def test_number_entity_does_not_elevate(self, processor):
        num_entity = EntityExtraction(
            text="42",
            entity_type="NUMBER",
            start_pos=0,
            end_pos=2,
            confidence=0.8,
            metadata={},
        )
        priority = processor._determine_priority(IntentCategory.QUESTION, [num_entity])
        assert priority == "normal"


# ---------------------------------------------------------------------------
# process_query (full pipeline) tests
# ---------------------------------------------------------------------------

class TestProcessQuery:
    """Tests for QueryProcessor.process_query end-to-end."""

    def test_returns_query_analysis(self, processor):
        result = processor.process_query("What is AI?")
        assert isinstance(result, QueryAnalysis)

    def test_original_query_preserved(self, processor):
        q = "What is AI?"
        result = processor.process_query(q)
        assert result.original_query == q

    def test_normalized_query_lowercased(self, processor):
        result = processor.process_query("HELLO WORLD")
        assert result.normalized_query == result.normalized_query.lower()

    def test_intent_is_enum_member(self, processor):
        result = processor.process_query("what is python?")
        assert isinstance(result.intent, IntentCategory)

    def test_entities_list(self, processor):
        result = processor.process_query("remind me tomorrow at 3:00 pm")
        assert isinstance(result.entities, list)
        assert len(result.entities) > 0

    def test_keywords_list(self, processor):
        result = processor.process_query("python programming tutorial")
        assert isinstance(result.keywords, list)
        assert len(result.keywords) > 0

    def test_sentiment_string(self, processor):
        result = processor.process_query("this is great")
        assert result.sentiment in {"positive", "negative", "neutral"}

    def test_priority_string(self, processor):
        result = processor.process_query("remind me to call John")
        assert result.priority in {"high", "normal", "low"}

    def test_processing_time_positive(self, processor):
        result = processor.process_query("hello")
        assert result.processing_time_ms >= 0

    def test_memory_usage_non_negative(self, processor):
        result = processor.process_query("hello")
        assert result.memory_usage_mb >= 0

    def test_increments_query_count(self, processor):
        assert processor._query_count == 0
        processor.process_query("first")
        assert processor._query_count == 1
        processor.process_query("second")
        assert processor._query_count == 2

    def test_question_query(self, processor):
        result = processor.process_query("What is machine learning?")
        assert result.intent in {IntentCategory.QUESTION, IntentCategory.DEFINITION}
        assert result.intent_confidence > 0

    def test_reminder_query(self, processor):
        result = processor.process_query("Remind me to buy groceries tomorrow")
        assert result.intent == IntentCategory.REMINDER

    def test_schedule_query(self, processor):
        result = processor.process_query("Schedule a meeting for next Monday")
        assert result.intent == IntentCategory.SCHEDULE

    def test_greeting_query(self, processor):
        result = processor.process_query("Hello there!")
        assert result.intent == IntentCategory.GREETING

    def test_help_query(self, processor):
        result = processor.process_query("Help me with this problem")
        assert result.intent == IntentCategory.HELP

    def test_calculate_query(self, processor):
        result = processor.process_query("Calculate 15 + 27")
        assert result.intent == IntentCategory.CALCULATE


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge-case and boundary tests."""

    def test_empty_string(self, processor):
        result = processor.process_query("")
        assert isinstance(result, QueryAnalysis)
        assert result.intent == IntentCategory.UNKNOWN

    def test_whitespace_only(self, processor):
        result = processor.process_query("   ")
        assert isinstance(result, QueryAnalysis)

    def test_very_long_query(self, processor):
        long_q = "what is " + "python " * 500 + "?"
        result = processor.process_query(long_q)
        assert isinstance(result, QueryAnalysis)
        assert result.intent != IntentCategory.UNKNOWN

    def test_special_characters(self, processor):
        result = processor.process_query("!@#$%^&*()_+-={}[]|\\:;<>,./~`")
        assert isinstance(result, QueryAnalysis)

    def test_unicode_query(self, processor):
        result = processor.process_query("What is café résumé naïve?")
        assert isinstance(result, QueryAnalysis)

    def test_numeric_only(self, processor):
        result = processor.process_query("12345")
        assert isinstance(result, QueryAnalysis)

    def test_single_character(self, processor):
        result = processor.process_query("x")
        assert isinstance(result, QueryAnalysis)

    def test_newlines_in_query(self, processor):
        result = processor.process_query("line one\nline two\nline three")
        assert isinstance(result, QueryAnalysis)

    def test_tabs_in_query(self, processor):
        result = processor.process_query("hello\tworld")
        assert isinstance(result, QueryAnalysis)

    def test_repeated_question_marks(self, processor):
        result = processor.process_query("what???")
        assert isinstance(result, QueryAnalysis)
        assert result.intent == IntentCategory.QUESTION


# ---------------------------------------------------------------------------
# get_stats tests
# ---------------------------------------------------------------------------

class TestGetStats:
    """Tests for QueryProcessor.get_stats."""

    def test_returns_dict(self, processor):
        stats = processor.get_stats()
        assert isinstance(stats, dict)

    def test_contains_expected_keys(self, processor):
        stats = processor.get_stats()
        expected_keys = {
            "queries_processed",
            "memory_usage_mb",
            "memory_limit_mb",
            "device",
            "supported_intents",
            "supported_entities",
        }
        assert expected_keys.issubset(stats.keys())

    def test_queries_processed_starts_zero(self, processor):
        assert processor.get_stats()["queries_processed"] == 0

    def test_queries_processed_increments(self, processor):
        processor.process_query("hello")
        processor.process_query("world")
        assert processor.get_stats()["queries_processed"] == 2

    def test_device_matches(self, processor):
        assert processor.get_stats()["device"] == "cpu"

    def test_memory_limit_matches(self, processor_custom_limit):
        assert processor_custom_limit.get_stats()["memory_limit_mb"] == 32

    def test_supported_intents_positive(self, processor):
        assert processor.get_stats()["supported_intents"] > 0

    def test_supported_entities_positive(self, processor):
        assert processor.get_stats()["supported_entities"] > 0


# ---------------------------------------------------------------------------
# clear_cache tests
# ---------------------------------------------------------------------------

class TestClearCache:
    """Tests for QueryProcessor.clear_cache."""

    def test_clear_cache_runs_without_error(self, processor):
        processor.clear_cache()  # Should not raise

    def test_clear_cache_after_queries(self, processor):
        processor.process_query("hello")
        processor.process_query("world")
        processor.clear_cache()
        # Processor should still be usable after clearing cache
        result = processor.process_query("test after clear")
        assert isinstance(result, QueryAnalysis)


# ---------------------------------------------------------------------------
# Factory function test
# ---------------------------------------------------------------------------

class TestFactory:
    """Tests for create_query_processor factory."""

    def test_factory_returns_processor(self):
        qp = create_query_processor()
        assert isinstance(qp, QueryProcessor)

    def test_factory_processor_works(self):
        qp = create_query_processor()
        result = qp.process_query("hello")
        assert isinstance(result, QueryAnalysis)


# ---------------------------------------------------------------------------
# IntentCategory enum tests
# ---------------------------------------------------------------------------

class TestIntentCategoryEnum:
    """Basic sanity checks for IntentCategory enum values."""

    def test_unknown_exists(self):
        assert IntentCategory.UNKNOWN.value == "unknown"

    def test_greeting_exists(self):
        assert IntentCategory.GREETING.value == "greeting"

    def test_music_exists(self):
        assert IntentCategory.MUSIC.value == "music"

    def test_all_values_are_strings(self):
        for member in IntentCategory:
            assert isinstance(member.value, str)
