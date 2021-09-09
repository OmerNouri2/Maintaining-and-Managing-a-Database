# The Database
import atexit
import sqlite3
from Dto import Logistic
from Dto import Supplier
from Dto import Clinic
from Dto import Vaccine
from GenericDao import GenericDao


# The Repository
class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('database.db')
        self.logistic_dao = GenericDao(Logistic, self._conn)  # dao from type Logistic
        self.vaccine_dao = GenericDao(Vaccine, self._conn)  # dao from type Vaccine
        self.supp_dao = GenericDao(Supplier, self._conn)  # dao from type Supplier
        self.dao_clinic = GenericDao(Clinic, self._conn)  # dao from type Clinic




    def _close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        CREATE TABLE logistics (
            id INTEGER PRIMARY KEY,
            name STRING NOT NULL,
            count_sent INTEGER NOT NULL,
            count_received INTEGER NOT NULL
        );
        
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY,
            name STRING NOT NULL,
            logistic INTEGER REFERENCES logistics(id)
        );
        
        CREATE TABLE vaccines (
            id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            supplier INTEGER REFERENCES suppliers(id),
            quantity INTEGER NOT NULL
        );
        
        CREATE TABLE clinics (
            id INTEGER PRIMARY KEY,
            location STRING NOT NULL,
            demand INTEGER NOT NULL,
            logistic INTEGER REFERENCES logistics(id)
        );
    """)


# the repository singleton
repo = _Repository()
atexit.register(repo._close)
