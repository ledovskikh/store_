import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Basket(SqlAlchemyBase):
    __tablename__ = 'basket'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    product_id = sqlalchemy.Column(sqlalchemy.Integer)
    user = orm.relation('User')
