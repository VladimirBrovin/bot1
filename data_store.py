# импорты
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import config


class Base(DeclarativeBase): 
    pass


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


class DataBase():

    def __init__(self):
        self.create_db()
        self.engine = create_engine(config.db_url_object)
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def create_db(self):
        """Если БД отсутсвует - создадим"""
        engine = create_engine(config.db_url_object)
        if not database_exists(engine.url):
            create_database(engine.url)
    
    def to_bd(self, profile_id, worksheet_id):
        """добавлем просмотренные анкеты"""
        self.session.add(Viewed(profile_id=profile_id, worksheet_id=worksheet_id))
        self.session.commit()
    
    def from_bd(self, profile_id, worksheet_id):
        """проверяем анкету на просмотр"""
        return bool(self.session.query(Viewed).filter(Viewed.profile_id==profile_id, 
                                                Viewed.worksheet_id == worksheet_id).all())


if __name__ == '__main__':
    my_ = DataBase()
    # my_.to_bd(2, 2)
    print(my_.from_bd(2, 2))
    print(my_.from_bd(2, 21))