import os
import random
import string

from datetime import date, timedelta
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
from datetime import datetime



PURCHASE_COUNT = 1
MIN_BATCH_VALUE = 250_000
MAX_BATCH_VALUE = 25_000_000
MIN_AMOUNT = 25_000
MAX_AMOUNT = 250_000
AMOUNT_OUTLIER_RATE = 10
MARGIN = 1.02
TYPE2_DEBTOR_RATE = 100
TYPE3_DEBTOR_RATE = 10
MIN_INTEREST = 3
MAX_INTEREST = 25



DATABASE_USER_CMS = 'cms'
DATABASE_USER_FIN = 'fin'
DATABASE_PASSWORD = 'pass'
DATABASE_HOST = 'localhost'
DATABASE_PORT_1 = '5431'
DATABASE_PORT_2 = '5432'
POOL_PORT = '5433'
DATABASE_PORT_4 = '5434'
DATABASE_NAME_CMS = 'cms'
DATABASE_NAME_FIN = 'fin'
SRV1_DB_CONN_INFO = f'postgresql+psycopg2://{DATABASE_USER_CMS}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT_1}/{DATABASE_NAME_CMS}'
SRV2_DB_CONN_INFO = f'postgresql+psycopg2://{DATABASE_USER_CMS}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT_2}/{DATABASE_NAME_CMS}'
FIN_DB_CONN_INFO = f'postgresql+psycopg2://{DATABASE_USER_FIN}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT_4}/{DATABASE_NAME_FIN}'
POOL_CONN_INFO = f'postgresql+psycopg2://{DATABASE_USER_CMS}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{POOL_PORT}/{DATABASE_NAME_CMS}'

engine = create_engine(POOL_CONN_INFO)
connection = engine.connect()

def load_csv(file_name, sep=','):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, file_name)
    return pd.read_csv(file_path, sep=sep)

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
    return int(dc.sample().iloc[0, 0])

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
    rd = generate_random_date(date(2015, 1, 1), datetime.today())
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
    case_id = connection.execute(text("INSERT INTO cases(purchase_id, partner_case_number, due_date, amount, current_amount, created_at, interest_rate, current_interest_amount, current_interest_rate, current_due_date) VALUES \
                                      (:purchase_id, :partner_case_number, :due_date, :amount, :amount, :created_at, :interest_rate, 0, :interest_rate, :due_date) returning case_id"),
                        {"purchase_id": purchase_id, 
                         "partner_case_number": partner_case_number, 
                         "due_date": due_date, 
                         "amount": amount, 
                         "created_at": created_at,
                         "interest_rate": interest_rate}).fetchone()[0]
    return case_id

def generate_random_case(purchase_id, partner_id, purchased_at, created_at):
    partner_case_number = generate_random_case_number(partner_id)
    from_date = purchased_at -  timedelta(days=np.random.randint(62, 365))
    to_date = purchased_at - timedelta(days=np.random.randint(31, 62))
    due_date = generate_random_date(from_date=from_date, to_date=to_date)
    amount = np.random.randint(MIN_AMOUNT, MAX_AMOUNT)
    interest_rate = np.random.randint(MIN_INTEREST, MAX_INTEREST) / 100.
    if np.random.randint(1, AMOUNT_OUTLIER_RATE) == 7:
        amount += MAX_AMOUNT
    case_id = insert_case(purchase_id=purchase_id, partner_case_number=partner_case_number, due_date=due_date, amount=amount, created_at=created_at, interest_rate=interest_rate)
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

def calculate_interest():
    connection.execute(text("call calculate_interest_all();"))

def new_purchase(partner_id, purchase_id, purchased_at, batch_purchase_value, created_at) -> None:
    try:
        
        dn = load_csv(file_name='../../tools/data/utonevek_nem.csv', sep=';')
        dw = load_csv(file_name='../../tools/data/magyar_szavak.csv')

        dc = pd.read_sql_query(sql='select r.city_id, r."name" from cities r where r.deleted_at is null', con=connection)

        try:
            sum_amount = 0
            cnt = 0
            while sum_amount < (batch_purchase_value * MARGIN):
                try:
                    case_id, amount = generate_random_case(purchase_id=purchase_id, partner_id=partner_id, purchased_at=purchased_at, created_at=created_at)
                    _, _, _ = generate_debtor_all(dw=dw, dn=dn, dc=dc, created_at=created_at, case_id=case_id, type=1)
                    cnt += 1
                    sum_amount += amount
                    connection.commit()
                except Exception as e:
                    print(type(e))
                    print(e.args)
                    print(e)    
                    connection.rollback()
            update_calculated_purchase_value(purchase_id=purchase_id, batch_purchase_value=batch_purchase_value, sum_amount=sum_amount)
            connection.commit()
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)    
            connection.rollback()

        calculate_interest()
        connection.commit()

    except Exception as e:
        print(type(e))
        print(e.args)
        print(e)
        connection.rollback()
