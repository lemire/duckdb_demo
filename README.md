# OLAP sur la base de données shunshine

La base de données Sunshine de l’Ontario, officiellement appelée Public Sector Salary Disclosure (divulgation des salaires du secteur public), est une liste annuelle publiée par le gouvernement de l’Ontario, conformément à la Public Sector Salary Disclosure Act de 1996. Elle recense les employés du secteur public et des organisations financées par la province qui gagnent un salaire de 100 000 $ ou plus par an. Cette initiative vise à promouvoir la transparence et la responsabilité dans l’utilisation des fonds publics.
Nous pouvons utiliser cette base de données pour tester des requêtes OLAP.

## Prérequis

Avant de procéder, assurez-vous d'installer Python 3.7 ou une version ultérieure sur votre machine.

- **Pour Windows** :
  1. Téléchargez l'installateur depuis https://www.python.org/downloads/windows/
  2. Lancez l'installateur et cochez l'option "Add Python to PATH" avant de cliquer sur "Install Now".
  3. Ouvrez l'invite de commandes :
     - Cliquez sur le menu Démarrer (icône Windows en bas à gauche), tapez "Invite de commandes" ou "cmd", puis cliquez sur l'application correspondante.
  4. Vérifiez l'installation en tapant :
     ```
     python --version
     ```
     ou
     ```
     python3 --version
     ```

- **Pour macOS** :
  1. Ouvrez le Terminal.
  2. Installez Homebrew si ce n'est pas déjà fait :
     ```
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
  3. Installez Python 3 avec Homebrew :
     ```
     brew install python
     ```
  4. Vérifiez l'installation :
     ```
     python3 --version
     ```

Le nom de l'interpréteur Python sur votre système peut être `python` ou `python3` selon votre système. 


## Environnement virtuel et installation des dépendances

Pour isoler l'environnement de développement et gérer les dépendances, il est recommandé d'utiliser un environnement virtuel Python. Voici les étapes :

1. **Création de l'environnement virtuel** :
   - Ouvrez un terminal et placez-vous dans le répertoire principal du projet.
   - Exécutez la commande suivante pour créer un environnement virtuel nommé `venv` :
     ```bash
     python3 -m venv venv
     ```

2. **Activation de l'environnement virtuel** :
   - Sur macOS et Linux :
     ```bash
     source venv/bin/activate
     ```
   - Sur Windows :
     ```bash
     venv\Scripts\activate
     ```

   Une fois activé, vous devriez voir le préfixe `(venv)` dans votre terminal.

3. **Installation des dépendances** :
   - Assurez-vous que le fichier `requirements.txt` est présent dans le répertoire principal du projet.
   - Installez les dépendances nécessaires en exécutant :
     ```bash
     pip install -r requirements.txt
     ```

4. **Vérification de l'installation** :
   - Pour vérifier que toutes les dépendances sont correctement installées, exécutez :
     ```bash
     pip list
     ```

5. **Désactivation de l'environnement virtuel** :
   - Une fois terminé, vous pouvez désactiver l'environnement virtuel en exécutant :
     ```bash
     deactivate
     ```



## Obtention des fichiers du projet

Pour obtenir les fichiers du projet, vous pouvez télécharger une archive ZIP depuis GitHub :

1. Rendez-vous sur la page du projet : https://github.com/lemire/olap_demo
2. Cliquez sur le bouton vert « Code » puis sur « Download ZIP ».
3. Décompressez l’archive téléchargée sur votre ordinateur.
4. Ouvrez le dossier extrait dans votre terminal ou explorateur de fichiers pour suivre les instructions d’installation ci-dessus.

## Création de la base de données


Placez-vous dans le répartoire principal du projet. La commande

```bash
python python/create.py  data/tbs-pssd-compendium-salary-disclosed-2024-en-utf-8-2025-03-26.csv database.bin
```

ou 

```bash
python3 python/create.py  data/tbs-pssd-compendium-salary-disclosed-2024-en-utf-8-2025-03-26.csv database.bin
```

devrait créer une base de données "database.bin" normalisée.





## Description du schéma de la base de données

La base de données est conçue pour gérer les informations des employés du secteur public, en se concentrant sur leurs employeurs, leurs données personnelles et leurs rémunérations annuelles. Elle comprend quatre tables principales : `employers`, `individuals`, `salaries` et une table système `sqlite_sequence`. La table `employers` stocke les informations sur les employeurs, avec un identifiant unique (`employer_id`), le nom de l'employeur (`employer_name`) et son secteur d'activité (`sector`), garantissant l'unicité de la combinaison nom-secteur. La table `individuals` recense les employés avec un identifiant unique (`individual_id`), leur nom de famille (`last_name`), prénom (`first_name`) et titre de poste (`job_title`), avec une contrainte d'unicité sur ces trois champs pour éviter les doublons. Des index sont définis sur `individuals.last_name`, `salaries.employer_id` et `salaries.individual_id` pour optimiser les requêtes.

La table `salaries` est le cœur de la base, reliant les employeurs et les employés via leurs identifiants (`employer_id` et `individual_id`) pour enregistrer les salaires (`salary`), avantages (`benefits`) et l'année (`year`). Une clé primaire composite sur `employer_id`, `individual_id` et `year` assure l'unicité des enregistrements annuels. Les clés étrangères établissent des relations avec les tables `employers` et `individuals`, garantissant l'intégrité référentielle. La table `sqlite_sequence` est utilisée par SQLite pour gérer les séquences des clés primaires auto-incrémentées. Ce schéma normalisé permet des requêtes efficaces sur les données salariales tout en maintenant une structure claire et cohérente.




## Table employers
- **employer_id** : INTEGER, clé primaire, auto-incrémenté
- **employer_name** : TEXT, nom de l'employeur, non nul
- **sector** : TEXT, secteur d'activité, non nul
- **Contrainte** : UNIQUE(employer_name, sector)

## Table sqlite_sequence
- **name** : TEXT, nom de la table
- **seq** : INTEGER, valeur de la séquence
- **Description** : Gère les séquences pour les clés primaires auto-incrémentées

## Table individuals
- **individual_id** : INTEGER, clé primaire, auto-incrémenté
- **last_name** : TEXT, nom de famille, non nul
- **first_name** : TEXT, prénom, non nul
- **job_title** : TEXT, titre de poste, non nul
- **Contrainte** : UNIQUE(last_name, first_name, job_title)
- **Index** : idx_individuals_last_name ON last_name

## Table salaries
- **employer_id** : INTEGER, clé étrangère référençant employers(employer_id)
- **individual_id** : INTEGER, clé étrangère référençant individuals(individual_id)
- **year** : INTEGER, année, non nul
- **salary** : REAL, salaire, non nul
- **benefits** : REAL, avantages, non nul
- **Clé primaire** : (employer_id, individual_id, year)
- **Index** : idx_salaries_employer_id ON employer_id
- **Index** : idx_salaries_individual_id ON individual_id


## Requêtes OLAP


Lancez les requêtes avec la commande

```bash
python3 python/olap.py database.bin
```

ou 


```bash
python python/olap.py database.bin
```

## Résultat attendu

```

Roll-up (moyenne des salaires par secteur et année):
Secteur                                                  | Année | Salaire moyen     
-------------------------------------------------------------------------------------
Seconded (Education)*                                    | 2024  | 140793.70608618952
Hospitals & Boards of Public Health                      | 2024  | 125070.47068445323
Government of Ontario - Judiciary                        | 2024  | 252989.3396412037 
Crown Agencies                                           | 2024  | 134380.20020193592
Seconded (Tourism, Culture and Sport)*                   | 2024  | 164468.33333333334
Municipalities & Services                                | 2024  | 129793.56994108942
Seconded (Health)*                                       | 2024  | 351025.7552083333 
Ontario Power Generation                                 | 2024  | 167894.58760089971
Seconded (Natural Resources and Forestry)*               | 2024  | 124451.66666666667
Universities                                             | 2024  | 162657.09056290291
Seconded (Attorney General)*                             | 2024  | 184807.78125      
Seconded (Children, Community and Social Services)*      | 2024  | 132979.171875     
Seconded (Citizenship and Multiculturalism)*             | 2024  | 129375.298828125  
Other Public Sector Employers                            | 2024  | 133772.44516580293
Colleges                                                 | 2024  | 127213.46430454799
School Boards                                            | 2024  | 127756.60419959223
Government of Ontario - Legislative Assembly and Offices | 2024  | 142334.92694289293
Government of Ontario - Ministries                       | 2024  | 130699.68700503888
Seconded (Solicitor General)*                            | 2024  | 134213.2036830357 

Drill-down (moyenne des salaires par employeur dans le secteur Universities):
Employeur                                    | Année | Salaire moyen     
-------------------------------------------------------------------------
Toronto Metropolitan University              | 2024  | 163716.77204457365
Carleton University                          | 2024  | 155391.69703415278
Ontario College Of Art And Design University | 2024  | 127792.44928977273
St. Jerome’s University                      | 2024  | 167832.72275641025
McMaster Divinity College                    | 2024  | 148712.6          
University Of Waterloo                       | 2024  | 163925.40422466592
Saint Paul University                        | 2024  | 125496.53247070312
Nipissing University                         | 2024  | 148424.1328598485 
University Of Guelph                         | 2024  | 157305.93033705186
York University                              | 2024  | 173237.03149495114
Lakehead University                          | 2024  | 151953.9504250919 
Brescia University College                   | 2024  | 120538.5          
Trent University                             | 2024  | 152701.80043129539
King’s University College                    | 2024  | 150696.33781934305
Brock University                             | 2024  | 170945.34118271954
Wilfrid Laurier University                   | 2024  | 157465.2061987705 
Victoria University                          | 2024  | 142360.26694542254
St. Peter’s Seminary                         | 2024  | 130812.4109375    
Ontario Tech University                      | 2024  | 156153.29446373458
Trinity College                              | 2024  | 140294.05249023438
University Of Toronto                        | 2024  | 163159.4354400102 
Universite De L’Ontario Francais             | 2024  | 142631.14         
Laurentian University Of Sudbury             | 2024  | 147515.0919306507 
University Of Sudbury                        | 2024  | 171057.6640625    
University Of Ottawa                         | 2024  | 164561.53503091578
Huron University College                     | 2024  | 138808.13695406626
Queen’s University                           | 2024  | 172498.18825741526
Algoma University                            | 2024  | 145674.25789882598
McMaster University                          | 2024  | 165949.82227207095
University Of Windsor                        | 2024  | 152353.42103324915
University Of St. Michael’s College          | 2024  | 157171.36225328947
University Of Western Ontario                | 2024  | 164741.23460428894
Université De Hearst                         | 2024  | 133438.21279761905
Northern Ontario School Of Medicine          | 2024  | 149445.72952302633

Dice (salaires des employés avec 'software' dans le titre pour employeurs commençant par 'Ontario'):
Nom               | Prénom          | Employeur                                                 | Salaire       
----------------------------------------------------------------------------------------------------------------
Cerelli           | Nancy           | Ontario Educational Communications Authority (TV Ontario) | 106446.3984375
Lee               | Simon           | Ontario Health                                            | 105410.5390625
Naseer            | Muhammad        | Ontario Health                                            | 120589.65625  
Niazmand          | Najla           | Ontario Health                                            | 120636.890625 
Singh             | Dalveer         | Ontario Health                                            | 104898.9296875
Zhang             | Zhen            | Ontario Health                                            | 128492.3984375
Zhou              | Ye              | Ontario Health                                            | 104898.828125 
Batista Freijanes | Alejandro       | Ontario Health                                            | 120548.046875 
Blaga             | Lucian          | Ontario Health                                            | 104423.5234375
Cacenco           | Vladimir M      | Ontario Health                                            | 121866.921875 
Kim               | Hongwan         | Ontario Health                                            | 122800.3828125
Lam               | Kam Chuen       | Ontario Health                                            | 116905.4375   
Liu               | Gang            | Ontario Health                                            | 105410.609375 
Ma                | Chenghua        | Ontario Health                                            | 111141.78125  
Pala              | Bharathi Alisha | Ontario Health                                            | 106716.3828125
Wiszniewski       | Sebastian       | Ontario Health                                            | 127770.2421875
Durson            | Indra           | Ontario Health                                            | 124474.921875 
Ferguson          | Brandon A       | Ontario Health                                            | 105410.5625   
Joukova           | Tatiana         | Ontario Health                                            | 133926.453125 
Kanagasabapathy   | Balakumar       | Ontario Health                                            | 100890.4609375
Lee               | Michelle        | Ontario Educational Communications Authority (TV Ontario) | 110343.328125 
Rygiel            | Mateusz         | Ontario Health                                            | 122312.2421875
Taylor            | Shirley         | Ontario Health                                            | 111692.546875 
Wang              | Yongzhong       | Ontario Health                                            | 109278.0625   
Wen               | Xinhua          | Ontario Health                                            | 124876.96875  
Xu                | Hai Yan         | Ontario Cannabis Retail Corporation                       | 139524.890625 
Arab              | Mahmood-Reza    | Ontario Health                                            | 104898.796875 
Hloba             | Yevhen          | Ontario Health                                            | 114532.4765625
Li                | Jie             | Ontario Health                                            | 108578.8671875
Mikesewala        | Yasmin          | Ontario Health                                            | 105410.578125 
Xie               | Ting            | Ontario Health                                            | 113578.953125 
Dasanayaka        | Sandaruwan      | Ontario Health                                            | 104898.8828125
Fonseka           | Chandima        | Ontario Health                                            | 116154.390625 
Hawkins           | Jennifer        | Ontario Health                                            | 105849.640625 
Sedighi           | Amir            | Ontario Health                                            | 149957.125    
Sun               | Wei             | Ontario Health                                            | 120589.6328125
Wang              | Xiaomei         | Ontario Health                                            | 124858.2109375
Xu                | Cong            | Ontario Health                                            | 119418.859375 
Arthur            | John            | Ontario Health                                            | 105410.578125 
Dinesan           | Priya           | Ontario Health                                            | 107749.4765625
Fu                | Bing            | Ontario Health                                            | 120589.6484375
Jose              | Jane Elizabeth  | Ontario Health                                            | 104865.4609375
Qin               | Bill            | Ontario Health                                            | 134632.40625  
Sazonova          | Lioudmila       | Ontario Health                                            | 105410.5703125
Sivarasathurai    | Latheesan       | Ontario Health                                            | 121760.3984375
Bui               | Duyen           | Ontario Health                                            | 107613.1484375
Chau              | David W         | Ontario Health                                            | 120589.6875   
Jacobs            | Leo             | Ontario Cannabis Retail Corporation                       | 153583.3125   
Lennox            | Keith           | Ontario Educational Communications Authority (TV Ontario) | 104007.953125 
Lim               | Reayen Ron      | Ontario Health                                            | 124464.4921875
Zhou              | Jianzhou        | Ontario Cannabis Retail Corporation                       | 127958.96875  
Huang             | Jian            | Ontario Health                                            | 121224.7890625
Lou               | Dong            | Ontario Health                                            | 104963.7734375
Yi                | Jun             | Ontario Health                                            | 106528.546875 
Zuo               | Rui Song        | Ontario Health                                            | 119418.8671875
Bai               | Sheng           | Ontario Health                                            | 127605.90625  
Bordun            | Sergiy          | Ontario Health                                            | 105410.546875 
Jing              | Li              | Ontario Health                                            | 112857.609375 
Parmar            | Shailendrasinh  | Ontario Health                                            | 110163.203125 
Sun               | Zhu Wen         | Ontario Health                                            | 105410.5625   
Bedi              | Deep Singh      | Ontario Health                                            | 114571.46875  
Chau              | Johnson         | Ontario Health                                            | 108688.703125 
El-Hallak         | Walid           | Ontario Health                                            | 122811.2109375
Han               | Hao Peter       | Ontario Health                                            | 121380.109375 
Haque             | Syed Mairajul   | Ontario Health                                            | 104387.1796875
Kalambet          | Igor            | Ontario Health                                            | 136751.375    
Nanushi           | Valentina       | Ontario Health                                            | 147829.9375   
Syal              | Ashish          | Ontario Health                                            | 104898.8125   
Wang              | Jason           | Ontario Health                                            | 106904.6796875
Yep               | Daniel          | Ontario Health                                            | 106916.15625  
Aghababyan        | Aleksandr       | Ontario Health                                            | 117423.1171875
Chawla            | Kartik          | Ontario Health                                            | 104387.1328125
Waita             | Naomi           | Ontario Health                                            | 104898.7734375
Balayan           | Madhusudhan     | Ontario Health                                            | 105410.5703125
Hu                | Xiaodong        | Ontario Health                                            | 110385.546875 
Shi               | Hang            | Ontario Health                                            | 129335.4765625
Stark             | Corey           | Ontario Health                                            | 104898.8671875
Stewart           | Ashley          | Ontario Health                                            | 150389.734375 
Tran              | Chi-Lea         | Ontario Educational Communications Authority (TV Ontario) | 105681.0625   
Yamada            | Joseph          | Ontario Health                                            | 129529.546875 
Zhou              | Gang            | Ontario Health                                            | 121801.6484375
Broytman          | Dmitry          | Ontario Educational Communications Authority (TV Ontario) | 101984.953125 
Chen              | Hui             | Ontario Health                                            | 119960.03125  
Goodine           | Richard         | Ontario Educational Communications Authority (TV Ontario) | 106387.3125   
He                | Yubo            | Ontario Health                                            | 105410.546875 
Hoad              | Christian       | Ontario Educational Communications Authority (TV Ontario) | 106451.8125   
Kim               | Kwonil          | Ontario Health                                            | 126277.1328125
Lin               | Shaole          | Ontario Health                                            | 120589.640625 
Liu               | Xin             | Ontario Health                                            | 105410.5390625
Park              | Jeesun          | Ontario Health                                            | 120589.6328125
Perera            | Thenkuttige     | Ontario Health                                            | 106350.71875  
Shaik             | Nazia B         | Ontario Educational Communications Authority (TV Ontario) | 103889.3828125
Wang              | Shanshan        | Ontario Health                                            | 140274.875    
Cheng             | Manchung        | Ontario Health                                            | 106864.7578125
Kurian            | Liza            | Ontario Health                                            | 104387.171875 
Lin               | Hai             | Ontario Health                                            | 106365.8671875
Liu               | Michael         | Ontario Health                                            | 105410.5390625
Deneweth          | Glenn           | Ontario Health atHome                                     | 120068.421875 
Ghafouri          | Behnam          | Ontario Cannabis Retail Corporation                       | 131535.90625  
Hui               | Michael         | Ontario Health                                            | 140709.71875  
Kulkarni          | Hrishikesh      | Ontario Lottery And Gaming Corporation                    | 157184.40625  
Maserrat          | Abdol           | Ontario Health                                            | 130850.4765625
Scaletchi         | Victor          | Ontario Health                                            | 121323.65625  
Zhang             | Linhan          | Ontario Health                                            | 104387.140625 
Bodean            | Petrisor R      | Ontario Health                                            | 104387.109375 
Cong              | Peijun          | Ontario Health                                            | 128683.796875 
Dehghani          | Daryoosh        | Ontario Health                                            | 107457.34375  
Hudson            | Warren          | Ontario Health                                            | 109612.0703125
Kim               | Sae-Il          | Ontario Health                                            | 127470.9921875
Kolhe             | Pradnya         | Ontario Health                                            | 124778.546875 
Ma                | Yuefei          | Ontario Health                                            | 120589.6875   

Slice (moyenne des salaires par année pour Pay Equity Commission):
Année | Salaire moyen     
--------------------------
2024  | 137576.02403846153

Pivot (salaires moyens par employeur, secteurs en colonnes):
Employeur | Universities       | Colleges          
---------------------------------------------------
2024      | 162657.09056290291 | 127213.46430454799

Approximate count distinct (nombre approximatif d'employeurs par secteur):
Secteur                                                  | Nombre approximatif d'employeurs
-------------------------------------------------------------------------------------------
Hospitals & Boards of Public Health                      | 160                             
Seconded (Children, Community and Social Services)*      | 2                               
Seconded (Natural Resources and Forestry)*               | 1                               
Crown Agencies                                           | 84                              
Government of Ontario - Ministries                       | 27                              
Municipalities & Services                                | 440                             
Ontario Power Generation                                 | 4                               
Seconded (Citizenship and Multiculturalism)*             | 4                               
School Boards                                            | 98                              
Government of Ontario - Judiciary                        | 2                               
Other Public Sector Employers                            | 1559                            
Seconded (Education)*                                    | 31                              
Universities                                             | 30                              
Seconded (Tourism, Culture and Sport)*                   | 2                               
Colleges                                                 | 21                              
Government of Ontario - Legislative Assembly and Offices | 7                               
Seconded (Attorney General)*                             | 1                               
Seconded (Health)*                                       | 3      
Seconded (Solicitor General)*                            | 14                              
```

## Explication des requêtes OLAP dans `python/olap.py`

### 1. Roll-up
```sql
SELECT e.sector, s.year, AVG(s.salary) as average_salary
FROM salaries s
JOIN employers e ON s.employer_id = e.employer_id
GROUP BY e.sector, s.year
```
Cette requête calcule le salaire moyen par secteur et par année. Elle regroupe les données selon le secteur d'activité des employeurs et l'année, permettant une vue agrégée des rémunérations.

### 2. Drill-down
```sql
SELECT e.employer_name, s.year, AVG(s.salary) as average_salary
FROM salaries s
JOIN employers e ON s.employer_id = e.employer_id
WHERE e.sector = 'Universities'
GROUP BY e.employer_name, s.year
```
Cette requête affine l'analyse en calculant le salaire moyen par employeur et par année, mais uniquement pour le secteur "Universities". Elle permet d'explorer les détails des employeurs dans ce secteur.

### 3. Dice
```sql
SELECT i.last_name, i.first_name, e.employer_name, s.salary
FROM salaries s
JOIN individuals i ON s.individual_id = i.individual_id
JOIN employers e ON s.employer_id = e.employer_id
WHERE e.employer_name LIKE 'Ontario%' AND i.job_title ILIKE '%software%'
```
Cette requête extrait les salaires des employés dont le titre de poste contient "software" et dont l'employeur commence par "Ontario". Elle cible un sous-ensemble précis des données.

### 4. Slice
```sql
SELECT s.year, AVG(s.salary) as average_salary
FROM salaries s
JOIN employers e ON s.employer_id = e.employer_id
WHERE e.employer_name = 'Pay Equity Commission'
GROUP BY s.year
```
Cette requête calcule le salaire moyen par année pour l'employeur "Pay Equity Commission". Elle réduit la dimensionnalité en se concentrant sur un employeur spécifique.

### 5. Pivot
```sql
PIVOT (
    SELECT s.year, e.sector, AVG(s.salary) as average_salary
    FROM salaries s
    JOIN employers e ON s.employer_id = e.employer_id
    GROUP BY s.year, e.sector
) ON sector IN ('Universities', 'Colleges')
USING AVG(average_salary)
GROUP BY year
```
Cette requête transforme les données pour afficher les salaires moyens par employeur, avec les secteurs "Universities" et "Colleges" comme colonnes. Elle facilite la comparaison entre ces secteurs.

### 6. Approximate Count Distinct
```sql
SELECT e.sector, APPROX_COUNT_DISTINCT(e.employer_id) as approx_employer_count
FROM employers e
GROUP BY e.sector
```
Cette requête utilise une fonction d'estimation pour compter approximativement le nombre d'employeurs uniques par secteur. Cela est utile pour des analyses rapides sur de grandes bases de données.

## Différences entre DuckDB et SQLite
DuckDB offre des fonctionnalités avancées qui ne sont pas disponibles dans SQLite, notamment :
1. **Support des requêtes OLAP** : DuckDB est optimisé pour les analyses de données volumineuses, avec des fonctions comme `PIVOT` et `APPROX_COUNT_DISTINCT`.
2. **Performance** : DuckDB utilise un moteur en colonnes, ce qui le rend plus rapide pour les agrégations et les analyses complexes.
2. **Interopérabilité** : DuckDB peut facilement intégrer des formats de données comme Parquet et CSV, facilitant l'analyse directe sans conversion préalable.

SQLite, en revanche, est principalement conçu pour des bases de données transactionnelles légères et ne dispose pas de ces capacités analytiques avancées.



