import sys
import json
import tkinter as tk
from tkinter import filedialog
import os.path

# Kontrola importu tabulate
print("Kontroluji přítomnost knihovny 'tabulate'...")
try:
    from tabulate import tabulate
    print("Knihovna 'tabulate' úspěšně načtena.")
except ImportError:
    print("Chyba: Knihovna 'tabulate' není nainstalována.")
    print("Nainstalujte ji příkazem: pip install tabulate")
    input("Stiskněte Enter pro ukončení...")
    sys.exit(1)

# Kontrola importu tkinter
print("Kontroluji přítomnost knihovny 'tkinter'...")
try:
    root = tk.Tk()
    root.withdraw()
    print("Knihovna 'tkinter' úspěšně načtena.")
except Exception as e:
    print(f"Chyba při načítání 'tkinter': {str(e)}")
    print("Pokud používáte Linux, nainstalujte tkinter příkazem: sudo apt-get install python3-tk")
    print("Na Windows by měl být tkinter součástí Pythonu.")
    input("Stiskněte Enter pro ukončení...")
    sys.exit(1)

# Funkce pro zaokrouhlení hodnot na 2 desetinná místa, pokud je třeba
def round_if_needed(value):
    print(f"Zaokrouhluji hodnotu: {value}")
    if isinstance(value, (int, float)) and value == int(value):
        return value
    if isinstance(value, float):
        rounded = round(value, 2)
        print(f"Zaokrouhleno na: {rounded}")
        return rounded
    return value

# Funkce pro vytvoření tabulky a vrácení jejího textového formátu
def create_table(data, table_title, start_index=1):
    print(f"Vytvářím tabulku: {table_title}")
    headers = ["Measuring Number", "coreVoltage", "frequency", "averageHashRate", "averageTemperature", "efficiencyJHT", "averageVRTemp"]
    table_data = []
    
    for i, entry in enumerate(data, start=start_index):
        print(f"Zpracovávám řádek {i}...")
        row = [
            i,
            entry["coreVoltage"],
            entry["frequency"],
            round_if_needed(entry["averageHashRate"]),
            round_if_needed(entry["averageTemperature"]),
            round_if_needed(entry["efficiencyJTH"]),
            round_if_needed(entry["averageVRTemp"])
        ]
        table_data.append(row)
    
    # Vytvoření textového výstupu tabulky s tabulátorem jako oddělovačem
    table_output = f"\n{table_title}\n"
    table_output += tabulate(table_data, headers=headers, tablefmt="tsv", numalign="center", stralign="center")
    table_output += "\n"  # Přidání prázdného řádku pro oddělení tabulek
    
    # Výpis do konzole
    print(table_output)
    
    return table_output

# Funkce pro sloučení měření a odstranění duplicit
def merge_measurements(all_results, most_efficient, top_performers):
    print("Sloučím měření z all_results, most_efficient a top_performers...")
    
    # Vytvoření seznamu všech měření
    combined_measurements = []
    
    # Přidání měření z all_results
    combined_measurements.extend(all_results)
    
    # Přidání měření z most_efficient
    for measurement in most_efficient:
        if measurement not in combined_measurements:
            combined_measurements.append(measurement)
    
    # Přidání měření z top_performers
    for measurement in top_performers:
        if measurement not in combined_measurements:
            combined_measurements.append(measurement)
    
    print(f"Celkový počet měření po sloučení: {len(combined_measurements)}")
    return combined_measurements

# Hlavní funkce
def main():
    print("Spouštím skript...")
    try:
        # Vytvoření dialogového okna pro výběr souboru
        print("Otevírám dialogové okno pro výběr souboru...")
        file_path = filedialog.askopenfilename(
            title="Vyberte soubor",
            filetypes=[("Textové soubory", "*.txt"), ("JSON soubory", "*.json"), ("Všechny soubory", "*.*")]
        )
        
        if not file_path:
            print("Nebyl vybrán žádný soubor. Ukončuji...")
            return
        
        print(f"Vybraný soubor: {file_path}")
        
        # Extrakce názvu souboru bez přípony a vytvoření názvu výstupního souboru
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = f"{base_name}.txt"
        print(f"Výstupní soubor bude pojmenován: {output_file}")
        
        # Načtení JSON souboru
        with open(file_path, 'r', encoding='utf-8') as file:
            print("Načítám soubor...")
            parser_data = json.load(file)
        
        print("Soubor načten úspěšně. Zpracovávám data...")
        
        # Extrakce dat
        all_results = parser_data.get("all_results", [])
        most_efficient = parser_data.get("most_efficient", [])
        top_performers = parser_data.get("top_performers", [])
        
        print(f"Počet měření v 'all_results': {len(all_results)}")
        print(f"Počet měření v 'most_efficient': {len(most_efficient)}")
        print(f"Počet měření v 'top_performers': {len(top_performers)}")
        
        # Sloučení všech měření do první tabulky (včetně most_efficient a top_performers)
        complete_measurements = merge_measurements(all_results, most_efficient, top_performers)
        
        # Vytvoření tabulek a shromažďování jejich textového výstupu
        output_content = []
        
        # První tabulka: Všechna měření (včetně most_efficient a top_performers)
        print(f"Vytvářím tabulku z kompletních měření s {len(complete_measurements)} měřeními...")
        table1 = create_table(complete_measurements, "ALL RESULTS")
        output_content.append(table1)
        
        # Druhá tabulka: Most Efficient (top 5 podle parseru)
        print("Vytvářím tabulku pro 'most_efficient'...")
        table2 = create_table(most_efficient, "MOST EFFICIENT")
        output_content.append(table2)
        
        # Třetí tabulka: Top Performers (top 5 podle parseru)
        print("Vytvářím tabulku pro 'top_performers'...")
        table3 = create_table(top_performers, "TOP PERFORMANCE")
        output_content.append(table3)
        
        # Uložení tabulek do souboru
        print(f"Ukládám tabulky do souboru: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(output_content))
        print(f"Tabulky byly úspěšně uloženy do souboru: {output_file}")
        
    except Exception as e:
        print(f"Došlo k chybě: {str(e)}")
        print("Skript se ukončí po stisknutí Enter...")
    finally:
        input("\nStiskněte Enter pro ukončení...")

if __name__ == "__main__":
    try:
        print("Inicializuji skript...")
        main()
    except Exception as e:
        print(f"Kritická chyba při inicializaci: {str(e)}")
        input("Stiskněte Enter pro ukončení...")