from sqlalchemy import MetaData, Column, Integer, String, Unicode, Text, UnicodeText, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class EroticArticle(Base):
    __tablename__ = 'eroticarticle'
    id = Column(Integer, primary_key=True)
    viewcount = Column(Integer)
    title = Column(String(128), index=True)
    chinese_title = Column(Unicode(64))
    content = relationship('Paragraph', backref='eroticarticle', lazy='dynamic')  # Column(Text())
    translation = relationship('Translation', backref='eroticarticle', lazy='dynamic')
    category = Column(String(64))
    tags = Column(Text())
    url = Column(String(128))

    def get_content(self, rel):
        return [(para.para_idx, para.content) for para in getattr(self, rel)]

    def to_dict(self):
        cols = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        cols['tags'] = list(map(lambda x: x.strip(), self.tags.split('\xa0– ')))
        return cols

    def to_dict_w_details(self):
        cols = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        rels = {rel.key: self.get_content(rel.key) for rel in inspect(self.__class__).relationships}
        return {**cols, **rels}


class Paragraph(Base):
    __tablename__ = 'paragraph'
    id = Column(Integer, primary_key=True)
    art_id = Column(Integer, ForeignKey('eroticarticle.id'))
    para_idx = Column(Integer)
    content = Column(Text())


class Translation(Base):
    __tablename__ = 'translation'
    id = Column(Integer, primary_key=True)
    art_id = Column(Integer, ForeignKey('eroticarticle.id'))
    para_idx = Column(Integer)
    content = Column(UnicodeText())
