from controller.html_formatter import HtmlFormatter


def test_timestamp_to_date_formats_utc_timestamp() -> None:
    assert HtmlFormatter.timestamp_to_date(0) == "00:00 - 01.01.1970"


def test_milliseconds_to_duration_formats_hh_mm_ss() -> None:
    assert HtmlFormatter.milliseconds_to_duration(95_000) == "00:01:35"


def test_get_speech_recognition_precision_counts_unknown_tokens() -> None:
    formatter = HtmlFormatter()
    assert formatter.get_speech_recognition_precision(["a", "u", "b", "u"]) == "50%"


def test_format_recognized_speech_marks_matches_and_relevant_tokens() -> None:
    formatter = HtmlFormatter()
    tokens = ["foo", "bar", "baz"]
    result = formatter.format_recognized_speech(
        token_list=tokens,
        search_term_set={"bar"},
        relevant_term_set={"baz"},
    )
    assert result == [("foo", 0), ("bar", 1), ("baz", 2)]
