from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import LONGBLOB, SMALLINT, VARCHAR, INTEGER, TIMESTAMP
from sqlalchemy.sql import func, null

Base = declarative_base()

class StorageMeta(Base):
    __tablename__ = "bluemap_storage_meta"

    key = Column(VARCHAR(255), primary_key=True, nullable=False)
    value = Column(VARCHAR(255), nullable=True, default=null)

class Map(Base):
    __tablename__ = 'bluemap_map'

    id = Column(SMALLINT(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    map_id = Column(VARCHAR(255), unique=True, nullable=False, index=True)

class MapMeta(Base):
    __tablename__ = 'bluemap_map_meta'

    map = Column(SMALLINT(unsigned=True), ForeignKey('bluemap_map.id'), primary_key=True, nullable=False)
    key = Column(VARCHAR(255), primary_key=True, nullable=False)
    value = Column(LONGBLOB(), nullable=False)

class MapTile(Base):
    __tablename__= 'bluemap_map_tile'

    map = Column(SMALLINT(unsigned=True), ForeignKey('bluemap_map.id'), primary_key=True, nullable=False)
    type = Column(SMALLINT(unsigned=True), ForeignKey('bluemap_map_tile_type.id'), primary_key=True, nullable=False)
    x = Column(INTEGER(), nullable=False, primary_key=True)
    z = Column(INTEGER(), nullable=False, primary_key=True)
    compression = Column(SMALLINT(unsigned=True), ForeignKey('bluemap_map_tile_compression.id'), nullable=False)
    changed = Column(TIMESTAMP(), nullable=False, server_default=func.now(), server_onupdate=func.now())
    data = Column(LONGBLOB(), nullable=False)

class MapTileCompression(Base):
    __tablename__ = 'bluemap_map_tile_compression'

    id = Column(SMALLINT(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    compression = Column(VARCHAR(255), nullable=False, unique=True, index=True)

class MapTileType(Base):
    __tablename__ = 'bluemap_map_tile_type'

    id = Column(SMALLINT(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    type = Column(VARCHAR(255), nullable=False, unique=True, index=True)

