import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# создание экземпляра declarative_base
Base = declarative_base()

# здесь добавим классы


# мы создаем класс Book наследуя его из класса Base.
class News(Base):
    __tablename__ = 'new'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    author = Column(String(250), nullable=False)
    genre = Column(String(250))
    text = Column(String(1000))


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(150), nullable=False)
    password = Column(String(100), nullable=False)


# создает экземпляр create_engine в конце файла
engine = create_engine('sqlite:///news-collection.db')

Base.metadata.create_all(engine)
