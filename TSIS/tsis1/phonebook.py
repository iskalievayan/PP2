import json
from connect import get_connection


# ---------- ДОБАВЛЕНИЕ КОНТАКТА ----------
def add_contact():
    # подключение к базе данных
    conn = get_connection()
    cur = conn.cursor()

    # ввод данных от пользователя
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group = input("Group: ")

    # проверяем есть ли такая группа в базе
    cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
    g = cur.fetchone()

    # если группы нет — создаём
    if not g:
        cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (group,))
        group_id = cur.fetchone()[0]
    else:
        group_id = g[0]

    # добавляем контакт в таблицу contacts
    cur.execute("""
        INSERT INTO contacts(name,email,birthday,group_id)
        VALUES(%s,%s,%s,%s)
        ON CONFLICT (name) DO NOTHING
    """, (name, email, birthday, group_id))

    # сохраняем изменения
    conn.commit()
    cur.close()
    conn.close()


# ---------- ДОБАВЛЕНИЕ ТЕЛЕФОНА ----------
def add_phone():
    conn = get_connection()
    cur = conn.cursor()

    # ввод данных
    name = input("Contact name: ")
    phone = input("Phone: ")
    type_ = input("Type (home/work/mobile): ")

    # вызываем SQL процедуру из PostgreSQL
    cur.execute("CALL add_phone(%s,%s,%s)", (name, phone, type_))

    conn.commit()
    cur.close()
    conn.close()


# ---------- ПОИСК ----------
def search():
    conn = get_connection()
    cur = conn.cursor()

    # строка поиска
    q = input("Search: ")

    # вызываем SQL функцию поиска
    cur.execute("SELECT * FROM search_contacts(%s)", (q,))
    rows = cur.fetchall()

    # вывод результата
    for r in rows:
        print(r)

    cur.close()
    conn.close()


# ---------- ФИЛЬТР ПО ГРУППЕ ----------
def filter_group():
    conn = get_connection()
    cur = conn.cursor()

    g = input("Group: ")

    # выбираем контакты по названию группы
    cur.execute("""
        SELECT c.name, c.email
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name=%s
    """, (g,))

    for r in cur.fetchall():
        print(r)

    cur.close()
    conn.close()


# ---------- ЭКСПОРТ В JSON ----------
def export_json():
    conn = get_connection()
    cur = conn.cursor()

    # получаем основные данные контактов
    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
    """)

    contacts = []

    for row in cur.fetchall():
        name, email, birthday, group = row

        # получаем телефоны для каждого контакта
        cur.execute("""
            SELECT phone, type FROM phones
            JOIN contacts ON contacts.id = phones.contact_id
            WHERE contacts.name=%s
        """, (name,))

        phones = cur.fetchall()

        # формируем структуру JSON
        contacts.append({
            "name": name,
            "email": email,
            "birthday": str(birthday),
            "group": group,
            "phones": phones
        })

    # записываем в файл
    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=4)

    print("Exported!")


# ---------- ИМПОРТ ИЗ JSON ----------
def import_json():
    conn = get_connection()
    cur = conn.cursor()

    # читаем файл JSON
    with open("contacts.json") as f:
        data = json.load(f)

    for c in data:
        name = c["name"]

        # проверяем существует ли контакт
        cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
        exists = cur.fetchone()

        # если есть — спрашиваем что делать
        if exists:
            choice = input(f"{name} exists. skip/overwrite: ")
            if choice == "skip":
                continue
            else:
                cur.execute("DELETE FROM contacts WHERE name=%s", (name,))

        # работа с группами
        cur.execute("SELECT id FROM groups WHERE name=%s", (c["group"],))
        g = cur.fetchone()

        if not g:
            cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (c["group"],))
            gid = cur.fetchone()[0]
        else:
            gid = g[0]

        # добавляем контакт
        cur.execute("""
            INSERT INTO contacts(name,email,birthday,group_id)
            VALUES(%s,%s,%s,%s)
            RETURNING id
        """, (name, c["email"], c["birthday"], gid))

        cid = cur.fetchone()[0]

        # добавляем телефоны
        for p in c["phones"]:
            cur.execute("""
                INSERT INTO phones(contact_id,phone,type)
                VALUES(%s,%s,%s)
            """, (cid, p[0], p[1]))

    conn.commit()
    print("Imported!")


# ---------- МЕНЮ ПРОГРАММЫ ----------
def menu():
    while True:
        print("\n1 Add contact")
        print("2 Add phone")
        print("3 Search")
        print("4 Filter by group")
        print("5 Export JSON")
        print("6 Import JSON")
        print("0 Exit")

        c = input("Choose: ")

        if c == "1":
            add_contact()
        elif c == "2":
            add_phone()
        elif c == "3":
            search()
        elif c == "4":
            filter_group()
        elif c == "5":
            export_json()
        elif c == "6":
            import_json()
        elif c == "0":
            break


# запуск программы
menu()