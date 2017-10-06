from unittest.mock import MagicMock, patch

import arrow
from aturan_calendar_bot.core import check_posted_today, format_tweet


@patch('aturan_calendar_bot.core.arrow')
def test_check_posted_today_no_tweets(m_arrow):
    today = arrow.utcnow()
    twitter = MagicMock()
    twitter.statuses.user_timeline.return_value = []

    rv = check_posted_today(twitter, today)

    assert rv is False
    twitter.statuses.user_timeline.assert_called_with()
    m_arrow.assert_not_called()


def test_check_posted_today_already_posted():
    today = arrow.utcnow()
    twitter = MagicMock()
    twitter.statuses.user_timeline.return_value = [{'created_at': today.format('ddd MMM DD HH:mm:ss Z YYYY')}]

    rv = check_posted_today(twitter, today)

    assert rv is True


def test_check_posted_today_not_posted():
    today = arrow.utcnow()
    twitter = MagicMock()
    twitter.statuses.user_timeline.return_value = [{'created_at': today.shift(days=-2).format('ddd MMM DD HH:mm:ss Z YYYY')}]

    rv = check_posted_today(twitter, today)

    assert rv is False


def test_format_tweet_special_days():
    dt = arrow.get(2017, 6, 3)
    expected = 'Day #359 of 2017\nHigh Mourning Day #7 (Winter\'s Solstice)'

    actual = format_tweet(dt)

    assert actual == expected


def test_format_tweet_regular_day():
    dt = arrow.get(2016, 4, 14)
    expected = 'Day #303 of 2016\nHepten, the 39th of Fallow (4th Span)'

    actual = format_tweet(dt)

    assert expected == actual
