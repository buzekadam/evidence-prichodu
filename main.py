import pyodbc
import serial
import time
import threading

# -----------------------------
# Připojení k databázi
# -----------------------------
conn = pyodbc.connect(
    r'DRIVER={SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=test_pss;Trusted_Connection=yes;' # místo test_pss název tvé databáze
)
cursor = conn.cursor()

# -----------------------------
# Připojení k Arduinu
# -----------------------------
arduino = serial.Serial('COM3', 9600, timeout=1) # ve Windows COM číslo zjistíš podle: správce zařízení > Porty COM > COMx (za x dosadíš číslo, které je napsané u nově připojeného zařízení)
time.sleep(2)

last_uid = None
last_time = 0
DELAY = 2
ready_printed = False

add_user_mode = threading.Event()
delete_user_mode = threading.Event()
cancel_action = threading.Event()
new_user_name = None
card_to_delete = None
ignore_uid = None

# -----------------------------
# Funkce pro sledování karet
# -----------------------------
def card_loop():
    global last_uid, last_time, ready_printed, new_user_name, card_to_delete, ignore_uid

    print("=" * 29 + "\n      EVIDENCE PŘÍCHODŮ\n" + "=" * 29)

    while True:
        if cancel_action.is_set():
            add_user_mode.clear()
            delete_user_mode.clear()
            cancel_action.clear()
            card_to_delete = None
            print("\nAkce zrušena.")
            ready_printed = False

        uid_line = arduino.readline().decode().strip().upper()

        if not uid_line:
            if not ready_printed and not add_user_mode.is_set() and not delete_user_mode.is_set():
                print("\nČekám na kartu... (pro akci dej 'Enter' a pak číslo akce)")
                ready_printed = True
            time.sleep(0.1)
            continue
        if uid_line == ignore_uid and delete_user_mode.is_set():
            continue

        ready_printed = False
        now = time.time()
        if uid_line == last_uid and (now - last_time) < DELAY:
            continue
        last_uid = uid_line
        last_time = now

        # -----------------------------
        # Přidání nové osoby
        # -----------------------------
        if add_user_mode.is_set():
            cursor.execute("SELECT id FROM users WHERE cardUID=?", (uid_line,))
            if cursor.fetchone():
                print("\n(Přidání) Tato karta už existuje! Přilož jinou kartu nebo napiš 'x' pro zrušení…")
                last_uid = None
                continue
            try:
                cursor.execute(
                    "INSERT INTO users (jmeno, cardUID) VALUES (?, ?)",
                    (new_user_name, uid_line)
                )
                conn.commit()
                print(f"\n(Přidání) Uživatel '{new_user_name}' přidán s UID {uid_line}")
            except pyodbc.IntegrityError:
                print("\n(Přidání) Chyba při přidávání osoby! Nová osoba se stejným jménem nesmí již existovat. Přidej osobu znovu.")
            finally:
                add_user_mode.clear()
                new_user_name = None

        # -----------------------------
        # Odstranění karty
        # -----------------------------

        elif delete_user_mode.is_set() and not card_to_delete:
            cursor.execute("SELECT id, jmeno FROM users WHERE cardUID=?", (uid_line,))
            user = cursor.fetchone()
            if user:
                card_to_delete = user
                print(f"\n(Odstranění) Nalezena osoba: {user[1]} ({uid_line}). Pokračuj 'Enter'")
            else:
                print(f"\n(Odstranění) UID {uid_line} nenalezeno v databázi!")
            

        # -----------------------------
        # Normální příchody/odchody
        # -----------------------------
        else:
            cursor.execute("SELECT id, jmeno FROM users WHERE cardUID=?", (uid_line,))
            user = cursor.fetchone()
            if user:
                cursor.execute(
                    "SELECT TOP 1 typ FROM prichody WHERE users_id=? ORDER BY cas DESC",
                    (user[0],)
                )
                last = cursor.fetchone()
                typ = 'prichod' if not last or last[0] == 'odchod' else 'odchod'

                cursor.execute(
                    "INSERT INTO prichody (users_id, typ) VALUES (?, ?)",
                    (user[0], typ)
                )
                conn.commit()
                print(f"\n{user[1]} ({uid_line}) -> {typ} zaznamenán")
            else:
                print(f"\nUID {uid_line} nenalezen v databázi!")

        time.sleep(0.1)

# -----------------------------
# Funkce pro vstup uživatele
# -----------------------------
def input_loop():
    global new_user_name, card_to_delete, last_uid, last_time, ignore_uid
    while True:
        if add_user_mode.is_set():
            choice = input("(Přidání) čekám na kartu.").strip().lower()
            if choice == 'x':
                cancel_action.set()
        elif delete_user_mode.is_set() and card_to_delete:
            while card_to_delete is not None:
                choice = input(f"[Odstranit '{card_to_delete[1]}'?] A/N: ").strip().lower()

                if choice == "a":
                    cursor.execute("DELETE FROM prichody WHERE users_id=?", (card_to_delete[0],))
                    cursor.execute("DELETE FROM users WHERE id=?", (card_to_delete[0],))
                    conn.commit()
                    print(f"\nUživatel '{card_to_delete[1]}' byl úspěšně odstraněn.")
                    card_to_delete = None
                    delete_user_mode.clear()
                    last_uid = None
                    last_time = 0

                elif choice in ["n", "x"]:
                    print("\nAkce zrušena.")
                    ignore_uid = last_uid
                    card_to_delete = None
                    delete_user_mode.clear()
                    last_uid = None
                    last_time = 0

                else:
                    print("\n(Odstranění) Neplatná volba, zadej 'A' pro ANO nebo 'N/X' pro NE.")
        elif delete_user_mode.is_set() and card_to_delete is None:
            choice = input("").strip().lower()
            if choice == 'x':
                print("\nAkce zrušena.")
                delete_user_mode.clear()
                card_to_delete = None
                last_uid = None
                ignore_uid = None

        else:
            if not add_user_mode.is_set() and not delete_user_mode.is_set():
                choice = input("\nPro přidání nové osoby napiš '1'\nOdstranění osoby '2'\nVýpis příchodů/odchodů '3': \n").strip().lower()
                if choice == 'x':
                    cancel_action.set()
                elif choice == '1':
                    name_input = input("(Přidání) Zadej jméno nového uživatele (nebo 'x' pro zrušení): ").strip()
                    if name_input.lower() == 'x':
                        print("\nPřidávání nové osoby zrušeno.")
                        continue
                    elif name_input:
                        new_user_name = name_input
                        print(f"(Přidání) Pro přidání uživatele '{new_user_name}' přilož novou kartu nebo napiš 'x' pro zrušení…")
                        add_user_mode.set()
                    else:
                        print("Nezadáno jméno, zkuste znovu.")
                elif choice == '2':
                    print("\n(Odstranění) Přilož kartu, kterou chceš odstranit, nebo zadej 'x' pro ukončení.")
                    delete_user_mode.set()
                    ignore_uid = None
                elif choice == '3':
                    cursor.execute("SELECT id, jmeno FROM users")
                    users = cursor.fetchall()
                    print("\nSeznam uživatelů (seřazeno abecedně podle jména):")
                    for u in users:
                        print(f"ID: {u[0]}, Jméno: {u[1]}")
                    user_id = input("\nZadej ID uživatele pro zobrazení příchodů/odchodů: ").strip()
                    if user_id.isdigit():
                        cursor.execute(
                            "SELECT typ, cas FROM prichody WHERE users_id=? ORDER BY cas ASC",
                            (int(user_id),)
                        )
                        entries = cursor.fetchall()
                        if entries:
                            print(f"\nPříchody/odchody osoby ID {user_id}:")
                            for e in entries:
                                print(f"{e[1]} -> {e[0]}")
                        else:
                            print("Žádné záznamy nenalezeny.")
                    else:
                        print("Neplatné ID.")

# -----------------------------
# Spuštění vláken
# -----------------------------
threading.Thread(target=card_loop, daemon=True).start()
threading.Thread(target=input_loop, daemon=True).start()

while True:
    time.sleep(1)