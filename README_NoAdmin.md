# 🔓 Browser Blocker (No Admin Required)

Un program simplu pentru Windows 10/11 care blochează accesul browserelor la internet **FĂRĂ să necesite parola de Administrator!**

## 🎯 Caracteristici

- ✅ **NU necesită drepturi de Administrator** - funcționează fără parolă admin!
- 🌐 **Suportă browsere populare**: Chrome, Edge, Firefox, Brave
- 🔧 **Metodă proxy invalid** - Browserele pornesc dar nu au internet
- 🔄 **Monitorizare continuă** - Împiedică pornirea browserelor
- 📊 **Log în timp real** - Vezi exact ce se întâmplă
- 🧹 **Restaurare automată** - Setările se restaurează când oprești programul

## 📋 Cerințe

- Windows 10/11
- Python 3.6 sau mai nou (tkinter inclus)
- Python library: `psutil` (se instalează automat la prima rulare)
- **NU** necesită drepturi de Administrator!

## 🚀 Utilizare

### SUPER SIMPLU - Dublu-click:

1. **Dublu-click pe `Browser_Blocker_NoAdmin.vbs`**
2. Dacă îți cere să instaleze `psutil`, apasă **Yes**
3. Interfața se deschide automat!
4. Apasă **BLOCK BROWSERS**

**NU apare cerere UAC! NU necesită parolă de Administrator!** 🎉

### Alternativ - Python direct:

```bash
# Instalează dependența (o singură dată)
pip install psutil

# Rulează programul
python browser_blocker_no_admin.py
```

## 🔧 Cum Funcționează

### 1. **Setare Proxy Invalid**
- Modifică fișierele de configurare ale browserelor
- Setează un proxy invalid: `127.0.0.1:9999` (care nu există)
- Browserele încarcă setările și încearcă să se conecteze prin proxy-ul inexistent
- Rezultat: Browser-ul pornește, dar **nu are acces la internet!**

### 2. **Monitorizare Continuă**
- Programul monitorizează procesele care rulează
- Când detectează un browser pornind, îl închide automat
- Copilul vede browser-ul deschizându-se pentru o secundă, apoi se închide

### 3. **Restaurare Automată**
- Când apeși **UNBLOCK** sau închizi programul
- Setările originale sunt restaurate din backup
- Browserele funcționează normal din nou

## 🖼️ Interfața GUI

Interfața oferă:
- **Status vizual** - Vezi instant dacă browserele sunt blocate
- **Log detaliat** - Toate acțiunile în timp real
- **2 butoane simple**:
  - 🚫 **BLOCK BROWSERS** - Blochează accesul
  - ✅ **UNBLOCK BROWSERS** - Deblochează accesul

## ⚠️ Important de Știut

### Avantaje:
- ✅ NU necesită parolă Administrator
- ✅ Simplu de folosit
- ✅ Browserul pornește (nu suspectează nimic)
- ✅ Pur și simplu "nu merge netul" în browser
- ✅ Alte aplicații au net normal

### Limitări:
- ⚠️ Browserele trebuie închise când aplici blocarea (programul le închide automat)
- ⚠️ Un user tehnic poate reseta manual setările de proxy
- ⚠️ Poate fi ocolit cu Safe Mode sau editare manuală a fișierelor de config
- ⚠️ Nu funcționează la fel de bine ca Windows Firewall (care necesită admin)

## 📁 Fișiere Incluse

- **`Browser_Blocker_NoAdmin.vbs`** - Launcher recomandat (silent, auto-instalare psutil)
- **`browser_blocker_no_admin.py`** - Programul principal Python
- **`requirements.txt`** - Dependențe Python (psutil)
- **`README_NoAdmin.md`** - Acest fișier

## 🛡️ Ce Modifică Programul

### Chrome / Edge / Brave:
- **Fișier**: `%LOCALAPPDATA%\...\User Data\Default\Preferences`
- **Modificare**: Adaugă setări proxy în JSON
- **Backup**: `Preferences.backup_browser_blocker`

### Firefox:
- **Fișier**: `%APPDATA%\Mozilla\Firefox\Profiles\...\prefs.js`
- **Modificare**: Adaugă linii de configurare proxy
- **Backup**: `prefs.js.backup_browser_blocker`

**Toate modificările sunt reversibile!**

## 🐛 Troubleshooting

**Eroare: "psutil not found"**
- Launcher-ul VBS instalează automat psutil
- SAU manual: `pip install psutil`

**Browserul încă are acces la internet**
- Asigură-te că ai apăsat BLOCK BROWSERS
- Verifică că browser-ul a fost închis și redeschis
- Unele browsere pot folosi VPN care ocolește proxy-ul

**Programul se închide singur**
- Verifică că Python este instalat corect
- Rulează din Command Prompt pentru a vedea erorile:
  ```
  python browser_blocker_no_admin.py
  ```

**Vreau să blochez permanent (fără să ruleze programul)**
- Acest program necesită să ruleze continuu
- Pentru blocare permanentă, ai nevoie de versiunea cu Admin:
  - Folosește `browser_blocker.py` (necesită parola Administrator)
  - SAU configurează blocarea la nivel de router

## 🔄 Diferențe față de Versiunea cu Admin

| Caracteristică | **Fără Admin** (acest program) | **Cu Admin** (browser_blocker.py) |
|----------------|-------------------------------|-----------------------------------|
| Parola Admin necesară | ❌ NU | ✅ DA |
| Metoda de blocare | Proxy invalid | Windows Firewall |
| Eficiență blocare | 80-90% | 99% |
| Browser pornește | ✅ DA (fără net) | ✅ DA (fără net) |
| Poate fi ocolit | Mediu (cu cunoștințe tehnice) | Greu (necesită admin) |
| Program trebuie să ruleze | ✅ DA | ✅ DA |
| Potrivit pentru | Utilizare personală, productivitate | Control parental strict |

## 💡 Recomandări

**Folosește acest program dacă:**
- ✅ Nu ai parolă de Administrator
- ✅ Vrei blocare temporară pentru productivitate
- ✅ Copilul nu are cunoștințe tehnice avansate

**Folosește versiunea cu Admin (`browser_blocker.py`) dacă:**
- ✅ Ai acces Administrator
- ✅ Vrei blocare foarte sigură (control parental)
- ✅ Trebuie să împiedici complet accesul la internet

**Cea mai sigură soluție:**
- 🥇 **Blocarea la nivel de router** (configurare router)
- 🥈 **Windows Firewall** (`browser_blocker.py` cu admin)
- 🥉 **Proxy blocker** (acest program, fără admin)

## 📝 Licență

Acest tool este pentru administrare sistem, control parental sau productivitate personală.

## 🎉 Enjoy!

Program creat pentru a bloca distracțiile și a îmbunătăți productivitatea!
