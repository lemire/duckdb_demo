import duckdb
import os

# Function to create the database and tables
def create_database(db_name):
    # Check if database file already exists
    if os.path.exists(db_name):
        raise FileExistsError(f"Error: Database {db_name} already exists.")

    conn = duckdb.connect(db_name)

    # Create sequence for employer_id
    conn.execute('CREATE SEQUENCE employer_id_seq')

    # Create employers table
    conn.execute('''
        CREATE TABLE employers (
            employer_id INTEGER PRIMARY KEY DEFAULT NEXTVAL('employer_id_seq'),
            employer_name TEXT NOT NULL,
            sector TEXT NOT NULL,
            UNIQUE(employer_name, sector)
        )
    ''')

    # Create sequence for individual_id
    conn.execute('CREATE SEQUENCE individual_id_seq')

    # Create individuals table
    conn.execute('''
        CREATE TABLE individuals (
            individual_id INTEGER PRIMARY KEY DEFAULT NEXTVAL('individual_id_seq'),
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            UNIQUE(last_name, first_name, job_title)
        )
    ''')

    # Create salaries table
    conn.execute('''
        CREATE TABLE salaries (
            employer_id INTEGER,
            individual_id INTEGER,
            year INTEGER NOT NULL,
            salary REAL NOT NULL,
            benefits REAL NOT NULL,
            PRIMARY KEY (employer_id, individual_id, year),
            FOREIGN KEY (employer_id) REFERENCES employers (employer_id),
            FOREIGN KEY (individual_id) REFERENCES individuals (individual_id)
        )
    ''')

    return conn

# Function to load and normalize CSV data
def load_csv_to_db(csv_file, conn):
    # Create a temporary table to hold raw CSV data
    conn.execute('''
        CREATE TEMPORARY TABLE raw_data (
            sector TEXT,
            last_name TEXT,
            first_name TEXT,
            salary TEXT,
            benefits TEXT,
            employer_name TEXT,
            job_title TEXT,
            year TEXT
        )
    ''')

    # Load CSV directly into temporary table
    conn.execute(f'''
        INSERT INTO raw_data
        SELECT * FROM read_csv_auto('{csv_file}', header=true)
    ''')

    # Normalize and insert into employers
    conn.execute('''
        INSERT INTO employers (employer_name, sector)
        SELECT DISTINCT employer_name, sector
        FROM raw_data
        ON CONFLICT (employer_name, sector) DO NOTHING
    ''')

    # Normalize and insert into individuals
    conn.execute('''
        INSERT INTO individuals (last_name, first_name, job_title)
        SELECT DISTINCT last_name, first_name, job_title
        FROM raw_data
        ON CONFLICT (last_name, first_name, job_title) DO NOTHING
    ''')

    # Insert into salaries, joining with employers and individuals to get IDs
    conn.execute('''
        INSERT INTO salaries (employer_id, individual_id, year, salary, benefits)
        SELECT 
            e.employer_id,
            i.individual_id,
            CAST(r.year AS INTEGER),
            CAST(REPLACE(r.salary, ',', '') AS REAL),
            CAST(REPLACE(r.benefits, ',', '') AS REAL)
        FROM raw_data r
        JOIN employers e ON r.employer_name = e.employer_name AND r.sector = e.sector
        JOIN individuals i ON r.last_name = i.last_name 
            AND r.first_name = i.first_name 
            AND r.job_title = i.job_title
        ON CONFLICT (employer_id, individual_id, year)
        DO UPDATE SET 
            salary = EXCLUDED.salary,
            benefits = EXCLUDED.benefits
    ''')

    # Drop temporary table
    conn.execute('DROP TABLE raw_data')

    conn.commit()

# Main function
def main(csv_file, db_name):
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    # Create database and load data
    try:
        conn = create_database(db_name)
        try:
            load_csv_to_db(csv_file, conn)
            print(f"Database {db_name} created and data loaded successfully from {csv_file}.")
        except Exception as e:
            print(f"An error occurred while loading data: {e}")
        finally:
            conn.close()
    except FileExistsError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred while creating database: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python create_sunshine_db.py <csv_file> <db_name>")
    else:
        main(sys.argv[1], sys.argv[2])