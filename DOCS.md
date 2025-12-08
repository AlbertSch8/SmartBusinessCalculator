# Dokumentace – Chytrá kalkulačka pro podnikatele (v1.0 + JSON)

## 1. Účel aplikace
Aplikace slouží pro malé podnikatele, kteří potřebují snadno počítat cenu zakázky.
Uživatel může do zakázky přidávat položky a program vypočítá mezisoučet, DPH a cenu s DPH.
Výpočet probíhá ve worker vlákně (threading).

Verze 2.0 přidává možnost **uložit zakázku do JSON** a **znovu ji načíst**.

---

## 2. Hlavní části programu

### OrderManager
- spravuje zakázku
- ukládá a vypisuje položky
- po načtení JSON dokáže položky kompletně nahradit (`replace_items`)

### LineItem
- jedna položka v zakázce (název, množství, cena, DPH)
- umí spočítat mezisoučet a DPH

### CalculationWorker
- běží v samostatném vlákně
- čeká na úkoly („CALCULATE“)
- provádí výpočet zakázky bez blokování hlavního vlákna

### JSON Storage (json_storage.py)
- `save_order_to_json(...)` – uloží zakázku do souboru `data/orders.json`
- `load_order_from_json(...)` – načte zakázku ze stejného souboru

---

## 3. Menu aplikace

1. Přidat položku  
2. Vypsat položky  
3. Spustit výpočet (worker thread)  
4. Zobrazit poslední výsledek  
5. Uložit zakázku do JSON  
6. Načíst zakázku z JSON  
0. Ukončit program  

---

## 4. Formát JSON souboru

Soubor `data/orders.json` má tuto strukturu:

```json
{
    "order_name": "Název zakázky",
    "items": [
        {
            "name": "Položka",
            "quantity": 5,
            "unit_price": 120,
            "vat_rate": 21
        }
    ]
}
5. Použité knihovny
threading – vlákna a synchronizace

queue – komunikace mezi vlákny

json – ukládání a načítání dat

žádné externí knihovny

6. Možné budoucí rozšíření
automatické ukládání (autosave) ve vlastním vlákně

správa více zakázek

export do CSV/PDF

jednoduché GUI