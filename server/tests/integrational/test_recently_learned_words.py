import datetime

import pytest

from server.main import get_learned_words
from server.schema import User, UserWord, Word


@pytest.mark.asyncio
async def test_get_learned_words_returns_correct_count(async_db):
    Session = async_db
    async with Session() as session:
        session.add_all(
            [
                User(id=1, chat_id=1),
                User(id=2, chat_id=2),
                User(id=3, chat_id=3),
            ]
        )
        await session.commit()

        session.add_all(
            [
                Word(id=1, english="test", russian="тест"),
                Word(id=2, english="car", russian="машина"),
                Word(id=3, english="dog", russian="собака"),
            ]
        )
        await session.commit()
        now = datetime.datetime.now()
        session.add_all(
            [
                UserWord(user_id=1, word_id=1, count=1, need_to_show=now),
                UserWord(user_id=1, word_id=2, count=1, need_to_show=now),
                UserWord(user_id=2, word_id=3, count=1, need_to_show=now),
            ]
        )
        await session.commit()

        result1 = await get_learned_words(1, session)
        assert result1 == {"learned_words_count": 2}

        result2 = await get_learned_words(2, session)
        assert result2 == {"learned_words_count": 1}

        result3 = await get_learned_words(3, session)
        assert result3 == {"learned_words_count": 0}
