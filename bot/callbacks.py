from aiogram.filters.callback_data import CallbackData


class MyCallback(CallbackData, prefix="my"):
    dict_id: int
    user_id: int
    dict_title: str
    action: str

class MyCallbackLearn(CallbackData, prefix="ln"):
    user_id: int
    word_id: int
    know_the_word: bool
    action: str

class MyCallBackReview(CallbackData, prefix="rv"):
    user_id: int
    word_id: int
    know_the_word: bool
    action: str
