import os
import random
import string

from datetime import date, timedelta
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
from tqdm import tqdm



print('Generating data...')

PURCHASE_COUNT = 240
MIN_BATCH_VALUE = 250_000
MAX_BATCH_VALUE = 25_000_000
MIN_AMOUNT = 25_000
MAX_AMOUNT = 250_000
AMOUNT_OUTLIER_RATE = 10
MARGIN = 1.05
TYPE2_DEBTOR_RATE = 100
TYPE3_DEBTOR_RATE = 10
MIN_INTEREST = 5
MAX_INTEREST = 25
CLOSED_CASE_RATE = 0.6

DATABASE_USER = 'cms'
DATABASE_PASSWORD = 'pass'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5433'
DATABASE_NAME = 'cms'
DATABASE_URL = f'postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

engine = create_engine(DATABASE_URL)
connection = engine.connect()

def initialize():
    print('initializing...')
    cnt_exist = connection.execute(text("select count(*) from partners")).fetchone()[0]

    if cnt_exist == 0:
        connection.execute(text("INSERT INTO public.debtor_types(name, created_at) VALUES ('adós', date'2015-01-01');"))
        connection.execute(text("INSERT INTO public.debtor_types(name, created_at) VALUES ('örökös', date'2015-01-01');"))
        connection.execute(text("INSERT INTO public.debtor_types(name, created_at) VALUES ('adóstárs', date'2015-01-01');"))

        connection.execute(text("INSERT INTO public.genders(name, created_at) VALUES ('ferfi', date'2015-01-01');"))
        connection.execute(text("INSERT INTO public.genders(name, created_at) VALUES ('no', date'2015-01-01');"))

        connection.execute(text("INSERT INTO public.sectors(name, created_at) VALUES ('B2B', date'2015-01-01');"))
        connection.execute(text("INSERT INTO public.sectors(name, created_at) VALUES ('Telekommunikacio', date'2015-01-01');"))
        connection.execute(text("INSERT INTO public.sectors(name, created_at) VALUES ('Bank', date'2015-01-01');"))
        connection.execute(text("INSERT INTO public.sectors(name, created_at) VALUES ('Kozmu', date'2015-01-01');"))

        connection.execute(text("INSERT INTO public.partners(name, sector_id, created_at) VALUES ('Tartozas Kezelo Zrt.', 1, date'2015-03-05');"))
        connection.execute(text("INSERT INTO public.partners(name, sector_id, created_at) VALUES ('Debt Hungary Zrt.', 1, date'2019-07-11');"))
        connection.execute(text("INSERT INTO public.partners(name, sector_id, created_at) VALUES ('Vodafone', 2, date'2015-01-01');"))
        connection.execute(text("INSERT INTO public.partners(name, sector_id, created_at) VALUES ('Magyar Telekom Nyrt.', 2, date'2015-07-28');"))
        connection.execute(text("INSERT INTO public.partners(name, sector_id, created_at) VALUES ('One Magyarország', 2, date'2016-05-09');"))
        connection.execute(text("INSERT INTO public.partners(name, sector_id, created_at) VALUES ('OTP Bank', 3, date'2015-11-23');"))
        connection.execute(text("INSERT INTO public.partners(name, sector_id, created_at) VALUES ('Erste Bank', 3, date'2017-11-05');"))
        connection.execute(text("INSERT INTO public.partners(name, sector_id, created_at) VALUES ('ELMŰ-ÉMÁSZ Energiaszolgáltató Zrt.', 4, date'2016-02-17');"))
        connection.execute(text("INSERT INTO public.partners(name, sector_id, created_at) VALUES ('E.ON Energiamegoldások Kft.', 4, date'2015-06-22');"))

        connection.commit()
    else:
        print('skipping init')

def load_csv(file_name, sep=','):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, file_name)
    return pd.read_csv(file_path, sep=sep)

def insert_region(dm: pd.DataFrame):
    dm['id'] = None
    pb = tqdm(dm.iterrows(), total=dm.shape[0])
    for index, row in pb:
        result = connection.execute(text("INSERT INTO regions (name, created_at) VALUES (:name, date'2015-01-01') RETURNING region_id"), {"name": row['megye']})
        dm.at[index, 'id'] = result.fetchone()[0]
    pb.close()
    return dm

def insert_city(dc: pd.DataFrame, dr: pd.DataFrame, rc: pd.DataFrame):
    dc['id'] = None
    pb = tqdm(dc.iterrows(), total=dc.shape[0])
    for index, row in pb:
        region_name = rc[rc['telepules'] == row['telepules']]['megye'].values[0]
        region_id = dr[dr['megye'] == region_name]['id'].values[0]
        result = connection.execute(text("INSERT INTO cities (name, region_id, created_at) VALUES (:name, :region_id, date'2015-01-01') RETURNING city_id"), {"name": row['telepules'], "region_id": region_id})
        dc.at[index, 'id'] = result.fetchone()[0]
    pb.close()
    return dc

def generate_random_date(from_date: date, to_date: date) -> date:
    start_u = from_date.toordinal()
    end_u = to_date.toordinal()
    return date.fromordinal(np.random.randint(start_u, end_u))

def generate_random_gender():
    return np.random.randint(1, 3)

def generate_bank_account_number() -> str:
    return '-'.join([''.join([str(np.random.randint(0, 9)) for _ in range(8)]) for _ in range(3)])

def create_bank_account(created_at: date) -> int:
    return connection.execute(text("insert into bank_accounts (account_number, created_at) values (:account_number, :created_at) returning bank_account_id"), {"account_number": generate_bank_account_number(), "created_at": created_at}).fetchone()[0]

def generate_random_last_name(dw: pd.DataFrame) -> str:
    return dw.sample().iloc[0, 0].capitalize()

def generate_random_first_name(gender: int, dn: pd.DataFrame) -> str:
    filtered_un = dn[dn.iloc[:, 1] == gender]
    return filtered_un.sample().iloc[0, 0]

def generate_random_birth_place(dc: pd.DataFrame) -> int:
    return dc.sample().iloc[0, 1]

def generate_random_birth_name(rg: int, dw, dn) -> str:
    return None if rg == 1 else None if generate_random_gender() == 1 else generate_random_last_name(dw) + " " + generate_random_first_name(2, dn)

def generate_random_mother_name(dw, dn):
    return generate_random_last_name(dw) + " " + generate_random_first_name(2, dn)

def insert_person(first_name, last_name, birth_place_city_id, birth_date, birth_name, mother_name, death_date, gender_id, created_at):
    return connection.execute(text("INSERT INTO persons(first_name, last_name, birth_place_city_id, birth_date, birth_name, mother_name, death_date, gender_id, created_at) " +
                                            "VALUES (:first_name, :last_name, :birth_place_city_id, :birth_date, :birth_name, :mother_name, :death_date, :gender_id, :created_at) returning person_id"), 
                        {"first_name": first_name, 
                            "last_name": last_name, 
                            "birth_place_city_id": birth_place_city_id, 
                            "birth_date": birth_date, 
                            "birth_name": birth_name, 
                            "mother_name": mother_name, 
                            "death_date": death_date, 
                            "gender_id": gender_id, 
                            "created_at": created_at}).fetchone()[0]

def generate_random_person(dw: pd.DataFrame, dn: pd.DataFrame, dc: pd.DataFrame):
    rd = generate_random_date(date(2015, 1, 1), date(2024, 12, 31))
    bd = generate_random_date(date(1950, 1, 1), rd)
    rg = generate_random_gender()
    ln = generate_random_last_name(dw)
    fn = generate_random_first_name(rg, dn)
    bp = generate_random_birth_place(dc)
    bn = generate_random_birth_name(rg, dw, dn)
    mn = generate_random_mother_name(dw, dn)
    person_id = insert_person(ln, fn, bp, bd, bn,mn, None, rg, rd)
    return person_id

def get_random_partner_id(ps: pd.DataFrame) -> int:
    return int(ps.sample().iloc[0, 0])

def generate_random_batch_number() -> str:
    random_char = random.choice(string.ascii_uppercase)
    return "B/" + str(np.random.randint(1000, 9999)) + "-" + random_char + str(np.random.randint(1000, 9999))

def insert_purchase(partner_id, batch_number, purchased_at, batch_purchase_value, created_at):
    purchase_id = connection.execute(text("INSERT INTO purchases(partner_id, batch_number, purchased_at, batch_purchase_value, created_at) VALUES (:partner_id, :batch_number, :purchased_at, :batch_purchase_value, :created_at) returning purchase_id"), 
                        {"partner_id": partner_id, 
                            "batch_number": batch_number, 
                            "purchased_at": purchased_at, 
                            "batch_purchase_value": batch_purchase_value, 
                            "created_at": created_at}).fetchone()[0]
    return purchase_id

def generate_random_purchase(ps):
    partner_id = get_random_partner_id(ps)
    batch_number = generate_random_batch_number()
    purchased_at = generate_random_date(from_date=ps["created_at"].iloc[0], to_date=date(2024, 12, 31))
    batch_purchase_value = np.random.randint(MIN_BATCH_VALUE, MAX_BATCH_VALUE)
    created_at = generate_random_date(from_date=purchased_at, to_date=purchased_at + timedelta(days=np.random.randint(1, 31)))
    purchase_id = insert_purchase(partner_id, batch_number, purchased_at, batch_purchase_value, created_at)
    return partner_id, purchase_id, purchased_at, batch_purchase_value, created_at

def generate_random_case_number(partner_id: int) -> str:
    if partner_id % 2 == 0:
        return random.choice(string.ascii_uppercase) + str(np.random.randint(1000, 99999)) + "-" + random.choice(string.ascii_uppercase)
    if partner_id % 3 == 0:
        return random.choice(string.ascii_uppercase) + str(np.random.randint(10000, 999999))
    if partner_id % 5 == 0:
        return str(np.random.randint(10000, 999999)) + random.choice(string.ascii_uppercase)
    if partner_id % 7 == 0:
        return random.choice(string.ascii_uppercase) + "/" + str(np.random.randint(10000, 999999)) + "/" + random.choice(string.ascii_uppercase)
    return random.choice(string.ascii_uppercase) + "-" + str(np.random.randint(1, 999999)) + "/" + random.choice(string.ascii_uppercase) + str(np.random.randint(100000, 999999))

def insert_case(purchase_id, partner_case_number, due_date, amount, created_at, interest_rate):
    case_id = connection.execute(text("INSERT INTO cases(purchase_id, partner_case_number, due_date, amount, created_at, interest_rate) VALUES (:purchase_id, :partner_case_number, :due_date, :amount, :created_at, :interest_rate) returning case_id"),
                        {"purchase_id": purchase_id, 
                            "partner_case_number": partner_case_number, 
                            "due_date": due_date, 
                            "amount": amount, 
                            "created_at": created_at,
                            "interest_rate": interest_rate}).fetchone()[0]
    return case_id

def generate_random_case(partner_id, purchased_at, created_at):
    partner_case_number = generate_random_case_number(partner_id)
    from_date = purchased_at -  timedelta(days=np.random.randint(62, 365))
    to_date = purchased_at - timedelta(days=np.random.randint(31, 62))
    due_date = generate_random_date(from_date=from_date, to_date=to_date)
    amount = np.random.randint(MIN_AMOUNT, MAX_AMOUNT)
    interest_rate = np.random.randint(MIN_INTEREST, MAX_INTEREST) / 100.
    if np.random.randint(1, AMOUNT_OUTLIER_RATE) == 7:
        amount += MAX_AMOUNT
    case_id = insert_case(purchase_id, partner_case_number, due_date, amount, created_at, interest_rate)
    return case_id, amount

def insert_debtor(case_id, person_id, created_at, type):
    return connection.execute(text("INSERT INTO debtors(case_id, person_id, debtor_type_id, created_at) VALUES (:case_id, :person_id, :debtor_type_id, :created_at) returning debtor_id"), 
                            parameters={"case_id": case_id, 
                                        "person_id": person_id, 
                                        "debtor_type_id": type, 
                                        "created_at": created_at}).fetchone()[0]

def update_calculated_purchase_value(purchase_id, batch_purchase_value, sum_amount):
    connection.execute(text("UPDATE cases SET calculated_purchase_value = round((amount/:sum_amount) * :batch_purchase_value, 3) WHERE purchase_id = :purchase_id"), 
                        {"purchase_id": purchase_id, "batch_purchase_value": batch_purchase_value, "sum_amount": sum_amount})

def insert_account_holder(person_id, bank_account_id, created_at):
    connection.execute(text("INSERT INTO account_holders(person_id, bank_account_id, created_at, valid_from) VALUES (:person_id, :bank_account_id, :created_at, :created_at)"), 
                        {"person_id": person_id, "bank_account_id": bank_account_id, "created_at": created_at})

def generate_debtor_all(dw, dn, dc, created_at, case_id, type):
    person_id = generate_random_person(dw, dn, dc)
    bank_account_id = create_bank_account(created_at)
    insert_account_holder(person_id, bank_account_id, created_at)
    debtor_id = insert_debtor(case_id, person_id, created_at, type)
    return person_id, debtor_id, bank_account_id

def handle_death(created_at, person_id):
    death_date = generate_random_date(created_at, date(2024, 12, 31))
    connection.execute(text("UPDATE persons SET death_date = :death_date WHERE person_id = :person_id"), {"death_date": death_date, "person_id": person_id})
    return death_date

def generate_payments():
    connection.execute(text("call generate_payments();"))

def get_case_numbers():
    all_cases = connection.execute(text("select count(*) from cases")).fetchone()[0]
    closed_cases = connection.execute(text("select count(*) from cases where closed_at is not null")).fetchone()[0]
    return all_cases, closed_cases

def calculate_interet():
    connection.execute(text("call calculate_interest();"))

try:
    initialize()
    rc = load_csv('data/telepules_megye.csv', sep=';')
    dn = load_csv('data/utonevek_nem.csv', sep=';')
    dw = load_csv('data/magyar_szavak.csv')

    dr = pd.DataFrame(rc['megye'].unique(), columns=['megye'])
    dc = pd.DataFrame(rc['telepules'].unique(), columns=['telepules'])
    ps = pd.read_sql_query('select p.partner_id, p.created_at from partners p', con=connection)

    dr = insert_region(dr)
    dc = insert_city(dc, dr, rc)
    connection.commit()
    
    pb = tqdm(iterable=range(PURCHASE_COUNT))
    for i in pb:
        try:
            partner_id, purchase_id, purchased_at, batch_purchase_value, created_at = generate_random_purchase(ps)
            sum_amount = 0
            cnt = 0
            while sum_amount < (batch_purchase_value * MARGIN):
                case_id, amount = generate_random_case(partner_id, purchased_at, created_at)
                person_id, _, _ = generate_debtor_all(dw, dn, dc, created_at, case_id, 1)
                gad = np.random.randint(1, TYPE3_DEBTOR_RATE)
                if gad == 3:
                    generate_debtor_all(dw, dn, dc, generate_random_date(created_at, date(2024, 12, 31)), case_id, 3)
                gad = np.random.randint(1, TYPE2_DEBTOR_RATE)
                if gad == 2:
                    death_date = handle_death(created_at, person_id)
                    generate_debtor_all(dw, dn, dc, generate_random_date(death_date, date(2024, 12, 31)), case_id, 2)
                cnt += 1
                sum_amount += amount
            update_calculated_purchase_value(purchase_id, batch_purchase_value, sum_amount)
            connection.commit()
        except Exception as e:
            connection.rollback()
    pb.close()

    all_cases, closed_cases = get_case_numbers()
    while closed_cases / all_cases < CLOSED_CASE_RATE:
        print('generating payment data...')
        generate_payments()
        connection.commit()
        all_cases, closed_cases = get_case_numbers()

    print('calculating interest...')
    calculate_interet()
    connection.commit()

    print('Data generated successfully!')
except Exception as e:
    print(type(e))
    print(e.args)
    print(e)
    print('main loop')
    connection.rollback()
    print('Error during data generation:', e)
