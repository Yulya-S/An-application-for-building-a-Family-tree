import sqlite3
from os import mkdir
from os.path import exists

if not exists('./base'):
    mkdir('./base')


class Data_base():
    def __init__(self, base_name: str):
        self.db = sqlite3.connect(f'./base/{base_name}.db')
        self.cursor = self.db.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text VARCHAR(255),
                gender BOOLEAN ); """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS last_names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                male VARCHAR(255),
                female VARCHAR(255) ); """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text VARCHAR(255) ); """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text VARCHAR(255),
                country_id INTEGER,
                FOREIGN KEY (`country_id`) REFERENCES `countries`(`id`) ); """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_id INTEGER,
                last_name_id INTEGER,
                birthday_year INTEGER,
                birthday DATE,
                alive BOOLEAN,
                death_year INTEGER,
                date_of_death DATE,
                biography VARCHAR(255),
                phone_number VARCHAR(255),
                сity_of_birth_id INTEGER,
                image VARCHAR(255),
                FOREIGN KEY (`name_id`) REFERENCES `names`(`id`),
                FOREIGN KEY (`last_name_id`) REFERENCES `last_names`(`id`),
                FOREIGN KEY (`сity_of_birth_id`) REFERENCES `cites`(`id`) ); """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS marriages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spouse_1_id INT,
                spouse_2_id INT,
                year INTEGER,
                date DATE,
                actual BOOLEAN,
                FOREIGN KEY (`spouse_1_id`) REFERENCES `persons`(`id`),
                FOREIGN KEY (`spouse_2_id`) REFERENCES `persons`(`id`) ); """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS communications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INT,
                parent_1_id INT,
                parent_2_id INT,
                type_of_communication BOOLEAN,
                FOREIGN KEY (`person_id`) REFERENCES `persons`(`id`),
                FOREIGN KEY (`parent_1_id`) REFERENCES `persons`(`id`),
                FOREIGN KEY (`parent_2_id`) REFERENCES `persons`(`id`) ); """)


# удаление последней строки без увеличения счетчика id
def delete_last_element(db, id: int, table_name: str):
    db.cursor.execute("SELECT seq FROM `sqlite_sequence` WHERE name = ?", (table_name,))
    count = db.cursor.fetchall()
    if len(count) != 0 and id == count[0][0]:
        db.cursor.execute("UPDATE `sqlite_sequence` SET seq = ? WHERE name = ?", (int(count[0][0]) - 1, table_name))
        db.db.commit()


# добавление нового имени
def append_names(db, text, gender):
    db.cursor.execute(f"INSERT INTO `names` (`text`, `gender`) VALUES (?,?)", (text, gender))
    db.db.commit()


# получить все существующие в базе имена
def all_names(db, gender):
    db.cursor.execute("SELECT text FROM `names` WHERE gender = ?", (gender,))
    return [i[0] for i in db.cursor.fetchall()]


# поиск имени по его id
def find_name(db, name_id: int):
    db.cursor.execute("SELECT text, gender FROM `names` WHERE id = ?", (name_id,))
    result = db.cursor.fetchall()
    return result[0] if len(result) > 0 else None


# поиск id имени
def find_name_by_text(db, text: str, gender: bool):
    db.cursor.execute("SELECT id FROM `names` WHERE text = ? and gender = ?", (text, gender))
    result = db.cursor.fetchall()
    return result[0] if len(result) > 0 else None


# поиск гендера по id
def find_gender_by_id(db, person_id: int):
    db.cursor.execute("SELECT * FROM `persons` WHERE id = ?", (person_id,))
    result = db.cursor.fetchall()
    if len(result) > 0:
        db.cursor.execute("SELECT gender FROM `names` WHERE id = ?", (result[0][1],))
        result = db.cursor.fetchall()
        return result[0] if len(result) > 0 else None


# поиск всех мужских имен
def find_male_names(db):
    db.cursor.execute("SELECT `text` FROM `names` WHERE gender = 1")
    result = db.cursor.fetchall()
    return [i[0] for i in result]


# поиск всех женских имен
def find_female_names(db):
    db.cursor.execute("SELECT `text` FROM `names` WHERE gender = 0")
    result = db.cursor.fetchall()
    return [i[0] for i in result]


# очистка не использующихся в базе имен
def clear_names(db):
    pass


# добавление новой фамилии
def append_last_names(db, male, female):
    db.cursor.execute(f"INSERT INTO `last_names` (`male`, `female`) VALUES (?,?)", (male, female))
    db.db.commit()


# получить все фамилии в мужском варианте
def all_male_last_names(db):
    db.cursor.execute("SELECT male FROM `last_names`")
    return [i[0] for i in db.cursor.fetchall()]


# получить все фамилии в фенском варианте
def all_female_last_names(db):
    db.cursor.execute("SELECT female FROM `last_names`")
    return [i[0] for i in db.cursor.fetchall()]


# поиск фамилии по её id
def find_last_name(db, last_name_id: int):
    db.cursor.execute("SELECT male, female FROM `last_names` WHERE id = ?", (last_name_id,))
    result = db.cursor.fetchall()
    return result[0] if len(result) > 0 else None


# поиск id фамилии
def find_last_name_by_text(db, text: str):
    db.cursor.execute("SELECT id FROM `last_names` WHERE ? IN (male, female)", (text,))
    result = db.cursor.fetchall()
    return result[0] if len(result) > 0 else None


# добавление новой страны
def append_country(db, country):
    db.cursor.execute(f"INSERT INTO `countries` (`text`) VALUES (?);", (country,))
    db.db.commit()


# добавление нового города
def append_city(db, country_id, city):
    db.cursor.execute(f"INSERT INTO `cites` (`country_id`, `text`) VALUES (?, ?);", (country_id, city))
    db.db.commit()


# поиск страны и города по id
def find_country_and_city_by_id(db, city_id):
    db.cursor.execute("SELECT country_id, text FROM `cites` WHERE id = ?", (city_id,))
    city = db.cursor.fetchall()
    if len(city) > 0:
        db.cursor.execute("SELECT text FROM `countries` WHERE id = ?", (city[0][0],))
        country = db.cursor.fetchall()
        return country[0][0], city[0][1]
    return "", ""


# поиск id страны и города
def find_country_and_city(db, country, city):
    if country != "" and city != "":
        db.cursor.execute("SELECT id FROM `countries` WHERE text = ?", (country,))
        country_id = db.cursor.fetchall()
        if len(country_id) == 0:
            append_country(db, country)
            db.cursor.execute("SELECT id FROM `countries` WHERE text = ?", (country,))
            country_id = db.cursor.fetchall()
        country_id = country_id[0][0]
        db.cursor.execute("SELECT id FROM `cites` WHERE country_id = ? AND text = ?", (country_id, city))
        city_id = db.cursor.fetchall()
        if len(city_id) == 0:
            append_city(db, country_id, city)
            db.cursor.execute("SELECT id FROM `cites` WHERE country_id = ? AND text = ?", (country_id, city))
            city_id = db.cursor.fetchall()
        city_id = city_id[0][0]
        return city_id
    return None


# добавить новую персону
def append_person(db, name_id: str, last_name_id: str, birthday_year, birthday, alive: bool,
                  death_year, death_date, biography: str, information, image: str):
    inform = []
    for i in information:
        inform.append(i.get_text)
    city_id = find_country_and_city(db, inform[1], inform[2])
    db.cursor.execute("""INSERT INTO `persons` (`name_id`, `last_name_id`, `birthday_year`, `birthday`, `alive`,
                        `death_year`, `date_of_death`, `biography`, `phone_number`, сity_of_birth_id, image)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                      (name_id[0], last_name_id[0], birthday_year, birthday, alive, death_year, death_date,
                       biography, inform[0], city_id, image))
    db.db.commit()


# изменение персоны
def update_person(db, person_id, name_id: str, last_name_id: str, birthday_year, birthday, alive: bool,
                  death_year, death_date, biography: str, information, image: str):
    inform = []
    for i in information:
        inform.append(i.get_text)
    city_id = find_country_and_city(db, inform[1], inform[2])
    db.cursor.execute("""UPDATE `persons` SET name_id = ?, last_name_id = ?, birthday_year = ?, birthday = ?,
                        alive = ?, death_year = ?, date_of_death = ?, biography = ?, phone_number = ?,
                        сity_of_birth_id = ?, image = ? WHERE id = ?""",
                      (name_id[0], last_name_id[0], birthday_year, birthday, alive, death_year, death_date,
                       biography, inform[0], city_id, image, person_id))
    db.db.commit()


# поиск всех персон
def all_person_id(db):
    db.cursor.execute("SELECT id FROM `persons`;")
    result = db.cursor.fetchall()
    return [i[0] for i in result] if len(result) > 0 else []


# поиск персон по id
def find_person(db, person_id: int):
    db.cursor.execute("SELECT * FROM `persons` WHERE id = ?", (person_id,))
    result = db.cursor.fetchall()
    return result[0] if len(result) > 0 else None


# поиск персон без связей
def find_person_without_communication(db):
    db.cursor.execute("SELECT spouse_1_id, spouse_2_id  FROM `marriages`")
    result = db.cursor.fetchall()
    ids = []
    if len(result) > 0:
        for i in result:
            ids.append(i[0])
            ids.append(i[1])
    db.cursor.execute("SELECT person_id, parent_1_id, parent_2_id  FROM `communications`")
    result = db.cursor.fetchall()
    if len(result) > 0:
        for i in result:
            if i[0] not in ids:
                ids.append(i[0])
            if i[1] not in ids and i[1] is not None:
                ids.append(i[1])
            if i[2] not in ids and i[2] is not None:
                ids.append(i[2])
    db.cursor.execute("SELECT id FROM `persons`")
    result = db.cursor.fetchall()
    if len(result) > 0:
        for i in range(len(result)):
            result[i] = result[i][0]
    for i in ids:
        if i in result:
            result.pop(result.index(i))
    return result


# поиск первой персоны в базе данных
def find_first(db):
    db.cursor.execute("SELECT * FROM `communications`")
    result = db.cursor.fetchall()
    if len(result) > 0:
        return result[0][1]
    db.cursor.execute("SELECT * FROM `marriages`")
    result = db.cursor.fetchall()
    return result[0][1] if len(result) > 0 else 0


# добавить новую или изменить существующую связь
def append_communications(db, person_id: int, parent_id: int, type_of_communication: bool):
    par = find_parents(db, person_id)
    if par:
        if not par[0]:
            db.cursor.execute("""UPDATE `communications` SET parent_1_id = ? WHERE person_id = ?""",
                              (parent_id, person_id))
        else:
            db.cursor.execute("""UPDATE `communications` SET parent_2_id = ? WHERE person_id = ?""",
                              (parent_id, person_id))
    else:
        db.cursor.execute("""INSERT INTO `communications` (`person_id`, `parent_1_id`, `type_of_communication`)
                            VALUES (?,?,?)""", (person_id, parent_id, type_of_communication))
    db.db.commit()


# изменение связи
def update_communications(db, person_id: int, parent_id: int, type_of_communication: bool):
    db.cursor.execute("""SELECT id FROM `communications` WHERE ? in (parent_1_id, parent_2_id) AND
                        person_id = ?;""", (parent_id, person_id))
    result = db.cursor.fetchall()
    if len(result) > 0:
        db.cursor.execute("UPDATE `communications` SET `type_of_communication` = ? WHERE id = ?;",
                          (type_of_communication, result[0][0]))
        db.db.commit()


# получить все связи
def all_communications(db):
    db.cursor.execute("""SELECT person_id, parent_1_id, parent_2_id FROM `communications`;""")
    return [i for i in db.cursor.fetchall()]


# удаление персоны из базы данных
def delete_person(db, id):
    db.cursor.execute("DELETE FROM persons WHERE id = ?;", (id,))
    db.db.commit()


# поиск связи типа родитель для персоны
def find_parents(db, person_id: int):
    db.cursor.execute("""SELECT parent_1_id, parent_2_id, type_of_communication FROM `communications`
                        WHERE person_id = ?""", (person_id,))
    result = db.cursor.fetchall()
    return result[0] if len(result) > 0 else None


# поиск связи типа детей для персоны
def find_children(db, person_id: int):
    db.cursor.execute("""SELECT person_id FROM `communications`
                        WHERE ? in (parent_1_id, parent_2_id)""", (person_id,))
    result = db.cursor.fetchall()
    return [i[0] for i in result] if len(result) > 0 else []


# поиск связи типа "сиблинги" для персоны
def find_sibling(db, parent_1_id: int, parent_2_id: int):
    db.cursor.execute("""SELECT person_id FROM `communications` WHERE
                        ? in (parent_1_id, parent_2_id) AND ? in (parent_1_id, parent_2_id)""",
                      (parent_1_id, parent_2_id))
    result = db.cursor.fetchall()
    return [i[0] for i in result] if len(result) > 0 else []


# удаление связи типа родитель для персоны по id родителя
def delete_parent(db, id):
    db.cursor.execute("SELECT * FROM `communications`")
    db.cursor.execute("""UPDATE `communications` SET parent_1_id = NULL WHERE parent_1_id = ?""", (id,))
    db.db.commit()
    db.cursor.execute("""UPDATE `communications` SET parent_2_id = NULL WHERE parent_2_id = ?""", (id,))
    db.db.commit()
    db.cursor.execute("""DELETE FROM `communications` WHERE parent_1_id IS NULL AND parent_2_id IS NULL""")
    db.db.commit()
    db.cursor.execute("SELECT * FROM `communications`")


# удаление связи типа родитель для персоны
def delete_parent_with_person_id(db, parent_id, person_id):
    db.cursor.execute("""UPDATE `communications` SET parent_1_id = NULL WHERE parent_1_id = ? AND person_id = ?""",
                      (parent_id, person_id))
    db.db.commit()
    db.cursor.execute("""UPDATE `communications` SET parent_2_id = NULL WHERE parent_2_id = ? AND person_id = ?""",
                      (parent_id, person_id))
    db.db.commit()
    db.cursor.execute("""DELETE FROM `communications` WHERE parent_1_id IS NULL AND parent_2_id IS NULL""")
    db.db.commit()


# удаление связи типа дети для персоны
def delete_child(db, id):
    db.cursor.execute("""DELETE FROM `communications` WHERE person_id = ?;""", (id,))
    db.db.commit()


# удаление связей всех видов
def delete_communications(db, id):
    delete_parent(db, id)
    delete_child(db, id)
    delete_spouse(db, id)


# добавить новый брак
def append_marriages(db, spouse_id_1: int, spouse_id_2: int, date, actual: bool = True):
    db.cursor.execute("""INSERT INTO `marriages` (`spouse_1_id`, `spouse_2_id`, `year`, `date`, `actual`)
                        VALUES (?,?,?,?,?)""", (spouse_id_1, spouse_id_2, date[0], date[1], actual))
    db.db.commit()


# поиск брака по id персоны
def find_marriages(db, person_id: int):
    db.cursor.execute(
        "SELECT spouse_1_id, spouse_2_id FROM `marriages` WHERE ? in (spouse_1_id, spouse_2_id)", (person_id,))
    return [i[0] if i[0] != person_id else i[1] for i in db.cursor.fetchall()]


# поиск информации о браке
def find_marriage_status(db, spouse_1_id: int, spouse_2_id: int):
    db.cursor.execute(
        """SELECT year, date, actual FROM `marriages`
           WHERE ? in (spouse_1_id, spouse_2_id) AND ? in (spouse_1_id, spouse_2_id)""",
        (spouse_1_id, spouse_2_id))
    result = db.cursor.fetchall()
    return result[0] if len(result) > 0 else None


# изменение данных о браке
def update_marriages(db, spouse_id_1: int, spouse_id_2: int, date, actual: bool = True):
    db.cursor.execute("""SELECT id FROM `marriages` WHERE ? in (spouse_1_id, spouse_2_id) AND
                        ? in (spouse_1_id, spouse_2_id);""", (spouse_id_1, spouse_id_2))
    result = db.cursor.fetchall()
    if len(result) > 0:
        db.cursor.execute("UPDATE `marriages` SET `year` = ?, `date` = ?, `actual` = ? WHERE id = ?",
                          (date[0], date[1], actual, result[0][0]))
        db.db.commit()


# удаление брака по id супруга
def delete_spouse(db, id):
    db.cursor.execute("DELETE FROM `marriages` WHERE ? in (spouse_1_id, spouse_2_id)", (id,))
    db.db.commit()


# удаление брака для персон
def delete_spouse_with_person_id(db, spouse_1_id, spouse_2_id):
    db.cursor.execute("""DELETE FROM `marriages`
                        WHERE ? in (spouse_1_id, spouse_2_id) AND ? in (spouse_1_id, spouse_2_id)""",
                      (spouse_1_id, spouse_2_id))
    db.db.commit()


# проверка базы данных на наличие персон
def checking_database(db):
    db.cursor.execute("SELECT * FROM `persons`")
    return len(db.cursor.fetchall())


# проверка существования персоны по её id
def check_id(db, id):
    db.cursor.execute("SELECT * FROM `persons` WHERE id = ?", (id,))
    return len(db.cursor.fetchall()) > 0
