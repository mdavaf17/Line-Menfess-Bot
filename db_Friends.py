import re
from sqlalchemy import create_engine


URI = "mysql+pymysql://<your_username>:<your_mysql_password>@<your_mysql_hostname>/<your_database_name>"


def createTable():
    engine = create_engine(URI, pool_recycle=90)
    with engine.connect() as conn:
        try:
            # conn.execute("CREATE TABLE IF NOT EXISTS Friends (ID VARCHAR(50), IDL VARCHAR(50), NIM VARCHAR(10) PRIMARY KEY, UNAME VARCHAR(20))")
            # conn.execute("CREATE TABLE IF NOT EXISTS Registers (ID VARCHAR(50), IDL VARCHAR(50), NIM VARCHAR(10) PRIMARY KEY, UNAME VARCHAR(20))")
            conn.execute("CREATE TABLE IF NOT EXISTS `Groups` (GID VARCHAR(50) PRIMARY KEY, GUNAME VARCHAR(10), IDREG VARCHAR(50))")
            return "Success"
        except Exception as error:
            return error
        conn.close()
    engine.dispose()

def insertTable(TABLE, ID, IDL, NIM, UNAME):
    engine = create_engine(URI, pool_recycle=90)
    with engine.connect() as conn:
        try:
            conn.execute("INSERT INTO {} (ID, IDL, NIM, UNAME) VALUES ('{}', '{}', '{}', '{}')".format(TABLE, ID, IDL, NIM, UNAME))
            return "Success"
        except Exception as error:
            return error
        conn.close()
    engine.dispose()


def insertGroups(GID, GUNAME, IDREG):
    engine = create_engine(URI, pool_recycle=90)
    with engine.connect() as conn:
        try:
            conn.execute("INSERT INTO `Groups` (GID, GUNAME, IDREG) VALUES ('{}', '{}', '{}')".format(GID, GUNAME, IDREG))
            return "Success"
        except Exception as error:
            return error
        conn.close()
    engine.dispose()


def readTable(TABLE):
    engine = create_engine(URI, pool_recycle=90)
    with engine.connect() as conn:
        # Initialize the result variable
        result = ""
        result_set = conn.execute("SELECT * FROM {}".format(TABLE))
        # Add a string from each row of data and break line (enter)
        for r in result_set:
            result += (str(r) + "\n")
        # If the length of the result var is not 0 or ""
        if len(result)>0:
            return result
        else:
            return "Empty"
        conn.close()
    engine.dispose()


def findTable(TABLE, COL, VAL):
    engine = create_engine(URI, pool_recycle=90)
    with engine.connect() as conn:
        # Initialize the result variable
        result = ""
        result_set = conn.execute("SELECT * FROM {} WHERE {}='{}'".format(TABLE, COL, VAL))
        # Updating the result variable of the data object
        for r in result_set:
            result = str(r)
        # If the length of the result var is not 0 or ""
        if len(result)>0:
            return result
        else:
            return False
        conn.close()
    engine.dispose()


def deleteTable(TABLE, COL, VAL):
    engine = create_engine(URI, pool_recycle=90)
    with engine.connect() as conn:
        try:
            conn.execute("DELETE FROM {} WHERE {}='{}'".format(TABLE, COL, VAL))
            return "Success"
        except Exception as error:
            return error
        conn.close()
    engine.dispose()


def lengthRow(TABLE):
    engine = create_engine(URI, pool_recycle=90)
    with engine.connect() as conn:
        # Initialize the result variable
        result = ""
        result_set = conn.execute("SELECT COUNT(*) FROM {}".format(TABLE))
        # Updating the result variable of the data object
        for r in result_set:
            result = str(r)
        # Removes all characters except numbers
        result = re.sub('[^0-9]', '', result)
        return int(result)
        conn.close()
    engine.dispose()