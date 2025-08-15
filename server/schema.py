import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class UserWord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    word_id: int = Field(default=None, foreign_key="word.id")
    count: int = 0
    need_to_show: Optional[datetime.datetime] = Field(
        default=None,
        nullable=True,
    )
    created_at: Optional[datetime.datetime] = Field(
        default_factory=datetime.datetime.now, nullable=True
    )

    word: Optional["Word"] = Relationship(
        back_populates="user_words",
    )
    user: Optional["User"] = Relationship(
        back_populates="user_words",
    )


class UserDict(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    user_id: int = Field(default=None, foreign_key="user.id")
    dict_id: int = Field(default=None, foreign_key="dictionary.id")

    user: Optional["User"] = Relationship(
        back_populates="user_dicts",
    )
    dictionary: Optional["Dictionary"] = Relationship(
        back_populates="user_dicts",
    )


class WordDict(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="word.id")
    dict_id: int = Field(foreign_key="dictionary.id")

    word: Optional["Word"] = Relationship(back_populates="word_dicts")
    dictionary: Optional["Dictionary"] = Relationship(
        back_populates="word_dicts",
    )


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int

    user_words: List[UserWord] = Relationship(back_populates="user")
    user_dicts: List[UserDict] = Relationship(back_populates="user")
    words: List["Word"] = Relationship(
        back_populates="users",
        link_model=UserWord,
    )
    dictionaries: List["Dictionary"] = Relationship(
        back_populates="users", link_model=UserDict
    )


class Word(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    english: str
    russian: str

    word_dicts: List[WordDict] = Relationship(back_populates="word")
    user_words: List[UserWord] = Relationship(back_populates="word")
    dictionaries: List["Dictionary"] = Relationship(
        back_populates="words", link_model=WordDict
    )
    users: List["User"] = Relationship(
        back_populates="words",
        link_model=UserWord,
    )


class Dictionary(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    word_dicts: List[WordDict] = Relationship(back_populates="dictionary")
    user_dicts: List[UserDict] = Relationship(back_populates="dictionary")
    words: List[Word] = Relationship(
        back_populates="dictionaries",
        link_model=WordDict,
    )
    users: List[User] = Relationship(
        back_populates="dictionaries",
        link_model=UserDict,
    )


class About(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(default=None, nullable=True)


class ReviewWord(BaseModel):
    # not first time, reviewing
    user_id: int
    word_id: int
    count: int
    know_the_word: bool


class KnowWord(BaseModel):
    # first time
    user_id: int
    word_id: int
    know_the_word: bool


class UserDictionaryRequest(BaseModel):
    chat_id: int
    dict_id: int


class WordToLearnRequest(BaseModel):
    chat_id: int
    word_id: int
    know_the_word: bool


class WordToReviewRequest(BaseModel):
    chat_id: int
    word_id: int
    know_the_word: bool
