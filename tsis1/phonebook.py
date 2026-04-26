import json
from connect import get_connection


# создаем таблицы и процедуры
def create_database_objects():
    conn = get_connection()
    cur = conn.cursor()

    # основная таблица контактов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            birthday DATE,
            group_id INTEGER,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # таблица групп
    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        );
    """)

    # добавляем связь с группами
    cur.execute("""
        ALTER TABLE contacts
        ADD CONSTRAINT contacts_group_fk
        FOREIGN KEY (group_id) REFERENCES groups(id);
    """)

    # таблица телефонов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY,
            contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
            phone VARCHAR(20) NOT NULL,
            type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
        );
    """)

    # процедура для добавления телефона
    cur.execute("""
        CREATE OR REPLACE PROCEDURE add_phone(
            p_contact_name VARCHAR,
            p_phone VARCHAR,
            p_type VARCHAR
        )
        LANGUAGE plpgsql
        AS $$
        DECLARE
            found_contact_id INTEGER;
        BEGIN
            SELECT id INTO found_contact_id
            FROM contacts
            WHERE name = p_contact_name;

            IF found_contact_id IS NULL THEN
                RAISE NOTICE 'Contact not found';
                RETURN;
            END IF;

            INSERT INTO phones(contact_id, phone, type)
            VALUES (found_contact_id, p_phone, p_type);
        END;
        $$;
    """)

    # процедура для перемещения в группу
    cur.execute("""
        CREATE OR REPLACE PROCEDURE move_to_group(
            p_contact_name VARCHAR,
            p_group_name VARCHAR
        )
        LANGUAGE plpgsql
        AS $$
        DECLARE
            found_group_id INTEGER;
        BEGIN
            INSERT INTO groups(name)
            VALUES (p_group_name)
            ON CONFLICT (name) DO NOTHING;

            SELECT id INTO found_group_id
            FROM groups
            WHERE name = p_group_name;

            UPDATE contacts
            SET group_id = found_group_id
            WHERE name = p_contact_name;
        END;
        $$;
    """)

    # функция для общего поиска
    cur.execute("""
        CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
        RETURNS TABLE (
            contact_id INTEGER,
            contact_name VARCHAR,
            phone_number VARCHAR,
            email_address VARCHAR,
            birthday_date DATE,
            group_name VARCHAR
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                c.id,
                c.name,
                p.phone,
                c.email,
                c.birthday,
                g.name
            FROM contacts c
            LEFT JOIN phones p ON c.id = p.contact_id
            LEFT JOIN groups g ON c.group_id = g.id
            WHERE 
                c.name ILIKE '%' || p_query || '%'
                OR c.email ILIKE '%' || p_query || '%'
                OR p.phone ILIKE '%' || p_query || '%'
                OR g.name ILIKE '%' || p_query || '%';
        END;
        $$;
    """)

    conn.commit()
    cur.close()
    conn.close()


# показать все контакты
def show_contacts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY c.id;
    """)

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


# добавить контакт сразу с телефоном
def add_contact():
    contact_name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group_name = input("Group: ")
    phone_number = input("Phone: ")
    phone_type = input("Type (home/work/mobile): ")

    conn = get_connection()
    cur = conn.cursor()

    # создаем группу если ее нет
    cur.execute("""
        INSERT INTO groups(name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING;
    """, (group_name,))

    cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
    group_id = cur.fetchone()[0]

    # добавляем контакт
    cur.execute("""
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (contact_name, email, birthday, group_id))

    contact_id = cur.fetchone()[0]

    # добавляем телефон
    cur.execute("""
        INSERT INTO phones(contact_id, phone, type)
        VALUES (%s, %s, %s);
    """, (contact_id, phone_number, phone_type))

    conn.commit()
    cur.close()
    conn.close()

    print("Contact added")


# фильтр по группе
def filter_by_group():
    group_name = input("Enter group name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name = %s;
    """, (group_name,))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


# поиск по email
def search_by_email():
    email_part = input("Enter email part: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, email, birthday
        FROM contacts
        WHERE email ILIKE %s;
    """, ("%" + email_part + "%",))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


# сортировка
def sort_contacts():
    print("Sort by: name / birthday / date_added")
    sort_field = input("Enter field: ")

    allowed_fields = ["name", "birthday", "date_added"]

    if sort_field not in allowed_fields:
        print("Wrong field")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT name, email, birthday, date_added
        FROM contacts
        ORDER BY {sort_field};
    """)

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


# добавить еще один телефон
def add_phone():
    contact_name = input("Contact name: ")
    phone_number = input("Phone: ")
    phone_type = input("Type home/work/mobile: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CALL add_phone(%s, %s, %s);",
        (contact_name, phone_number, phone_type)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Phone added")


# переместить контакт в группу
def move_to_group():
    contact_name = input("Contact name: ")
    group_name = input("Group name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CALL move_to_group(%s, %s);",
        (contact_name, group_name)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Contact moved to group")


# общий поиск
def search_all():
    search_text = input("Search: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s);", (search_text,))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


# экспорт в JSON
def export_to_json():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.id,
            c.name,
            c.email,
            c.birthday::TEXT,
            g.name AS group_name,
            COALESCE(
                json_agg(
                    json_build_object('phone', p.phone, 'type', p.type)
                ) FILTER (WHERE p.id IS NOT NULL),
                '[]'
            ) AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, g.name
        ORDER BY c.id;
    """)

    rows = cur.fetchall()
    contacts_list = []

    for row in rows:
        contacts_list.append({
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "birthday": row[3],
            "group": row[4],
            "phones": row[5]
        })

    with open("contacts.json", "w", encoding="utf-8") as file:
        json.dump(contacts_list, file, indent=4, ensure_ascii=False)

    cur.close()
    conn.close()

    print("Exported to contacts.json")


# импорт из JSON
def import_from_json():
    with open("contacts.json", "r", encoding="utf-8") as file:
        contacts = json.load(file)

    conn = get_connection()
    cur = conn.cursor()

    for contact in contacts:
        contact_name = contact["name"]

        cur.execute("SELECT id FROM contacts WHERE name = %s;", (contact_name,))
        existing_contact = cur.fetchone()

        if existing_contact:
            choice = input(f"{contact_name} already exists. skip/overwrite: ")

            if choice == "skip":
                continue

            if choice == "overwrite":
                cur.execute("DELETE FROM contacts WHERE name = %s;", (contact_name,))

        group_name = contact["group"]

        if group_name:
            cur.execute("""
                INSERT INTO groups(name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING;
            """, (group_name,))

            cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
            group_id = cur.fetchone()[0]
        else:
            group_id = None

        cur.execute("""
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (
            contact["name"],
            contact["email"],
            contact["birthday"],
            group_id
        ))

        contact_id = cur.fetchone()[0]

        for phone in contact["phones"]:
            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s);
            """, (
                contact_id,
                phone["phone"],
                phone["type"]
            ))

    conn.commit()
    cur.close()
    conn.close()

    print("Imported from JSON")


# меню
def menu():
    while True:
        print("""
1. Show contacts
2. Add contact
3. Filter by group
4. Search by email
5. Sort contacts
6. Add phone
7. Move contact to group
8. Search all
9. Export to JSON
10. Import from JSON
0. Quit
""")

        choice = input("Choose: ")

        if choice == "1":
            show_contacts()
        elif choice == "2":
            add_contact()
        elif choice == "3":
            filter_by_group()
        elif choice == "4":
            search_by_email()
        elif choice == "5":
            sort_contacts()
        elif choice == "6":
            add_phone()
        elif choice == "7":
            move_to_group()
        elif choice == "8":
            search_all()
        elif choice == "9":
            export_to_json()
        elif choice == "10":
            import_from_json()
        elif choice == "0":
            break
        else:
            print("Wrong choice")


create_database_objects()
menu()