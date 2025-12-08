# Chytrá kalkulačka pro podnikatele (v2.0)

Tento projekt je jednoduchá konzolová aplikace v Pythonu.  
Umožňuje vytvořit zakázku, přidávat položky (název, množství, cena, DPH), provádět výpočet přes vlákno a nově také **ukládat a načítat zakázku do/z JSON souboru**.

---

## ✨ Funkce
- vytvoření zakázky  
- přidávání položek  
- výpis položek  
- výpočet mezisoučtu, DPH a celkové ceny (ve worker vlákně)  
- **uložení zakázky do `data/orders.json`**  
- **načtení zakázky ze `data/orders.json`**

---

## 🧵 Vícevláknová architektura
- hlavní vlákno: obsluhuje menu a vstupy
- worker vlákno: provádí výpočty (`CalculationWorker`)
- komunikace přes `queue.Queue`
- synchronizace sdílených dat pomocí `threading.Lock`

---

## ▶️ Spuštění
V rootu projektu spusť:

git clone https://github.com/TVOJ-USERNAME/TVOJE-REPO.git
cd TVOJE-REPO
python main.py