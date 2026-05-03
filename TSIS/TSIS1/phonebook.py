import re
import json
import csv
import os
from connect import get_connection

# ─── Validation ──────────────────────────────────────────────────────────────
PHONE_PATTERN = r"^\+77\d{9}$"

def valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(PHONE_PATTERN, phone))

def ask_phone(prompt: str = "Phone (+77xxxxxxxxx): ") -> str:
    while True:
        phone = input(prompt).strip()
        if valid_phone(phone):
            return phone
        print("  ✗ Invalid phone. Format: +77xxxxxxxxx")

# ─── Pretty printer ───────────────────────────────────────────────────────────
def _print_rows(rows, headers):
    if not rows:
        print("  (no records)")
        return
    cols     = len(headers)
    widths   = [len(h) for h in headers]
    str_rows = [[str(c) if c is not None else "" for c in row] for row in rows]
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < cols:
                widths[i] = max(widths[i], len(cell))
    sep  = "  +" + "+".join("-" * (w + 2) for w in widths) + "+"
    head = "  |" + "|".join(f" {h:<{widths[i]}} " for i, h in enumerate(headers)) + "|"
    print(sep); print(head); print(sep)
    for row in str_rows:
        line = "  |"
        for i in range(cols):
            cell = row[i] if i < len(row) else ""
            line += f" {cell:<{widths[i]}} |"
        print(line)
    print(sep)
    print(f"  {len(rows)} row(s)\n")

# ─── DB helper ────────────────────────────────────────────────────────────────
def _resolve_group(cur, group_name):
    if not group_name:
        return None
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups(name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]

# ─── Option 0: Apply schema & procedures ─────────────────────────────────────
def apply_schema():
    base = os.path.dirname(os.path.abspath(__file__))
    conn = get_connection()
    cur  = conn.cursor()
    for fname in ("schema.sql", "procedures.sql"):
        path = os.path.join(base, fname)
        if not os.path.exists(path):
            print(f"  ✗ {fname} not found next to phonebook.py")
            conn.close()
            return
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()
        cur.execute(sql)
        print(f"  ✓ {fname} applied.")
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH & FILTER  (options 1–4)
# ═══════════════════════════════════════════════════════════════════════════════

def filter_by_group():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT name FROM groups ORDER BY name;")
    groups = [r[0] for r in cur.fetchall()]
    conn.close()
    print("  Available groups:", ", ".join(groups))
    group = input("  Enter group name: ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    cur.execute("""
        SELECT c.name,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones,
               c.email,
               TO_CHAR(c.birthday, 'YYYY-MM-DD') AS birthday
        FROM contacts c
        LEFT JOIN phones p ON p.contact_id = c.id
        JOIN  groups  g ON g.id = c.group_id
        WHERE g.name ILIKE %s
        GROUP BY c.name, c.email, c.birthday
        ORDER BY c.name;
    """, (group,))
    rows = cur.fetchall()
    conn.close()
    _print_rows(rows, ("Name", "Phones", "Email", "Birthday"))

def search_by_email():
    keyword = input("  Email keyword: ").strip()
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT c.name,
               STRING_AGG(p.phone, ', ') AS phones,
               c.email
        FROM contacts c
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE c.email ILIKE %s
        GROUP BY c.name, c.email
        ORDER BY c.name;
    """, (f"%{keyword}%",))
    rows = cur.fetchall()
    conn.close()
    _print_rows(rows, ("Name", "Phones", "Email"))

def list_all_sorted():
    print("  Sort by:  1) Name   2) Birthday   3) Date added")
    choice    = input("  Choose (1/2/3) [1]: ").strip() or "1"
    order_map = {"1": "c.name", "2": "c.birthday NULLS LAST", "3": "c.created_at"}
    order_col = order_map.get(choice, "c.name")
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(f"""
        SELECT c.name,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones,
               c.email,
               TO_CHAR(c.birthday, 'YYYY-MM-DD')   AS birthday,
               COALESCE(g.name, '—')               AS grp,
               TO_CHAR(c.created_at, 'YYYY-MM-DD') AS added
        FROM contacts c
        LEFT JOIN phones p ON p.contact_id = c.id
        LEFT JOIN groups g ON g.id = c.group_id
        GROUP BY c.name, c.email, c.birthday, c.created_at, g.name
        ORDER BY {order_col};
    """)
    rows = cur.fetchall()
    conn.close()
    _print_rows(rows, ("Name", "Phones", "Email", "Birthday", "Group", "Added"))

def browse_paginated():
    try:
        limit = int(input("  Page size [5]: ").strip() or "5")
    except ValueError:
        limit = 5
    offset = 0
    while True:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
        rows = cur.fetchall()
        conn.close()
        page = offset // limit + 1
        print(f"\n  ── Page {page} ─────────────────────────────")
        _print_rows(rows, ("Name", "Phone", "Email"))
        if len(rows) < limit:
            print("  (end of records)")
            cmd = input("  [p]rev  [q]uit: ").strip().lower()
        else:
            cmd = input("  [n]ext  [p]rev  [q]uit: ").strip().lower()
        if   cmd == "n" and len(rows) == limit:
            offset += limit
        elif cmd == "p":
            offset = max(0, offset - limit)
        elif cmd == "q":
            break

# ═══════════════════════════════════════════════════════════════════════════════
#  IMPORT / EXPORT  (options 5–7)
# ═══════════════════════════════════════════════════════════════════════════════

def export_to_json():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email,
               TO_CHAR(c.birthday, 'YYYY-MM-DD') AS birthday,
               g.name AS group_name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY c.name;
    """)
    contacts = []
    for cid, name, email, birthday, group in cur.fetchall():
        cur2 = conn.cursor()
        cur2.execute("SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id", (cid,))
        phones = [{"phone": ph, "type": tp} for ph, tp in cur2.fetchall()]
        contacts.append({"name": name, "email": email, "birthday": birthday,
                          "group": group, "phones": phones})
    conn.close()
    filename = input("  Output file [contacts.json]: ").strip() or "contacts.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {len(contacts)} contact(s) exported → {filename}")

def import_from_json():
    filename = input("  JSON file [contacts.json]: ").strip() or "contacts.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print(f"  ✗ File '{filename}' not found.")
        return
    conn = get_connection()
    cur  = conn.cursor()
    inserted = skipped = overwritten = 0
    for c in contacts:
        name = (c.get("name") or "").strip()
        if not name:
            continue
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()
        if existing:
            action = input(f"  Duplicate '{name}' — [s]kip / [o]verwrite? ").strip().lower()
            if action != "o":
                skipped += 1
                continue
            contact_id = existing[0]
            group_id   = _resolve_group(cur, c.get("group"))
            cur.execute(
                "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                (c.get("email"), c.get("birthday"), group_id, contact_id)
            )
            cur.execute("DELETE FROM phones WHERE contact_id=%s", (contact_id,))
            overwritten += 1
        else:
            group_id = _resolve_group(cur, c.get("group"))
            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s,%s,%s,%s) RETURNING id
            """, (name, c.get("email"), c.get("birthday"), group_id))
            contact_id = cur.fetchone()[0]
            inserted  += 1
        for ph in c.get("phones", []):
            ptype = ph.get("type", "mobile")
            if ptype not in ("home", "work", "mobile"):
                ptype = "mobile"
            cur.execute(
                "INSERT INTO phones(contact_id, phone, type) VALUES (%s,%s,%s)",
                (contact_id, ph.get("phone", ""), ptype)
            )
    conn.commit()
    conn.close()
    print(f"  ✓ Done — inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}")

def import_from_csv():
    filename = input("  CSV file [contacts.csv]: ").strip() or "contacts.csv"
    try:
        f = open(filename, newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"  ✗ File '{filename}' not found.")
        return
    conn = get_connection()
    cur  = conn.cursor()
    count = errors = 0
    with f:
        reader = csv.DictReader(f)
        for row in reader:
            name  = (row.get("name")       or "").strip()
            phone = (row.get("phone")      or "").strip()
            email = (row.get("email")      or "").strip() or None
            bday  = (row.get("birthday")   or "").strip() or None
            group = (row.get("group")      or "").strip() or None
            ptype = (row.get("phone_type") or "mobile").strip().lower()
            if not name or not phone:
                errors += 1
                continue
            if ptype not in ("home", "work", "mobile"):
                ptype = "mobile"
            group_id = _resolve_group(cur, group)
            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s,%s,%s,%s)
                ON CONFLICT (name) DO UPDATE
                    SET email=EXCLUDED.email,
                        birthday=EXCLUDED.birthday,
                        group_id=EXCLUDED.group_id
                RETURNING id
            """, (name, email, bday, group_id))
            contact_id = cur.fetchone()[0]
            if phone:
                cur.execute("""
                    INSERT INTO phones(contact_id, phone, type) VALUES (%s,%s,%s)
                    ON CONFLICT DO NOTHING
                """, (contact_id, phone, ptype))
            count += 1
    conn.commit()
    conn.close()
    print(f"  ✓ CSV import done — {count} row(s) processed, {errors} skipped")

# ═══════════════════════════════════════════════════════════════════════════════
#  STORED PROCEDURES  (options 8–10)
# ═══════════════════════════════════════════════════════════════════════════════

def add_phone_to_contact():
    name  = input("  Contact name: ").strip()
    phone = ask_phone("  New phone (+77xxxxxxxxx): ")
    ptype = input("  Type (home/work/mobile) [mobile]: ").strip().lower() or "mobile"
    if ptype not in ("home", "work", "mobile"):
        ptype = "mobile"
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("  ✓ Phone added.")
    except Exception as e:
        conn.rollback()
        print(f"  ✗ {e}")
    finally:
        conn.close()

def move_contact_to_group():
    name  = input("  Contact name: ").strip()
    group = input("  Group name: ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print("  ✓ Contact moved.")
    except Exception as e:
        conn.rollback()
        print(f"  ✗ {e}")
    finally:
        conn.close()

def search_all_fields():
    keyword = input("  Search keyword: ").strip()
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (keyword,))
    rows = cur.fetchall()
    conn.close()
    _print_rows(rows, ("Name", "Phone", "Email"))

# ═══════════════════════════════════════════════════════════════════════════════
#  PRACTICE 7/8  (options 11–15)
# ═══════════════════════════════════════════════════════════════════════════════

def add_or_update():
    name  = input("  Name: ").strip()
    phone = ask_phone("  Phone (+77xxxxxxxxx): ")
    email = input("  Email: ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    cur.execute("CALL upsert_contact(%s, %s, %s)", (name, phone, email))
    conn.commit()
    conn.close()
    print("  ✓ Contact saved.")

def add_several_contacts():
    n = int(input("  How many contacts?: "))
    names, phones, emails = [], [], []
    for i in range(n):
        print(f"\n  Contact {i+1}:")
        names.append(input("  Name: ").strip())
        phones.append(ask_phone("  Phone (+77xxxxxxxxx): "))
        emails.append(input("  Email: ").strip())
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("CALL bulk_insert_contacts(%s, %s, %s)", (names, phones, emails))
    conn.commit()
    conn.close()
    print(f"  ✓ {n} contact(s) submitted.")

def add_contact_full():
    name  = input("  Name: ").strip()
    email = input("  Email (blank to skip): ").strip() or None
    bday  = input("  Birthday YYYY-MM-DD (blank to skip): ").strip() or None
    group = input("  Group (Family/Work/Friend/Other or new, blank to skip): ").strip() or None
    conn  = get_connection()
    cur   = conn.cursor()
    group_id = _resolve_group(cur, group)
    cur.execute("""
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s,%s,%s,%s)
        ON CONFLICT (name) DO UPDATE
            SET email=EXCLUDED.email,
                birthday=EXCLUDED.birthday,
                group_id=EXCLUDED.group_id
        RETURNING id
    """, (name, email, bday, group_id))
    contact_id = cur.fetchone()[0]
    while True:
        phone = ask_phone("  Phone (+77xxxxxxxxx): ")
        ptype = input("  Type (home/work/mobile) [mobile]: ").strip().lower() or "mobile"
        if ptype not in ("home", "work", "mobile"):
            ptype = "mobile"
        cur.execute(
            "INSERT INTO phones(contact_id, phone, type) VALUES (%s,%s,%s)",
            (contact_id, phone, ptype)
        )
        if input("  Add another phone? (y/n): ").strip().lower() != "y":
            break
    conn.commit()
    conn.close()
    print("  ✓ Contact saved.")

def delete():
    value = input("  Enter name or phone to delete: ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    cur.execute("CALL delete_contact(%s)", (value,))
    conn.commit()
    conn.close()
    print("  ✓ Deleted.")

def showall():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT c.name,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones,
               c.email,
               TO_CHAR(c.birthday,'YYYY-MM-DD') AS birthday,
               COALESCE(g.name,'—') AS grp
        FROM contacts c
        LEFT JOIN phones p ON p.contact_id = c.id
        LEFT JOIN groups g ON g.id = c.group_id
        GROUP BY c.name, c.email, c.birthday, g.name
        ORDER BY c.name;
    """)
    rows = cur.fetchall()
    conn.close()
    _print_rows(rows, ("Name", "Phones", "Email", "Birthday", "Group"))

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN MENU
# ═══════════════════════════════════════════════════════════════════════════════

MENU = """
╔══════════════════════════════════════════════════╗
║         PhoneBook  –  TSIS 1 Extended Menu       ║
╠══════════════════════════════════════════════════╣
║  SCHEMA                                          ║
║  0.  Apply schema & procedures                   ║
╠══════════════════════════════════════════════════╣
║  SEARCH & FILTER                                 ║
║  1.  Filter contacts by group                    ║
║  2.  Search by email                             ║
║  3.  List all contacts (sorted)                  ║
║  4.  Browse contacts (paginated)                 ║
╠══════════════════════════════════════════════════╣
║  IMPORT / EXPORT                                 ║
║  5.  Export to JSON                              ║
║  6.  Import from JSON                            ║
║  7.  Import from CSV (extended)                  ║
╠══════════════════════════════════════════════════╣
║  STORED PROCEDURES                               ║
║  8.  Add phone number to contact                 ║
║  9.  Move contact to group                       ║
║  10. Search contacts (all fields + phones)       ║
╠══════════════════════════════════════════════════╣
║  PRACTICE 7/8                                    ║
║  11. Add / Update contact (quick)                ║
║  12. Add several contacts (bulk)                 ║
║  13. Add full contact (birthday, group, phones)  ║
║  14. Delete contact                              ║
║  15. Show all contacts                           ║
╠══════════════════════════════════════════════════╣
║  Q.  Quit                                        ║
╚══════════════════════════════════════════════════╝"""

DISPATCH = {
    "0":  apply_schema,
    "1":  filter_by_group,
    "2":  search_by_email,
    "3":  list_all_sorted,
    "4":  browse_paginated,
    "5":  export_to_json,
    "6":  import_from_json,
    "7":  import_from_csv,
    "8":  add_phone_to_contact,
    "9":  move_contact_to_group,
    "10": search_all_fields,
    "11": add_or_update,
    "12": add_several_contacts,
    "13": add_contact_full,
    "14": delete,
    "15": showall,
}

def main():
    while True:
        print(MENU)
        choice = input("Choose: ").strip().lower()
        if choice == "q":
            print("  Bye!")
            break
        fn = DISPATCH.get(choice)
        if fn:
            print()
            fn()
        else:
            print("  ✗ Unknown option.")

if __name__ == "__main__":
    main()
