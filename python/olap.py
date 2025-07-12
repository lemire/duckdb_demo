import duckdb
import sys

def print_table(rows, headers):
    if not rows:
        print("Aucune donnée trouvée.")
        return
    
    # Calculer la largeur maximale pour chaque colonne
    widths = [len(header) for header in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)))
    
    # Afficher l'en-tête
    header_row = " | ".join(f"{header:<{widths[i]}}" for i, header in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Afficher les lignes
    for row in rows:
        row_str = " | ".join(f"{str(value):<{widths[i]}}" for i, value in enumerate(row))
        print(row_str)

def perform_olap_operations(db_name):
    # Connexion à la base de données DuckDB
    conn = duckdb.connect(db_name)
    
    # Roll-up: Agrégation vers un niveau supérieur (moyenne des salaires par secteur et année)
    roll_up_query = """
    SELECT e.sector, s.year, AVG(s.salary) as average_salary
    FROM salaries s
    JOIN employers e ON s.employer_id = e.employer_id
    GROUP BY e.sector, s.year
    """
    result = conn.execute(roll_up_query).fetchall()
    print("\nRoll-up (moyenne des salaires par secteur et année):")
    print_table(result, ["Secteur", "Année", "Salaire moyen"])
    
    # Drill-down: Décomposition vers un niveau plus détaillé (moyenne des salaires par employeur)
    drill_down_query = """
    SELECT e.employer_name, s.year, AVG(s.salary) as average_salary
    FROM salaries s
    JOIN employers e ON s.employer_id = e.employer_id
    WHERE e.sector = 'Universities'
    GROUP BY e.employer_name, s.year
    """
    result = conn.execute(drill_down_query).fetchall()
    print("\nDrill-down (moyenne des salaires par employeur dans le secteur Universities):")
    print_table(result, ["Employeur", "Année", "Salaire moyen"])
    
    # Dice: Sélection d'un sous-ensemble spécifique (salaires pour employeurs 'Ontario' et titres 'software')
    dice_query = """
    SELECT i.last_name, i.first_name, e.employer_name, s.salary
    FROM salaries s
    JOIN individuals i ON s.individual_id = i.individual_id
    JOIN employers e ON s.employer_id = e.employer_id
    WHERE e.employer_name LIKE 'Ontario%' AND i.job_title ILIKE '%software%'
    """
    result = conn.execute(dice_query).fetchall()
    print("\nDice (salaires des employés avec 'software' dans le titre pour employeurs commençant par 'Ontario'):")
    print_table(result, ["Nom", "Prénom", "Employeur", "Salaire"])
    
    # Slice: Réduction de la dimensionnalité (moyenne des salaires pour 'Pay Equity Commission')
    slice_query = """
    SELECT s.year, AVG(s.salary) as average_salary
    FROM salaries s
    JOIN employers e ON s.employer_id = e.employer_id
    WHERE e.employer_name = 'Pay Equity Commission'
    GROUP BY s.year
    """
    result = conn.execute(slice_query).fetchall()
    print("\nSlice (moyenne des salaires par année pour Pay Equity Commission):")
    print_table(result, ["Année", "Salaire moyen"])
    
    # Pivot: Transformation des salaires moyens par employeur, secteurs en colonnes
    pivot_query = """
    PIVOT (
        SELECT s.year, e.sector, AVG(s.salary) as average_salary
        FROM salaries s
        JOIN employers e ON s.employer_id = e.employer_id
        GROUP BY s.year, e.sector
    ) ON sector IN ('Universities', 'Colleges')
    USING AVG(average_salary)
    GROUP BY year
    """
    result = conn.execute(pivot_query).fetchall()
    print("\nPivot (salaires moyens par employeur, secteurs en colonnes):")
    print_table(result, ["Employeur", "Universities", "Colleges"])
    
    # Approximate_count_distinct: Nombre approximatif d'employeurs uniques par secteur
    approx_count_query = """
    SELECT e.sector, APPROX_COUNT_DISTINCT(e.employer_id) as approx_employer_count
    FROM employers e
    GROUP BY e.sector
    """
    result = conn.execute(approx_count_query).fetchall()
    print("\nApproximate count distinct (nombre approximatif d'employeurs par secteur):")
    print_table(result, ["Secteur", "Nombre approximatif d'employeurs"])
    
    # Fermeture de la connexion
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python olap_operations.py <database_name>")
        sys.exit(1)
    db_name = sys.argv[1]
    perform_olap_operations(db_name)