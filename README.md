# Evidence příchodů a odchodů

## Instalace a spuštění projektu

### 1. Stažení projektu
1. Otevři tento repozitář  
2. Klikni na tlačítko Code  
3. Zvol Download ZIP  
4. Soubor rozbal

---

### 2. Nastavení databáze (SQL Server)
# Instalace SQL Serveru
1. Stáhni a nainstaluj Microsoft SQL Server (doporučeno SQL Server Express) https://www.microsoft.com/en-us/sql-server/sql-server-downloads
2. Během instalace zvol:
   - režim: Basic nebo Custom
   - název instance: SQLEXPRESS (doporučeno)
# Instalace SSMS (SQL Server Management Studio) 
1. Stáhni SSMS (SQL Server Management Studio) https://learn.microsoft.com/en-us/ssms/install/install (při projektu používaná verze 18.12.1)
2. Nainstaluj a spusť
---
# Vytvoření databáze
1. vytvoř novou databázi, nebo použij z kódu, f5
2. use jmeno_databaze (nebo z kódu), f5
3. vytvoř 2 tabulky (users, prichody) z kódu (označ je, f5)
4. pro mazání podle id použij "návod" v sql kódu u --SMAZÁNÍ KARTY PODLE ID

### 3. Arduino + RFID
1. Otevři Arduino IDE  https://www.arduino.cc/en/software/
2. Otevři soubor RFID_Arduino/RFID_Arduino.ino
3. Připoj Arduino k PC
4. možná bude potřeba stáhnout v Arduino IDE "Libraries" > napiš MFRC522 > stáhni ten by GithubCommunity
5. nastav Tools > Board > Arduino UNO (nebo podle arduina, které používáš)
6. nastav Tools > Port > COMx podle čísla v "správce zařízení" > porty > COMx (za x číslo portu)
7. Klikni na Upload  

---

### 4. Python aplikace

#### Instalace knihoven
Otevři příkazový řádek a spusť:
pip install pyodbc pyserial

#### Nastavení
V souboru main.py uprav:
- COM port (např. COM3)
- připojení k databázi (např. localhost\SQLEXPRESS)

#### Spuštění
Přejdi do složky python a spusť:
python main.py

Nebo použij připravený soubor:
spustit.txt přejmenuj na spustit.bat a spusť ho
