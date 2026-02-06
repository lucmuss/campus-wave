from controller.html_formatter import HtmlFormatter


def main() -> None:
    formatter = HtmlFormatter()
    sample_timestamp = 1_700_000_000
    sample_duration_ms = 95_000

    print("Formatted date:", formatter.format_creation_date(sample_timestamp))
    print("Formatted duration:", formatter.milliseconds_to_duration(sample_duration_ms))


if __name__ == "__main__":
    main()
