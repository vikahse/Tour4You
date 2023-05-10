import sqlite3


def get_user(user):
    con = sqlite3.connect("users.db")
    curs = con.cursor()
    print(1)
    pass
