# 🔒 Browser Blocker - Windows Firewall Tool

Un program simplu pentru Windows 10/11 care blochează accesul la internet al browserelor web folosind Windows Firewall.

## 🎯 Caracteristici

- ✅ **Interfață grafică intuitivă** - Butoane simple pentru a bloca/debloca browserele
- 🌐 **Suportă browsere populare**: Chrome, Edge, Firefox, Brave
- 🔐 **Reguli Windows Firewall** - Folosește protecție nativă Windows
- 🧹 **Cleanup automat** - Șterge regulile când închizi programul
- 📊 **Log în timp real** - Vezi exact ce se întâmplă
- 🔍 **Dry Run** - Testează fără a face modificări

## 📋 Cerințe

- Windows 10/11
- Python 3.6 sau mai nou (tkinter inclus)
- Drepturi de Administrator

## 🚀 Utilizare

### Mod Recomandat - Interfață Grafică (SIMPLU!)

**✨ METODA CEA MAI SIMPLĂ - Dublu-click:**

1. **Dublu-click pe `Browser_Blocker.vbs`** (sau `Browser_Blocker_Launcher.bat`)
2. Aprobă UAC prompt (cerere drepturi Administrator)
3. Interfața grafică se deschide automat!

Fișierele launcher (`*.vbs` și `*.bat`) cer automat drepturi de Administrator - nu trebuie să dai click dreapta!

**Alternativ - Direct Python:**
1. Click dreapta pe `browser_blocker.py`
2. Selectează **"Run as Administrator"**
3. Interfața se deschide cu 3 butoane:
   - 🚫 **BLOCK BROWSERS** - Blochează toate browserele
   - ✅ **UNBLOCK BROWSERS** - Deblochează browserele
   - 👁 **DRY RUN** - Vezi ce ar face fără a schimba nimic

### Mod Avansat - Linie de Comandă

```bash
# Deschide Command Prompt sau PowerShell ca Administrator
# (Win + X -> "Terminal (Admin)")

# Navighează la folder
cd C:\path\to\script

# Rulează cu GUI
python browser_blocker.py

# SAU mod CLI:
python browser_blocker.py --block      # Blochează browserele
python browser_blocker.py --unblock    # Deblochează browserele
python browser_blocker.py --dry-run    # Preview fără modificări

# Pentru a opri (CLI mode): apasă Ctrl+C
```

## 🖼️ Captură Interfață

Interfața GUI oferă:
- **Status vizual** - Vezi instant dacă browserele sunt blocate
- **Log detaliat** - Toate acțiunile sunt afișate în timp real
- **Butoane mari** - Ușor de folosit
- **Dialog de confirmare** - Te întreabă dacă vrei să deblochezi când închizi programul

## 🔧 Cum Funcționează

1. **Detectare** - Găsește executabilele browserelor în locații standard:
   - `C:\Program Files\...\chrome.exe`
   - `C:\Program Files\...\msedge.exe`
   - `C:\Program Files\...\firefox.exe`
   - `C:\Program Files\...\brave.exe`

2. **Blocare** - Adaugă reguli Windows Firewall:
   - Tip: Outbound (ieșire)
   - Acțiune: Block
   - Nume: `BrowserBlocker-<browser>-<pid>-<hash>`

3. **Cleanup** - Șterge automat regulile când:
   - Apeși butonul UNBLOCK
   - Închizi programul (cu confirmare)
   - Întrerupi cu Ctrl+C (CLI mode)

## ⚠️ Important

- **Drepturi Administrator** sunt obligatorii pentru a modifica Windows Firewall
- Programul **NU modifică** setările de sistem permanent
- La închidere, **toate regulile** create de program sunt șterse automat
- Funcționează doar pe **Windows** (folosește `netsh` și Windows Firewall)

## 🛡️ Securitate

- Programul creează doar reguli temporare
- Regulile sunt identificate unic cu PID-ul procesului
- Nu modifică configurația globală a firewall-ului
- Nu necesită dependințe externe (doar Python standard library)

## 📁 Fișiere Incluse

- **`Browser_Blocker.vbs`** - Launcher recomandat (silent, fără fereastră command prompt)
- **`Browser_Blocker_Launcher.bat`** - Launcher alternativ (batch script)
- **`browser_blocker.py`** - Programul principal Python
- **`README.md`** - Instrucțiuni de utilizare

**Care să folosesc?**
- 🥇 **Browser_Blocker.vbs** - Cel mai elegant, fără ferestre CMD
- 🥈 **Browser_Blocker_Launcher.bat** - Simplu și rapid
- 🥉 **browser_blocker.py** - Direct dacă știi să dai "Run as Administrator"

## 📝 Licență

Acest tool este pentru administrare sistem, control parental sau productivitate personală.

## 🐛 Troubleshooting

**Eroare: "Administrator privileges required"**
- Rulează programul ca Administrator (click dreapta -> Run as Administrator)

**Browser-ul încă are acces la internet**
- Verifică dacă browser-ul folosește un VPN sau proxy
- Unele browsere pot avea mai multe executabile

**Reguli rămase după închidere**
- Rulează: `python browser_blocker.py --unblock`
- Sau manual: Windows Defender Firewall -> Advanced Settings -> Outbound Rules
  - Caută reguli care încep cu "BrowserBlocker-"

## 🔄 Actualizări Viitoare (Opțional)

- [ ] Suport pentru mai multe browsere (Opera, Vivaldi, etc.)
- [ ] Programare automată (blocare între anumite ore)
- [ ] Whitelist pentru anumite site-uri
- [ ] Notificări system tray
