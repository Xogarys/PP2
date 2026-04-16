from connect import get_connection
import re 

# Pattern for phone number validation (+77xxxxxxxxx)
pattern = r"^\+77\d{9}$"

# Search contacts by keyword
def search():
    keyword = input("Search: ")          # get search keyword
    conn = get_connection()              # connect to DB
    cur = conn.cursor()                  # create cursor
    cur.execute("SELECT * FROM search_contacts(%s)", (keyword,))
    rows = cur.fetchall()                # fetch results
    for row in rows:
        print(row)                       # display each contact
    conn.close()                         # close connection

# Add or update a single contact
def add_or_update():
    name = input("Name: ")
    phone = input("Phone: ")
    if re.fullmatch(pattern, phone):     # validate phone
        email = input("Email: ")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "CALL upsert_contact(%s, %s, %s)",
            (name, phone, email)
        )
        conn.commit()                    # save changes
        conn.close()
    else:
        print("The phone number is invalid")  # invalid phone message

# Add multiple contacts at once
def add_several_contacts():
    n = int(input("How many contacts?: "))
    names, phones, emails = [], [], []

    for _ in range(n):
        name = input("Name: ")
        while True:
            phone = input("Phone: ")
            if re.fullmatch(pattern, phone):  # validate phone
                break
            else:
                print("Invalid phone, try again")
        email = input("Email: ")
        names.append(name)
        phones.append(phone)
        emails.append(email)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "CALL bulk_insert_contacts(%s, %s, %s)",
        (names, phones, emails)
    )
    conn.commit()                        # save all contacts
    conn.close()

# Delete contact by name or phone
def delete():
    value = input("Enter name or phone: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL delete_contact(%s)", (value,))
    conn.commit()
    conn.close()

# Show contacts with pagination
def pagination():
    limit = int(input("Limit: "))
    offset = int(input("Offset: "))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM get_contacts_paginated(%s, %s)",
        (limit, offset)
    )
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()

# Show all contacts
def showall():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonebook;")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()

# Main menu
def menu():
    while True:
        print("\n1. Search")
        print("2. Add/Update")
        print("3. Add Several Contacts")
        print("4. Delete")
        print("5. Pagination")
        print("6. Showall")
        print("7. Exit")

        choice = input("Choose: ")

        if choice == "1":
            search()
        elif choice == "2":
            add_or_update()
        elif choice == "3":
            add_several_contacts()
        elif choice == "4":
            delete()
        elif choice == "5":
            pagination()
        elif choice == "6":
            showall()
        elif choice == "7":
            break

# Run the program
if __name__ == "__main__":
    menu()