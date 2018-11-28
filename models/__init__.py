from app import app

# Database
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Mixin for generic model attributes
class idMixin(object):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

# ManyToMany relationship between an ETF and its assets.
asset_etf = db.Table('asset_etf', db.Model.metadata,
    db.Column('left_id', db.Integer, db.ForeignKey('asset.id')),
    db.Column('right_id', db.Integer, db.ForeignKey('asset.id'))
)

# Asset Model
class Asset(idMixin,db.Model):
    __tablename__ = 'asset'
    symbol = db.Column(db.String(length=50), index=True)
    source = db.Column(db.String(length=50), index=True)
    history = db.relationship("History", back_populates="asset", uselist=False)
    basket = db.relationship("Asset",
        secondary= asset_etf,
        primaryjoin=('asset.c.id==asset_etf.c.left_id'),
        secondaryjoin=('asset.c.id==asset_etf.c.right_id'),
        backref=db.backref("etfs"),
        uselist=True
    )
    def __repr__(self): return "<Asset(symbol='%s')>" % (self.symbol)


# History Model
class History(idMixin, db.Model):
    __tablename__ = 'history'
    asset_id = db.Column(db.Integer,db.ForeignKey('asset.id'), index=True)
    asset = db.relationship("Asset", back_populates="history", uselist=False)
    date = db.Column( db.DateTime(), index=True )
    vwap = db.Column( db.Numeric() )
    high = db.Column( db.Numeric() )
    low = db.Column( db.Numeric() )
    volume = db.Column( db.Numeric() )
    open = db.Column( db.Numeric() )
    close = db.Column( db.Numeric() )
    def __repr__(self): return "<History(asset='%s', date='%s', price='%s')>" % (self.asset, self.date, self.vwap)

# Create tables if necessary
db.create_all()