import sqlite3 as sl

# открываем файл с базой данных
con = sl.connect('not_finished_forms.db')
con2 = sl.connect('finished_forms.db')

with con:
    # получаем количество таблиц с нужным нам именем
    data = con.execute("select count(*) from sqlite_master where type='table' and name='not_finished_forms'")
    for row in data:
        # если таких таблиц нет
        if row[0] == 0:
            # создаём таблицу для товаров
            with con:
                con.execute("""
                    CREATE TABLE not_finished_forms (
                        key VARCHAR(1000) PRIMARY KEY,
                        user_id INTEGER,
                        town VARCHAR(1000),
                        purpose_of_trip VARCHAR(1000),
                        duration_of_trip VARCHAR(1000),
                        company VARCHAR(1000),
                        budget VARCHAR(1000),
                        lifestyle VARCHAR(1000),
                        count_visiting VARCHAR(1000),
                        transport VARCHAR(1000), 
                        contacts VARCHAR(1000), 
                        comments VARCHAR(1000)
            );
                """)

with con2:
    # получаем количество таблиц с нужным нам именем
    data = con2.execute("select count(*) from sqlite_master where type='table' and name='finished_forms'")
    for row in data:
        # если таких таблиц нет
        if row[0] == 0:
            # создаём таблицу для товаров
            with con2:
                con2.execute("""
                    CREATE TABLE finished_forms (
                        user_id INTEGER,
                        town VARCHAR(1000),
                        plan VARCHAR(1000)
            );
                """)

sql = 'INSERT INTO not_finished_forms (key, user_id, town, purpose_of_trip, duration_of_trip, company, budget,' \
      'lifestyle, count_visiting, transport, contacts, comments) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

sql2 = 'INSERT INTO finished_forms (user_id, town, plan) values(?, ?, ?)'

with con:
    data = con.execute("SELECT * FROM not_finished_forms")
    for row in data:
        print(row)

with con2:
    data = con2.execute("SELECT * FROM finished_forms")
    for row in data:
        print(row)
