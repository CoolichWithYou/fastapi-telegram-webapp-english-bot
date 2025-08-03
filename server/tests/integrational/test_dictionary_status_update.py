import pytest

from server.main import update_dictionary_status
from server.schema import Dictionary, User, UserDict, UserDictionaryRequest


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

        session.add(Dictionary(id=1, title="oxford 3000"))
        await session.commit()

        session.add_all(
            [
                UserDict(user_id=1, dict_id=1),
                UserDict(user_id=2, dict_id=1),
            ]
        )

        await session.commit()

        result = await update_dictionary_status(
            UserDictionaryRequest(chat_id=1, dict_id=1), session
        )
        assert result == {"character": " "}

        result = await update_dictionary_status(
            UserDictionaryRequest(chat_id=3, dict_id=1), session
        )
        assert result == {"character": "✓"}
