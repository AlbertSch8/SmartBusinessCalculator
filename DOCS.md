# Dokumentace – Chytrá kalkulačka pro podnikatele (v1.0)

## 1. Účel aplikace
Aplikace slouží jako jednoduchý nástroj pro malé podnikatele nebo živnostníky.  
Umožňuje vytvořit zakázku, přidat do ní položky a spočítat finální cenu zakázky včetně DPH.  
Současně ukazuje použití více vláken v Pythonu.

---

## 2. Hlavní části projektu

### a) `OrderManager`
- stará se o jednu zakázku
- ukládá položky (LineItem)
- umožňuje bezpečné (thread-safe) přidávání položek
- poskytuje kopii položek pro výpočet ve vlákně

### b) `LineItem`
- reprezentuje jednu položku v zakázce
- obsahuje: název, množství, cenu za jednotku a sazbu DPH
- umí spočítat mezisoučet a výši DPH

### c) `CalculationWorker` (worker vlákno)
- běží na pozadí
- čeká na úkoly v `queue.Queue`
- zpracovává úkol `"CALCULATE"`
- vypočítá:
  - mezisoučet
  - DPH
  - výslednou cenu
- výsledek uloží do sdíleného slovníku

---

## 3. Vlákna a synchronizace
- **Hlavní vlákno**: obsluhuje uživatelské menu a zadávání položek.
- **Worker vlákno**: provádí výpočty zakázky.
- Komunikace mezi vlákny:
  - `queue.Queue` (bez potřeby ručního zamykání)
- Sdílená data (`result_dict`) chráněna:
  - `threading.Lock`
- Položky zakázky jsou chráněny:
  - interním zámkem v `OrderManager`

---

## 4. Uživatelské ovládání
Menu umožňuje:
1. přidat položku  
2. zobrazit položky  
3. spustit výpočet  
4. zobrazit poslední výsledek  
0. ukončit aplikaci  

---

## 5. Rozšiřitelnost
Tento projekt lze dále rozšířit například o:
- ukládání dat do souborů (JSON, CSV)
- autosave pomocí dalšího vlákna
- evidenci více zakázek
- generování reportů
- grafické rozhraní (Tkinter)
