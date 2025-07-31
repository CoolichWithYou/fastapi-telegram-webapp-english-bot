import datetime
from collections import defaultdict

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from server.db import engine
from server.schema import (About, Dictionary, User, UserDict,
                           UserDictionaryRequest, UserWord, Word, WordDict,
                           WordToLearnRequest, WordToReviewRequest)


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session


def update_show_date(
    count: int, know_the_word: bool
) -> tuple[datetime.datetime | None, int] | None:
    current_show_date = datetime.datetime.now()
    if not know_the_word:
        return current_show_date + datetime.timedelta(seconds=15), 1
    match count:
        case 1:
            return current_show_date + datetime.timedelta(minutes=25), 2
        case 2:
            return current_show_date + datetime.timedelta(hours=8), 3
        case 3:
            return current_show_date + datetime.timedelta(days=1), 4
        case 4:
            return current_show_date + datetime.timedelta(days=3), 5
        case 5:
            return current_show_date + datetime.timedelta(days=14), 6
        case 6:
            return None, 7
    return None


router = APIRouter(prefix="/api")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@router.get("/learned_words")
async def get_learned_words(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """return learned words for 24 hours"""
    statement = (
        select(UserWord)
        .where(UserDict.user_id == user_id)
        .where(UserWord.count != 7)
        .where(
            UserWord.created_at
            < datetime.datetime.now()
            + datetime.timedelta(
                hours=24,
            )
        )
    )
    result = await session.exec(statement)
    recent_words = result.all()

    return {"learned_words_count": len(recent_words)}


@router.get("/dictionaries")
async def root(
    session: AsyncSession = Depends(get_session),
):
    statement = select(Dictionary)
    dictionaries = await session.exec(statement)
    dictionaries = dictionaries.all()
    return dictionaries


@router.post("/update_dictionary")
async def update_dictionary_status(
    user_dict: UserDictionaryRequest,
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.chat_id == user_dict.chat_id)
    result = await session.exec(statement)
    user = result.one()

    statement = (
        select(UserDict)
        .where(UserDict.user_id == user.id)
        .where(UserDict.dict_id == user_dict.dict_id)
    )
    dictionary = await session.exec(statement)
    dictionary = dictionary.first()
    character = " "
    if dictionary:
        await session.delete(dictionary)
    else:
        user_dict = UserDict(
            user_id=user.id,
            dict_id=user_dict.dict_id,
        )
        session.add(user_dict)
        character = "✓"
    await session.commit()
    return {"character": character}


@router.get("/user_dictionaries/{chat_id}")
async def get_user_dictionaries(
    chat_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.chat_id == chat_id)
    user = await session.exec(statement)
    user = user.first()

    statement = select(Dictionary, UserDict).join(
        UserDict,
        (UserDict.dict_id == Dictionary.id) & (UserDict.user_id == user.id),
        isouter=True,
    )

    result = await session.exec(statement)
    user_dicts = result.all()

    dictionaries = []
    for dict_obj, user_dict_obj in user_dicts:
        dictionaries.append(
            {
                "id": dict_obj.id,
                "title": dict_obj.title,
                "selected": user_dict_obj is not None
                and user_dict_obj.user_id == user.id,
            }
        )
    return {"dicts": dictionaries}


@router.get("/user_words/{user_id}")
async def get_user_words(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(UserWord).where(UserWord.user_id == user_id)
    result = await session.exec(statement)
    words = result.all()

    return words


@router.get("/words")
async def get_words(
    session: AsyncSession = Depends(get_session),
):
    statement = select(Word)
    result = await session.exec(statement)
    words = result.all()
    return words


@router.get("/word_to_review")
async def update_word_status(
    chat_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.chat_id == chat_id)
    user = await session.exec(statement)
    user = user.first()

    current_datetime = datetime.datetime.now()
    statement = (
        select(Word)
        .join(WordDict, Word.id == WordDict.word_id)
        .join(Dictionary, Dictionary.id == WordDict.dict_id)
        .join(UserDict, UserDict.dict_id == Dictionary.id)
        .join(UserWord, UserWord.word_id == Word.id)
        .where(UserDict.user_id == user.id)
        .where(UserWord.user_id == user.id)
        .where(UserWord.count < 7)
        .where(UserWord.need_to_show < current_datetime)
    )

    results = await session.exec(statement)
    result = results.first()
    if result:
        result = result.model_dump()
        result["english"] = (
            result["english"]
            .replace("_", "\\_")
            .replace("*", "\\*")
            .replace("[", "\\[")
            .replace("`", "\\`")
            .replace("-", "\\-")
        )
        result["russian"] = (
            result["russian"]
            .replace("_", "\\_")
            .replace("*", "\\*")
            .replace("[", "\\[")
            .replace("`", "\\`")
            .replace("-", "\\-")
        )

        return {"word": result}


@router.post("/user_dictionary")
async def add_dictionary(
    user_id: int,
    dict_id: int,
    session: AsyncSession = Depends(get_session),
):
    new_user_dict = UserDict(user_id=user_id, dict_id=dict_id)
    session.add(new_user_dict)
    await session.commit()


@router.delete("/user_dictionary")
async def remove_dictionary(
    user_id: int,
    dict_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(UserDict).where(
        UserDict.user_id == user_id,
        UserDict.dict_id == dict_id,
    )
    dictionary = await session.exec(statement).one()
    await session.delete(dictionary)
    await session.commit()


@router.post("/word_to_review")
async def get_word_to_review(
    data: WordToReviewRequest,
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.chat_id == data.chat_id)
    user = await session.exec(statement)
    user = user.first()

    statement = (
        select(UserWord)
        .where(UserWord.user_id == user.id)
        .where(UserWord.word_id == data.word_id)
    )
    results = await session.exec(statement)
    user_word = results.first()
    need_to_show, count = update_show_date(
        user_word.count,
        data.know_the_word,
    )
    user_word.need_to_show = need_to_show
    user_word.count = count

    session.add(user_word)
    await session.commit()
    await session.refresh(user_word)


@router.get("/word_to_learn")
async def get_word_to_learn(
    chat_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.chat_id == chat_id)
    user = await session.exec(statement)
    user = user.first()

    subquery = select(UserWord.word_id).where(
        UserWord.user_id == user.id,
    )

    statement = (
        select(Word)
        .join(WordDict, Word.id == WordDict.word_id)
        .join(Dictionary, Dictionary.id == WordDict.dict_id)
        .join(UserDict, UserDict.dict_id == Dictionary.id)
        .where(UserDict.user_id == user.id)
        .where(Word.id.not_in(subquery))
    )

    results = await session.exec(statement)
    result = results.first()

    if result:
        result = result.model_dump()
        result["english"] = (
            result["english"]
            .replace("_", "\\_")
            .replace("*", "\\*")
            .replace("[", "\\[")
            .replace("`", "\\`")
            .replace("-", "\\-")
        )
        result["russian"] = (
            result["russian"]
            .replace("_", "\\_")
            .replace("*", "\\*")
            .replace("[", "\\[")
            .replace("`", "\\`")
            .replace("-", "\\-")
        )

        return {"word": result}


@router.post("/word_to_learn")
async def post_word_to_learn(
    data: WordToLearnRequest,
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.chat_id == data.chat_id)
    user_db = await session.exec(statement)
    user = user_db.first()

    if data.know_the_word:
        session.add(
            UserWord(
                user_id=user.id,
                word_id=data.word_id,
                count=7,
            )
        )
    else:
        tuple_with_datetime = update_show_date(1, False)
        datetime_to_show = None
        if tuple_with_datetime:
            datetime_to_show, count = tuple_with_datetime
        session.add(
            UserWord(
                user_id=user.id,
                word_id=data.word_id,
                count=1,
                need_to_show=datetime_to_show,
            )
        )
    await session.commit()


@router.post("/register_user/{chat_id}")
async def post_register_user(
    chat_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.chat_id == chat_id)
    result = await session.exec(statement)
    user = result.first()
    if user is None:
        user = User(chat_id=chat_id)
        session.add(user)
        await session.commit()


@router.get("/about")
async def about(
    session: AsyncSession = Depends(get_session),
):
    statement = select(About)
    result = await session.exec(statement)
    about_ = result.first()
    if not about_:
        raise HTTPException(status_code=404)

    return {"about": about_.text}


@router.get("/inactive_users")
async def inactive_users(
    session: AsyncSession = Depends(get_session),
):
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=24)

    stmt = (
        select(User)
        .outerjoin(
            UserWord,
            (User.id == UserWord.user_id) & (UserWord.created_at > cutoff),
        )
        .group_by(User.id)
        .having(func.count(UserWord.id) == 0)
    )
    result = await session.exec(stmt)
    users = result.all()
    return users


@router.get("/statistics/{chat_id}")
async def statistics(
    chat_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.chat_id == chat_id)
    user = await session.exec(statement)
    user = user.first()

    statement = (
        select(UserWord)
        .where(UserWord.user_id == user.id)
        .where(
            UserWord.created_at
            > (datetime.datetime.now() - datetime.timedelta(days=30)),
        )
    )
    result = await session.exec(statement)
    statistics_ = result.all()

    daily_counts = defaultdict(int)
    for dt in statistics_:
        day = dt.created_at.date()
        daily_counts[day] += 1

    max_stars = 5

    now = datetime.datetime.now().date()
    start_date = now - datetime.timedelta(days=10)

    date_range = [start_date + datetime.timedelta(days=x) for x in range(11)]

    lines = []

    lines.append("Your learning words statistics:\n")

    for i in range(max_stars, 0, -1):
        line = []
        for date in date_range:
            count = min(daily_counts.get(date, 0), max_stars)
            line.append("---*" if count >= i else "----")
        lines.append(" ".join(line))

    date_labels = [d.strftime("%d") for d in date_range]
    lines.append("  ".join(date_labels))

    lines.append("\nRecord counts from")
    lines.append(f"{start_date} to {now}\n")

    return {"stats": "\n".join(lines)}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
