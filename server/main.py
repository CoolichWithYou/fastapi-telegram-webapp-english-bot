
from collections import defaultdict

from fastapi import FastAPI, HTTPException, APIRouter
import uvicorn
import datetime

from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware

from db import engine, create_db_and_tables
from schema import Dictionary, Word, User, UserWord, UserDict, WordDict, UserDictionaryRequest, WordToLearnRequest, \
    WordToReviewRequest, About
from sqlmodel import select

from sqlalchemy import func

def update_show_date(count: int, know_the_word: bool) -> tuple[datetime.datetime | None, int] | None:
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

router = APIRouter(prefix='/api')
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # или ["*"] для всех
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @router.post("/init_tables")
# async def init_tables():
#     '''create tables that featuresd in ./schema.py'''
#     create_db_and_tables()
#
# @router.post('/init_data')
# async def init_data():
#     '''fill all the tables with default data'''
#     with Session(engine) as session:
#         user = User(chat_id=1)
#
#         dictionary = Dictionary(title='Oxford 3000 A1')
#         session.add(user)
#         session.add(dictionary)
#         session.commit()
#
#         user_dict = UserDict(user_id=user.id, dict_id=dictionary.id)
#         session.add(user_dict)
#         session.commit()
#
#         word = Word(english='hello', russian='привет', dict_id=dictionary.id)
#         session.add(word)
#         session.commit()
#
#         word_dict = WordDict(word_id=word.id, dict_id=dictionary.id)
#         session.add(word_dict)
#         session.commit()
#
#         user_word = UserWord(user_id=user.id, word_id=word.id)
#         session.add(user_word)
#         session.commit()


@router.get('/learned_words')
async def get_learned_words(user_id: int):
    '''return learned words for 24 hours'''
    with Session(engine) as session:
        statement = select(UserWord).where(UserDict.user_id == user_id).where(UserWord.count != 7).where(UserWord.created_at < datetime.datetime.now() + datetime.timedelta(hours=24))
        recent_words = session.exec(statement).all()
        return {'learned_words_count': len(recent_words)}
@router.get('/dictionaries')
async def root():
    with Session(engine) as session:
        statement = select(Dictionary)
        dictionaries = session.exec(statement).all()
    return dictionaries

@router.post('/update_dictionary')
async def update_dictionary_status(user_dict: UserDictionaryRequest):
    with Session(engine) as session:
        statement = select(User).where(User.chat_id == user_dict.chat_id)
        user = session.exec(statement).one()

        statement = select(UserDict).where(UserDict.user_id == user.id).where(UserDict.dict_id == user_dict.dict_id)
        dictionary = session.exec(statement).first()
        character = ' '
        if dictionary:
            session.delete(dictionary)
        else:
            user_dict = UserDict(user_id=user.id, dict_id=user_dict.dict_id)
            session.add(user_dict)
            character = '✓'
        session.commit()
        return {'character': character}

@router.get('/user_dictionaries/{chat_id}')
async def get_user_dictionaries(chat_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.chat_id == chat_id)
        user = session.exec(statement).first()

        statement = (
            select(Dictionary, UserDict)
            .join(
                UserDict,
                (UserDict.dict_id == Dictionary.id) & (UserDict.user_id == user.id),
                isouter=True
            )
        )

        result = session.exec(statement).all()

        dictionaries = []
        for dict_obj, user_dict_obj in result:
            dictionaries.append({
                "id": dict_obj.id,
                "title": dict_obj.title,
                "selected": user_dict_obj is not None and user_dict_obj.user_id == user.id
            })
    return {'dicts': dictionaries}

@router.get('/user_words/{user_id}')
async def get_user_words(user_id: int):
    with Session(engine) as session:
        statement = select(UserWord).where(UserWord.user_id == user_id)
        words = session.exec(statement).all()
    return words

@router.get('/words')
async def root():
    with Session(engine) as session:
        statement = select(Word)
        words = session.exec(statement).all()
    return words


@router.get('/word_to_review')
async def update_word_status(chat_id: int):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.chat_id == chat_id)
        ).first()

        current_datetime = datetime.datetime.now()

        user_word = (
            session.exec(
                select(UserWord)
                .where(UserWord.user_id == user.id)
                .where(UserWord.count < 7)
                .where(UserWord.need_to_show < current_datetime)
            )
            .first()
        )

        if not user_word:
            return {"word": None}

        word = user_word.word
        dictionary = word.dictionaries[0] if word.dictionaries else None

        def escape(text: str) -> str:
            for ch in ["_", "*", "[", "`", "-"]:
                text = text.replace(ch, f"\\{ch}")
            return text

        word_data = word.model_dump()
        word_data["count"] = user_word.count
        word_data["dictionary"] = dictionary.title if dictionary else None
        word_data["english"] = escape(word_data["english"])
        word_data["russian"] = escape(word_data["russian"])
        return {'word': word_data}

@router.post('/user_dictionary')
async def add_dictionary(user_id: int, dict_id: int):
    with Session(engine) as session:
        new_user_dict = UserDict(user_id=user_id, dict_id=dict_id)
        session.add(new_user_dict)
        session.commit()

@router.delete('/user_dictionary')
async def remove_dictionary(user_id: int, dict_id: int):
    with Session(engine) as session:
        statement = select(UserDict).where(UserDict.user_id == user_id, UserDict.dict_id == dict_id)
        dictionary = session.exec(statement).one()
        session.delete(dictionary)
        session.commit()

@router.post('/word_to_review')
async def update_word_status(data: WordToReviewRequest):
    with Session(engine) as session:
        statement = select(User).where(User.chat_id == data.chat_id)
        user = session.exec(statement).first()

        statement = select(UserWord).where(UserWord.user_id == user.id).where(UserWord.word_id == data.word_id)
        results = session.exec(statement)
        user_word = results.first()
        need_to_show, count = update_show_date(user_word.count, data.know_the_word)
        user_word.need_to_show = need_to_show
        user_word.count = count

        session.add(user_word)
        session.commit()
        session.refresh(user_word)


@router.get('/word_to_learn')
async def word_to_learn(chat_id: int):

    with Session(engine) as session:
        statement = select(User).where(User.chat_id == chat_id)
        user = session.exec(statement).first()

        subquery = select(UserWord.word_id).where(UserWord.user_id == user.id)

        statement = (
            select(Word)
            .join(WordDict, Word.id == WordDict.word_id)
            .join(Dictionary, Dictionary.id == WordDict.dict_id)
            .join(UserDict, UserDict.dict_id == Dictionary.id)
            .where(UserDict.user_id == user.id)
            .where(Word.id.not_in(subquery))
        )
        results = session.exec(statement).first()
        if results:
            results = results.model_dump()
            results['english'] = results['english'].replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace(
                "`", "\\`").replace("-", "\\-")
            results['russian'] = results['russian'].replace("_", "\\_").replace("*", "\\*").replace(
                "[", "\\[").replace("`", "\\`").replace("-", "\\-")

        return {'word': results}

@router.post('/word_to_learn')
async def word_to_learn(data: WordToLearnRequest):
    with Session(engine) as session:
        statement = select(User).where(User.chat_id == data.chat_id)
        user = session.exec(statement).first()

        if data.know_the_word:
            session.add(UserWord(user_id=user.id, word_id=data.word_id, count=7))
        else:
            tuple_with_datetime = update_show_date(1, False)
            datetime_to_show = None
            if tuple_with_datetime:
                datetime_to_show, count = tuple_with_datetime
            session.add(UserWord(user_id=user.id, word_id=data.word_id, count=1, need_to_show=datetime_to_show))
        session.commit()


@router.post('/register_user/{chat_id}')
async def register_user(chat_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.chat_id == chat_id)
        user = session.exec(statement).first()
        if user is None:
            user = User(chat_id=chat_id)
            session.add(user)
            session.commit()


@router.get('/about')
async def about():
    with Session(engine) as session:
        statement = select(About)
        about = session.exec(statement).first()
        if not about:
            raise HTTPException(status_code=404)

        return {'about': about.text}

@router.get('/inactive_users')
async def inactive_users():
    with Session(engine) as session:
        cutoff = datetime.datetime.now() - datetime.timedelta(hours=24)

        stmt = (
            select(User)
            .outerjoin(UserWord, (User.id == UserWord.user_id) & (UserWord.created_at > cutoff))
            .group_by(User.id)
            .having(func.count(UserWord.id) == 0)
        )

        return session.exec(stmt).all()

@router.get('/statistics/{chat_id}')
async def statistics(chat_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.chat_id == chat_id)
        user = session.exec(statement).first()

        statement = select(UserWord).where(UserWord.user_id == user.id).where(UserWord.created_at > datetime.datetime.now() - datetime.timedelta(days=30))
        results = session.exec(statement).all()

        daily_counts = defaultdict(int)
        for dt in results:
            day = dt.created_at.date()
            daily_counts[day] += 1

        max_stars = 5

        now = datetime.datetime.now().date()
        start_date = now - datetime.timedelta(days=10)

        date_range = [start_date + datetime.timedelta(days=x) for x in range(11)]

        lines = []

        lines.append(f"Your learning words statistics:\n")

        for i in range(max_stars, 0, -1):
            line = []
            for date in date_range:
                count = min(daily_counts.get(date, 0), max_stars)
                line.append('---*' if count >= i else '----')
            lines.append(' '.join(line))

        date_labels = [d.strftime('%d') for d in date_range]
        lines.append('  '.join(date_labels))

        lines.append(f"\nRecord counts from")
        lines.append(f"{start_date} to {now}\n")

        return {'stats': '\n'.join(lines)}

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)