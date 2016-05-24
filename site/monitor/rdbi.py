from __future__ import print_function
import os
import sys
base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(base_dir))
rtp_dir = os.path.dirname(os.path.dirname(base_dir))
lib_dir = os.path.join(rtp_dir, 'lib')
sys.path.append(lib_dir)
import dbi
import decimal
import logging
from contextlib import contextmanager
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import datetime
import logging
try:
    import configparser
except:
    import ConfigParser as configparser

logger = logging.getLogger('librarian')
Base = declarative_base()

def decimal_default(obj):
    '''
    fixes decimal issue with json module

    Parameters
    ----------
    obj (object)

    Returns
    -------
    object: float version of decimal object
    '''
    if isinstance(obj, decimal.Decimal):
        return float(obj)

class DictFix(object):
    '''
    superclass for all SQLAlchemy Table objects
    allows access to object row dictionary

    Methods
    -------
    to_dict | creates python dict of fields from sqlalchemy object
    '''
    def to_dict(self):
        '''
        convert object to dict

        Returns
        -------
        dict: table attributes
        '''
        try:
            new_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
            return new_dict
        except(exc.InvalidRequestError):
            return None


#class Neighbors(dbi.neighbors, DictFix):
#    pass

class Observation_(dbi.Observation, DictFix):
    pass

class File_(dbi.File, DictFix):
    pass

class Log_(dbi.Log, DictFix):
    pass

class Still_(dbi.Still, DictFix):
    pass

class DataBaseInterface(object):
    '''
    Database Interface
    base class used to connect to databases

    Methods
    -------
    session_scope | context manager for session connection to database
    drop_db | drops all tables from database
    create_table | creates individual table in database
    add_entry | adds entry object to database
    add_entry_dict | adds entry to database using dict as kwarg
    get_entry | gets database object
    set_entry | updates database entry field with new value
    set_entry_dict | updates database entry fields with new values using input dict
    '''
    def __init__(self, configfile='~/still_shredder.cfg'):
        '''
        Connect to the database and make a session creator
        superclass of DBI for databases

        Parameters
        ----------
        configfile | Optional[str]: configuration file --defaults to ~/still_shredder.cfg
        '''
        if configfile is not None:
            config = configparser.ConfigParser()
            configfile = os.path.expanduser(configfile)
            if os.path.exists(configfile):
                logger.info(' '.join(('loading file', configfile)))
                config.read(configfile)
                try:
                    self.dbinfo = config._sections['dbinfo']
                except:
                    self.dbinfo = config['dbinfo']
                try:
                    self.dbinfo['dbpasswd'] = self.dbinfo['dbpasswd'].decode('string-escape')
                except:
                    self.dbinfo['dbpasswd'] = bytes(self.dbinfo['dbpasswd'], 'ascii').decode('unicode_escape')
            else:
                logging.info(' '.join((configfile, 'Not Found')))
        try:
            connect_string = 'mysql://{dbuser}:{dbpasswd}@{dbhost}:{dbport}/{dbname}'
            self.engine = create_engine(connect_string.format(**self.dbinfo), pool_size=20, max_overflow=40)
        except:
            connect_string = 'mysql+mysqldb://{dbuser}:{dbpasswd}@{dbhost}:{dbport}/{dbname}'
            self.engine = create_engine(connect_string.format(**self.dbinfo), pool_size=20, max_overflow=40)

        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self):
        '''
        creates a session scope
        can use 'with'

        Returns
        -------
        object: session scope to be used to access database with 'with'
        '''
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def drop_db(self, Base):
        '''
        drops the tables in the database.

        Parameters
        ----------
        Base | object: base object for database
        '''
        Base.metadata.bind = self.engine
        Base.metadata.drop_all()

    def create_table(Table):
        '''
        creates a table in the database.

        Parameters
        ----------
        Table | object: table object
        '''
        Table.__table__.create(bind=self.engine)

    def add_entry(self, s, ENTRY):
        '''
        adds entry to database and commits
        does not add if duplicate found

        Parameters
        ----------
        s | object: session object
        ENTRY | object: entry object
        '''
        try:
            s.add(ENTRY)
            s.commit()
        except (exc.IntegrityError):
            s.rollback()
            print('Duplicate entry found ... skipping entry')

    def add_entry_dict(self, mod_name, s, TABLE, entry_dict):
        '''
        create a new entry.

        Parameters
        ----------
        mod_name | str: name of module to access models
        s | object: session object
        TABLE | str: table name
        entry_dict | dict: dict of attributes for object
        '''
        table = getattr(sys.modules[mod_name], TABLE)
        ENTRY = table(**entry_dict)
        self.add_entry(s, ENTRY)

    def get_entry(self, mod_name, s, TABLE, unique_value):
        '''
        retrieves any object.
        Errors if there are more than one of the same object in the db. This is bad and should
        never happen

        Parameters
        ----------
        mod_name | str: name of module to access models
        s | object: session object
        TABLE | str: table name
        unique_value | int/float/str: primary key value of row

        Returns
        -------
        object: table object
        '''
        table = getattr(sys.modules[mod_name], TABLE)
        try:
            ENTRY = s.query(table).get(unique_value)
        except:
            return None

        return ENTRY

    def set_entry(self, s, ENTRY, field, new_value):
        '''
        sets the value of any entry

        Parameters
        ----------
        s | object: session object
        ENTRY | object: entry object
        field | str: field to be changed
        new_value | int/float/str: value to change field in entry to
        '''
        setattr(ENTRY, field, new_value)
        self.add_entry(s, ENTRY)

    def set_entry_dict(self, s, ENTRY, entry_dict):
        '''
        sets values of any entry

        Parameters
        ----------
        s | object: session object
        ENTRY | object: entry object
        entry_dict | dict: dict of attributes for object
        '''
        for field, new_value in entry_dict.items():
            setattr(ENTRY, field, new_value)
        self.add_entry(s, ENTRY)
