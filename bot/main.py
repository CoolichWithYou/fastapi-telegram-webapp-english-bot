import asyncio
import json

from aiogram import Bot, Dispatcher, Router
from aiogram.client.session import aiohttp
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import (Dialog, DialogManager, ShowMode, Window,
                            setup_dialogs)
from aiogram_dialog.widgets.kbd import (Button, Cancel, Column, Row, Select,
                                        Start)
from aiogram_dialog.widgets.text import Const, Format
from settings import get_settings

settings = get_settings()


class MainMenu(StatesGroup):
    START = State()


class Revising(StatesGroup):
    START = State()


class Learning(StatesGroup):
    START = State()


class Dictionaries(StatesGroup):
    START = State()


class Statistics(StatesGroup):
    START = State()


class About(StatesGroup):
    START = State()


EXTEND_BTN_ID = "extend"

main_menu = Dialog(
    Window(
        Format(
            "Hello, {event.from_user.username}. \n\n"
            'don\'t know how to use? Visit "About"'
        ),
        Row(
            Start(Const('Dictionaries'), id='dictionaries', state=Dictionaries.START),
            Start(Const('Statistics'), id='statistics', state=Statistics.START)
        ),
        Row(
            Start(Const("Learning"), id="learning", state=Learning.START),
            Start(Const('Repetition'), id='repetition', state=Revising.START),
        ),
        Start(Const("About"), id="about", state=About.START),
        state=MainMenu.START
    )
)


async def get_data(dialog_manager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/user_dictionaries/{user_id}'
        ) as response:
            response_text = await response.text()
            json_response = json.loads(response_text)
            if json_response:
                for dictionary in json_response['dicts']:
                    dictionary['selected'] = '[✓]' if dictionary['selected'] else '[ ]'
            return json_response


async def get_stats(dialog_manager, **kwargs):
    chat_id = dialog_manager.event.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/statistics/{chat_id}') as response:
            response_text = await response.text()
            json_response = json.loads(response_text)
            return json_response


async def get_about(dialog_manager, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/about') as response:
            response_text = await response.text()
            json_response = json.loads(response_text)
            return json_response


async def update_dictionaries(dict_id: int, chat_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/update_dictionary',
                                json={'dict_id': dict_id, 'chat_id': chat_id}) as response:
            pass


async def on_select_clicked(callback: CallbackQuery,
                            widget,
                            dialog_manager: DialogManager,
                            item_id: str):
    # item_id — это id словаря, который ты передашь как str

    dict_id = int(item_id)
    chat_id = callback.from_user.id
    # Тут обновляешь состояние БД:
    await update_dictionaries(dict_id, chat_id)

    # Перерисовываешь окно:
    # await dialog_manager.re
    await dialog_manager.show()


dictionaries = Dialog(
    Window(
        Format("Your dictionaries:"),
        Column(Select(
            text=Format("{item[title]} {item[selected]}"),
            items="dicts",
            item_id_getter=lambda item: str(item["id"]),
            id="dicts_select",
            on_click=on_select_clicked,

        )),
        Cancel(text=Const("Go to menu"), id="save"),
        state=Dictionaries.START,
        getter=get_data,
    )
)

statistics = Dialog(
    Window(
        Format(
            "{stats}"
        ),
        Cancel(text=Const("Go to menu"), id="save"),
        getter=get_stats,
        state=Statistics.START,
    )
)

about = Dialog(
    Window(
        Format(
            "{about}"
        ),
        Cancel(text=Const("Go to menu"), id="save"),
        getter=get_about,
        state=About.START,
    )
)


async def review_word(dialog_manager, **kwargs):
    chat_id = dialog_manager.event.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/word_to_review',
                params={'chat_id': chat_id}
        ) as response:
            word = await response.text()
            json_word = json.loads(word)
            dialog_manager.dialog_data["word"] = json_word

            if json_word:
                return {
                    "english": json_word['word']['english'],
                    "russian": json_word['word']['russian'],
                    "id": json_word['word']['id'],
                    "is_empty": False
                }
            else:
                return {
                    "english": "There are no words to learn yet",
                    "russian": " ",
                    "id": -1,
                    "is_empty": True
                }


async def learn_word(dialog_manager, **kwargs):
    chat_id = dialog_manager.event.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/word_to_learn',
                               params={'chat_id': chat_id}) as response:
            word = await response.text()
            json_word = json.loads(word)
            dialog_manager.dialog_data["word"] = json_word

            if json_word:
                return {
                    "english": json_word['word']['english'],
                    "russian": json_word['word']['russian'],
                    "id": json_word['word']['id'],
                    "is_empty": False
                }
            else:
                return {
                    "english": "There are no words to learn yet",
                    "russian": " ",
                    "id": -1,
                    "is_empty": True
                }


async def on_know_clicked(callback: CallbackQuery, button, dialog_manager: DialogManager):
    user_id = callback.from_user.id
    word = dialog_manager.dialog_data.get("word")

    if word:
        word_str = json.dumps(word)
        word_json = json.loads(word_str)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/word_to_review',
                    json={
                        'chat_id': user_id,
                        'word_id': word_json['word']['id'],
                        'know_the_word': True if callback.data == 'know' else False
                    }
            ) as response_post:
                pass  # you could log or handle post response if needed

    # Обновляем окно
    await dialog_manager.show()


async def clicked_learn(callback: CallbackQuery, button, dialog_manager: DialogManager):
    user_id = callback.from_user.id
    word = dialog_manager.dialog_data.get("word")

    if word:
        word_str = json.dumps(word)
        word_json = json.loads(word_str)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/word_to_learn',
                    json={
                        'chat_id': user_id,
                        'word_id': word_json['word']['id'],
                        'know_the_word': True if callback.data == 'know' else False
                    }
            ) as response_post:
                pass  # you could log or handle post response if needed

    # Обновляем окно
    await dialog_manager.show()


revising = Dialog(
    Window(
        Format(
            "{russian}\n\n"
            "{english}\n"
        ),
        Row(
            Button(
                text=Const('Know the word'),
                id='know',
                on_click=on_know_clicked,
                when=lambda data, *_: not data.get("is_empty")
            ),
            Button(
                text=Const("Don't know it"),
                id="dont",
                on_click=on_know_clicked,
                when=lambda data, *_: not data.get("is_empty")
            ),
        ),
        Row(
            Cancel(text=Const("Stop repetition"), id="save"),
        ),
        getter=review_word,
        state=Revising.START,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
)

learning = Dialog(
    Window(
        Format(
            'Learning\n\n'
            "{english}\n"
            "||{russian}||\n"
        ),
        Row(
            Button(
                text=Const('Know the word'),
                id='know',
                on_click=clicked_learn,
                when=lambda data, *_: not data.get("is_empty")
            ),
            Button(
                text=Const("Don't know it"),
                id="dont",
                on_click=clicked_learn,
                when=lambda data, *_: not data.get("is_empty")
            ),
        ),
        Row(
            Cancel(text=Const("Stop learning"), id="save"),
        ),
        getter=learn_word,
        state=Learning.START,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
)

router = Router()


@router.message(CommandStart())
async def start(message: Message, dialog_manager: DialogManager):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/register_user/{message.chat.id}') as response:
            pass

    await dialog_manager.start(MainMenu.START)


async def main():
    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher()
    dp.include_router(main_menu)
    dp.include_router(revising)
    dp.include_router(learning)
    dp.include_router(dictionaries)
    dp.include_router(statistics)
    dp.include_router(about)
    dp.include_router(router)
    setup_dialogs(dp)

    await dp.start_polling(bot)


asyncio.run(main())
