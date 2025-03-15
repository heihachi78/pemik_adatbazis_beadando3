from datetime import date, timedelta
from posixpath import sep
import pandas as pd
import os
from sqlalchemy import create_engine, text
import numpy as np
from tqdm import tqdm
import random
import string



print('Generating data...')



DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'postgrespass'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '6003'
DATABASE_NAME = 'prodf'
DATABASE_URL = f'postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

engine = create_engine(DATABASE_URL)
connection = engine.connect()
person_count = 20_000
purchase_count = 250
margin = 1.05




def generate_bank_accounts() -> str:
    return '-'.join([''.join([str(np.random.randint(0, 9)) for _ in range(8)]) for _ in range(3)])

def create_bank_account(created_at: date) -> int:
    try:
        return connection.execute(text("insert into bank_accounts (account_number, created_at) values (:account_number, :created_at) returning bank_account_id"),
                                  {"account_number": generate_bank_accounts(), "created_at": created_at}).fetchone()[0]
    except Exception as e:
        pass

def load_csv(file_name, sep=','):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, file_name)
    return pd.read_csv(file_path, sep=sep)

tm = load_csv('telepules_megye.csv', sep=';')
dm = pd.DataFrame(tm['megye'].unique(), columns=['megye'])
dc = pd.DataFrame(tm['telepules'].unique(), columns=['telepules'])

dm['id'] = None
for index, row in dm.iterrows():
    result = connection.execute(text("INSERT INTO regions (name, created_at) VALUES (:name, date'2010-07-19') RETURNING region_id"), {"name": row['megye']})
    dm.at[index, 'id'] = result.fetchone()[0]

connection.commit()

dc['id'] = None
for index, row in dc.iterrows():
    region_name = tm[tm['telepules'] == row['telepules']]['megye'].values[0]
    region_id = dm[dm['megye'] == region_name]['id'].values[0]
    result = connection.execute(text("INSERT INTO cities (name, region_id, created_at) VALUES (:name, :region_id, date'2010-07-19') RETURNING city_id"), {"name": row['telepules'], "region_id": region_id})
    dc.at[index, 'id'] = result.fetchone()[0]

connection.commit()

un = load_csv('utonevek_nem.csv', sep=';')
sz = load_csv('magyar_szavak.csv')

def generate_random_first_name(gender: int) -> str:
    filtered_un = un[un.iloc[:, 1] == gender]
    return filtered_un.sample().iloc[0, 0]

def generate_random_last_name() -> str:
    return sz.sample().iloc[0, 0].capitalize()

def generate_random_birth_place() -> int:
    return dc.sample().iloc[0, 1]

def generate_random_date(from_date: date, to_date: date) -> date:
    start_u = from_date.toordinal()
    end_u = to_date.toordinal()
    return date.fromordinal(np.random.randint(start_u, end_u))

def insert_person(first_name, last_name, birth_place_city_id, birth_date, birth_name, mother_name, death_date, gender_id, created_at, bank_account_id):
    try:
        connection.execute(text("INSERT INTO persons(first_name, last_name, birth_place_city_id, birth_date, birth_name, mother_name, death_date, gender_id, created_at, bank_account_id) VALUES (:first_name, :last_name, :birth_place_city_id, :birth_date, :birth_name, :mother_name, :death_date, :gender_id, :created_at, :bank_account_id)"), 
                            {"first_name": first_name, "last_name": last_name, "birth_place_city_id": birth_place_city_id, "birth_date": birth_date, "birth_name": birth_name, "mother_name": mother_name, "death_date": death_date, "gender_id": gender_id, "created_at": created_at, "bank_account_id": bank_account_id})
    except Exception as e:
        pass

def generate_random_gender():
    return np.random.randint(1, 3)

for i in tqdm(range(person_count)):
    try:
        rd = generate_random_date(date(2010, 1, 1), date(2025, 3, 10))
        bd = generate_random_date(date(1950, 1, 1), rd)
        rg = generate_random_gender()
        bai = create_bank_account(rd)
        insert_person(generate_random_last_name(),
                generate_random_first_name(rg),
                generate_random_birth_place(),
                bd,
                None if rg == 1 else None if generate_random_gender() == 1 else generate_random_last_name() + " " + generate_random_first_name(2),
                generate_random_last_name() + " " + generate_random_first_name(2),
                None,
                rg,
                rd,
                bai)
    except:
        pass

connection.commit()


pdf = pd.read_sql_query('select p.partner_id, p.created_at from partners p', con=connection)

def get_random_partner_id() -> int:
    return int(pdf.sample().iloc[0, 0])

def generate_random_batch_number() -> str:
    random_char = random.choice(string.ascii_uppercase)
    ret = "B-"
    if generate_random_gender() == 1:
        ret += str(np.random.randint(1, 9999))
    else:
        ret += random_char
    if generate_random_gender() == 1:
        ret += str(np.random.randint(1, 99)).zfill(2)
    else:
        ret += random_char
    if generate_random_gender() == 1:
        ret += "-" + str(np.random.randint(1, 99)).zfill(2)
    else:
        ret += random_char
    return ret + "/" + str(np.random.randint(1, 1000)) + "-" + random_char

def generate_random_case_number(partner_id) -> str:
    if partner_id % 2 == 0:
        return random.choice(string.ascii_uppercase) + str(np.random.randint(1000, 99999)) + "-" + random.choice(string.ascii_uppercase)
    if partner_id % 3 == 0:
        return random.choice(string.ascii_uppercase) + str(np.random.randint(10000, 999999))
    if partner_id % 5 == 0:
        return str(np.random.randint(10000, 999999)) + random.choice(string.ascii_uppercase)
    if partner_id % 7 == 0:
        return random.choice(string.ascii_uppercase) + "/" + str(np.random.randint(10000, 999999)) + "/" + random.choice(string.ascii_uppercase)
    return random.choice(string.ascii_uppercase) + "-" + str(np.random.randint(1, 999999)) + "/" + random.choice(string.ascii_uppercase) + str(np.random.randint(100000, 999999))


for i in tqdm(iterable=range(purchase_count)):
    partner_id = get_random_partner_id()
    batch_number = generate_random_batch_number()
    purchased_at = generate_random_date(from_date=pdf["created_at"].iloc[0], to_date=date(2025, 3, 10))
    created_at = generate_random_date(from_date=purchased_at, to_date=purchased_at + timedelta(days=np.random.randint(1, 31)))
    batch_purchase_value = np.random.randint(500_000, 5_000_000)
    try:
        purchase_id = connection.execute(text("INSERT INTO purchases(partner_id, batch_number, purchased_at, batch_purchase_value, created_at) VALUES (:partner_id, :batch_number, :purchased_at, :batch_purchase_value, :created_at) returning purchase_id"), 
                            {"partner_id": partner_id, "batch_number": batch_number, "purchased_at": purchased_at, "batch_purchase_value": batch_purchase_value, "created_at": created_at}).fetchone()[0]
    except Exception as e:
        pass

    connection.commit()

    sum_amount = 0
    cnt = 0
    while sum_amount < (batch_purchase_value * margin):
        partner_case_number = generate_random_case_number(partner_id)
        due_date = generate_random_date(from_date=purchased_at -  timedelta(days=np.random.randint(62, 365)), to_date=purchased_at - timedelta(days=np.random.randint(31, 62)))
        amount = np.random.randint(25_000, 1_000_000)
        try:
            case_id = connection.execute(text("INSERT INTO cases(purchase_id, partner_case_number, due_date, amount, created_at) VALUES (:purchase_id, :partner_case_number, :due_date, :amount, :created_at) returning case_id"), 
                                         {"purchase_id": purchase_id, "partner_case_number": partner_case_number, "due_date": due_date, "amount": amount, "created_at": created_at}).fetchone()[0]
            cnt += 1
            sum_amount += amount
        except Exception as e:
            pass

        person_ok = 0
        while person_ok == 0:
            person_id = np.random.randint(1, person_count)
            person_ok = connection.execute(text('select count(*) from persons p where p.person_id = :person_id and p.death_date is null'), {"person_id": person_id}).fetchone()[0]

        try:
            connection.execute(text("INSERT INTO debtors(case_id, person_id, debtor_type_id, created_at) VALUES (:case_id, :person_id, :debtor_type_id, :created_at)"), 
                                parameters={"case_id": case_id, "person_id": person_id, "debtor_type_id": 1, "created_at": created_at})
        except Exception as e:
            pass

        if np.random.randint(1, 25) == 11:
            death_date = generate_random_date(created_at, created_at + timedelta(days=np.random.randint(1, 365)))
            connection.execute(text("UPDATE persons SET death_date = :death_date WHERE person_id = :person_id"), {"death_date": death_date, "person_id": person_id})
            person_ok = 0
            while person_ok == 0:
                person_id = np.random.randint(1, person_count)
                person_ok = connection.execute(text('select count(*) from persons p where p.person_id = :person_id and p.death_date is null'), {"person_id": person_id}).fetchone()[0]
            try:
                new_created_at = generate_random_date(death_date, death_date + timedelta(days=np.random.randint(10, 100)))
                connection.execute(text("INSERT INTO debtors(case_id, person_id, debtor_type_id, created_at) VALUES (:case_id, :person_id, :debtor_type_id, :created_at)"), 
                                    {"case_id": case_id, "person_id": person_id, "debtor_type_id": 2, "created_at": new_created_at})
                connection.execute(text("UPDATE persons SET created_at = :new_created_at WHERE person_id = :person_id"), {"new_created_at": new_created_at, "person_id": person_id})
            except Exception as e:
                pass

        if np.random.randint(1, 5) == 3:
            person_ok = 0
            while person_ok == 0:
                person_id = np.random.randint(1, person_count)
                person_ok = connection.execute(text('select count(*) from persons p where p.person_id = :person_id and p.death_date is null'), {"person_id": person_id}).fetchone()[0]
            try:
                new_created_at = generate_random_date(created_at, date(2025, 3, 10))
                connection.execute(text("INSERT INTO debtors(case_id, person_id, debtor_type_id, created_at) VALUES (:case_id, :person_id, :debtor_type_id, :created_at)"), 
                                    {"case_id": case_id, "person_id": person_id, "debtor_type_id": 3, "created_at": new_created_at})
                connection.execute(text("UPDATE persons SET created_at = :new_created_at WHERE person_id = :person_id"), {"new_created_at": new_created_at, "person_id": person_id})
            except Exception as e:
                pass

    connection.commit()

    connection.execute(text("UPDATE cases SET calculated_purchase_value = round((amount/:sum_amount) * :batch_purchase_value, 3) WHERE purchase_id = :purchase_id"), {"purchase_id": purchase_id, "batch_purchase_value": batch_purchase_value, "sum_amount": sum_amount})

    connection.commit()

connection.execute(text("delete from persons p where not exists (select 1 from debtors d where d.person_id = p.person_id)"))

connection.commit()
    
print('Data generated successfully!')