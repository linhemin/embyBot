from sqlalchemy import Column, func, TIMESTAMP, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseMixin:
    """model的基类,所有model都必须继承"""
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    created = Column(TIMESTAMP(timezone=True), default=func.now(), comment="创建时间")
    updated = Column(TIMESTAMP(timezone=True), onupdate=func.now(), comment="更新时间")
