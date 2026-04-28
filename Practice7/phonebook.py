from connect import get_conn
import csv

# CREATE TABLE
def create_table():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100),
            phone VARCHAR(20) UNIQUE
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# INSERT
def insert_contact(name, phone):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()


# CSV IMPORT
def insert_from_csv():
    conn = get_conn()
    cur = conn.cursor()

    with open("contacts.csv", encoding="utf-8") as file:
        reader = csv.reader(file)
        for name, phone in reader:
            cur.execute(
                "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)",
                (name, phone)
            )

    conn.commit()
    cur.close()
    conn.close()


# SEARCH
def search_name(name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM phonebook WHERE first_name ILIKE %s",
        (f"%{name}%",)
    )

    print(cur.fetchall())

    cur.close()
    conn.close()


# UPDATE
def update(phone, new_name=None, new_phone=None):
    conn = get_conn()
    cur = conn.cursor()

    if new_name:
        cur.execute(
            "UPDATE phonebook SET first_name=%s WHERE phone=%s",
            (new_name, phone)
        )

    if new_phone:
        cur.execute(
            "UPDATE phonebook SET phone=%s WHERE phone=%s",
            (new_phone, phone)
        )

    conn.commit()
    cur.close()
    conn.close()


# DELETE
def delete(phone):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))

    conn.commit()
    cur.close()
    conn.close()


# MENU
def menu():
    create_table()

    while True:
        print("\n1 Add\n2 CSV\n3 Search\n4 Update\n5 Delete\n0 Exit")
        c = input("Choose: ")

        if c == "1":
            insert_contact(input("Name: "), input("Phone: "))

        elif c == "2":
            insert_from_csv()

        elif c == "3":
            search_name(input("Name: "))

        elif c == "4":
            update(input("Phone: "), input("New name (or empty): ") or None,
                   input("New phone (or empty): ") or None)

        elif c == "5":
            delete(input("Phone: "))

        elif c == "0":
            break


menu()