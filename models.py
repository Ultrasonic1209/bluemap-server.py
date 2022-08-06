from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import LONGBLOB, SMALLINT, VARCHAR, INTEGER, TIMESTAMP
from sqlalchemy.sql import func, null

Base = declarative_base()

class StorageMeta(Base):
    __tablename__ = "bluemap_storage_meta"

    key = Column(VARCHAR(255), primary_key=True, nullable=False)
    value = Column(VARCHAR(255), nullable=True, server_default=null)

class Map(Base):
    __tablename__ = 'bluemap_map'

    id = Column(SMALLINT(5, unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    map_id = Column(VARCHAR(255), unique=True, nullable=False)

class MapMeta(Base):
    __tablename__ = 'bluemap_map_meta'

    map = Column(SMALLINT(5, unsigned=True), primary_key=True, nullable=False)
    key = Column(VARCHAR(255), primary_key=True, nullable=False)
    value = Column(LONGBLOB(), nullable=False)

class MapTile(Base):
    __tablename__= 'bluemap_map_tile'

    map = Column(SMALLINT(5, unsigned=True), primary_key=True, nullable=False)
    type = Column(SMALLINT(5, unsigned=True), primary_key=True, nullable=False)
    x = Column(INTEGER(11), nullable=False, primary_key=True)
    z = Column(INTEGER(11), nullable=False, primary_key=True)
    compression = Column(SMALLINT(5, unsigned=True), nullable=False)
    changed = Column(TIMESTAMP(), nullable=False, server_default=func.now(), onupdate=func.now())
    data = Column(LONGBLOB(), nullable=False)

class MapTileCompression(Base):
    __tablename__ = 'bluemap_map_tile_compression'

    id = Column(SMALLINT(5, unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    compression = Column(VARCHAR(255), nullable=False, unique=True)

class MapTileType(Base):
    __tablename__ = 'bluemap_map_tile_type'

    id = Column(SMALLINT(5, unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    type = Column(VARCHAR(255), nullable=False, unique=True)

