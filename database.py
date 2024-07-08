from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URI = 'sqlite:///bank_system.db'
Base = declarative_base()
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
db_session = Session()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Loan(Base):
    __tablename__ = 'loans'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    principal = Column(Float)
    interest = Column(Float)
    total_amount = Column(Float)
    loan_period = Column(Integer)
    emi_amount = Column(Float)
    remaining_amount = Column(Float)
    emis_left = Column(Integer)
    customer = relationship('Customer')

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey('loans.id'))
    payment_type = Column(String)
    amount = Column(Float)
    date = Column(DateTime)
    loan = relationship('Loan')

def init_db():
    Base.metadata.create_all(engine)
