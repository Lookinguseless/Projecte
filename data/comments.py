import sqlalchemy

from .db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    content = sqlalchemy.Column(sqlalchemy.String)
    parent = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts'))
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user'))
