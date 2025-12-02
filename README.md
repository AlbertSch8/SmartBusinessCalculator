# Chytrá kalkulačka pro podnikatele (v1.0)

Tento projekt je jednoduchá konzolová aplikace v Pythonu.  
Umožňuje vytvořit zakázku, přidávat položky (název, množství, cena, DPH) a spočítat celkovou cenu zakázky.  
Výpočet probíhá v samostatném vlákně pomocí `threading`.

## ✨ Funkce
- vytvoření zakázky
- přidávání položek
- výpis všech položek
- výpočet přes worker vlákno (oddělení UI a výpočtu)
- zobrazení posledního výsledku

## 🧵 Vícevláknová architektura
- **Hlavní vlákno**: uživatelské menu (UI)
- **Worker vlákno**: provádí výpočty na pozadí
- Komunikace mezi vlákny probíhá přes `queue.Queue`
- Sdílená data jsou chráněna `threading.Lock`

## ▶️ Spuštění
```bash
python main.py