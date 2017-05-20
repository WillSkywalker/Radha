from sqlalchemy import MetaData, Column, Integer, String, Unicode, Text, UnicodeText, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


metadata = MetaData()
Base = declarative_base(metadata=metadata)


class EroticArticle(Base):
    __tablename__ = 'eroticarticle'
    id = Column(Integer, primary_key=True)
    title = Column(String(128), index=True)
    chinese_title = Column(Unicode(64))
    content = relationship('Paragraph', backref='eroticarticle', lazy='dynamic')  # Column(Text())
    translation = relationship('Translation', backref='eroticarticle', lazy='dynamic')
    category = Column(String(64))
    tags = Column(Text())
    url = Column(String(128))


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
