from sqlalchemy import Table, create_engine, insert, MetaData, select
import time
import random



DATABASE_USER = 'cms'
DATABASE_PASSWORD = 'pass'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5433'
DATABASE_NAME = 'cms'
DATABASE_URL = f'postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

engine = create_engine(DATABASE_URL)
metadata = MetaData()
test = Table('test', metadata, autoload_with=engine)
stmt = insert(test).values(n=1)
stmt2 = select(test)

x=0
while True:
    #time.sleep(round(random.uniform(0.1,1), 2))
    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
            conn.execute(stmt2)
            x+=1
            print(f"Record {x} inserted successfully")
    except Exception as e:
        print(f"An error occurred: {e}")
