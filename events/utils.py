import pytz
from django.utils import timezone


def get_formatted_stream_timeframe(stream):
    starts_at = stream.starts_at.strftime("%c %z")
    ends_at = stream.ends_at.strftime("%c %z")

    if stream.timezone:
        tzinfo = pytz.timezone(stream.timezone)
        starts_at_tz = timezone.make_aware(
            timezone.make_naive(stream.starts_at, timezone=tzinfo), timezone=tzinfo
        ).strftime("%c %z")
        ends_at_tz = timezone.make_aware(
            timezone.make_naive(stream.ends_at, timezone=tzinfo), timezone=tzinfo
        ).strftime("%c %z")
    else:
        starts_at_tz = ends_at_tz = None

    starts_at_s = f"{starts_at_tz} ({starts_at})" if starts_at_tz else starts_at
    ends_at_s = f"{ends_at_tz} ({ends_at})" if ends_at_tz else ends_at

    return starts_at_s, ends_at_s


def get_support_channels_test(stream):
    if stream.event.support_urls.exists():
        return (
            "Streaming documentation and support links.\n"
            + "If you have any questions, please reach out to our support channel:\n"
            + "\n".join(f"* {u.name}: {u.url}" for u in stream.event.support_urls.all())
        )
    else:
        return "If you have any questions, please reach out to our support channel."
