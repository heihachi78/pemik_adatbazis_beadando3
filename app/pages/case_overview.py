from math import e
from sqlalchemy import create_engine, text
from nicegui import ui, app
import pandas as pd
import theme
import config.database


def show_case_overview():
    with theme.frame('Ügy áttekintése'):
        ui.page_title('Ügy áttekintése')

        engine = create_engine(config.database.POOL_CONN_INFO)
        connection = engine.connect()

        def get_cases():
            qr = pd.read_sql_query('''
select 
	c.case_id, 
	concat(c.case_id, ' ', c.partner_case_number) vis
from 
	cases c
where
    c.deleted_at is null
order by 
    c.case_id desc
''', con=connection)
            ret = {}
            for i in range(len(qr)):
                ret[int(qr['case_id'][i])] = qr['vis'][i]
            return ret
        
        cases_set = get_cases()
        cases_list = list(cases_set)

        def filter_table(value):
            data_table1.update_from_pandas(pd.read_sql_query(text(sql1), params={'case_id':cases_list[value]}, con=connection))
            data_table2.update_from_pandas(pd.read_sql_query(text(sql2), params={'case_id':cases_list[value]}, con=connection))
            data_table3.update_from_pandas(pd.read_sql_query(text(sql3), params={'case_id':cases_list[value]}, con=connection))
            data_table4.update_from_pandas(pd.read_sql_query(text(sql4), params={'case_id':cases_list[value]}, con=connection))
            data_table5.update_from_pandas(pd.read_sql_query(text(sql5), params={'case_id':cases_list[value]}, con=connection))
            data_table6.update_from_pandas(pd.read_sql_query(text(sql6), params={'case_id':cases_list[value]}, con=connection))

        case_id = ui.select(label= 'Ügy kiválasztása', options=cases_set, with_input=True).props('size=100').on('update:model-value', lambda e: filter_table(e.args['value']))

        sql1 = f'''
select 
	c.case_id,
    p.purchase_id,
	r."name",
	c.calculated_purchase_value,
	c.amount,
	p.batch_number,
	p.purchased_at::date
from 
	cases c,
	purchases p,
	partners r
where 
	r.deleted_at is null and
	p.deleted_at is null and
	c.deleted_at is null and
	p.purchase_id = c.purchase_id and
	r.partner_id = p.partner_id and
    c.case_id = :case_id
'''
        ui.label('Vásárlási adatok').style('color: #6E93D6; font-size: 300%; font-weight: 300')
        try:
            data_table1 = ui.table.from_pandas(pd.read_sql_query(text(sql1), params={'case_id':-1}, con=connection), row_key='case_id', pagination=5).classes('w-full')
        except:
            pass


        sql2 = f'''
select 
	c.case_id, 
	c.partner_case_number,
	c.due_date,
	c.closed_at::date,
	c.amount,
	c.interest_rate,
	c.current_amount,
	c.current_interest_rate,
	c.current_interest_amount
from 
	cases c 
where 
	c.deleted_at is null and
    c.case_id = :case_id
'''
        ui.label('Ügy részletei').style('color: #6E93D6; font-size: 300%; font-weight: 300')
        try:
            data_table2 = ui.table.from_pandas(pd.read_sql_query(text(sql2), params={'case_id':-1}, con=connection), row_key='case_id', pagination=5).classes('w-full')
        except:
            pass


        sql6 = f'''
select 
	c.case_id, 
	d.debtor_id,
	d.person_id,
	t."name" debtor_type,
	p.first_name,
	p.last_name,
	p.death_date,
    d.created_at::date
from 
	cases c,
	debtors d,
	debtor_types t,
	persons p
where 
	c.deleted_at is null and
	d.deleted_at is null and
	t.deleted_at is null and
	p.deleted_at is null and
	d.case_id = c.case_id and
	t.debtor_type_id = d.debtor_type_id and
	p.person_id = d.person_id and
    c.case_id = :case_id
order by 1 desc
'''
        ui.label('Adósok részletei').style('color: #6E93D6; font-size: 300%; font-weight: 300')
        try:
            data_table6 = ui.table.from_pandas(pd.read_sql_query(text(sql6), params={'case_id':-1}, con=connection), row_key='case_id', pagination=5).classes('w-full')
        except:
            pass




        sql3 = f'''
select 
	c.case_id,
	d.debt_id,
	d.calculated_from,
	d.calculated_to,
	d.debt_amount,
	d.interest_rate,
	d.interest_amount,
	d.created_at::date
from
	cases c,
	debts d
where 
	c.deleted_at is null and
	d.deleted_at is null and
	d.case_id = c.case_id and
    c.case_id = :case_id
order by d.calculated_from desc
'''
        ui.label('Kamatok részletei').style('color: #6E93D6; font-size: 300%; font-weight: 300')
        try:
            data_table3 = ui.table.from_pandas(pd.read_sql_query(text(sql3), params={'case_id':-1}, con=connection), row_key='case_id', pagination=5).classes('w-full')
        except:
            pass

        sql4 = f'''
select 
	c.case_id,
	p.payment_id,
	a.account_number,
	p.payment_date,
	p.amount,
	p.created_at::date
from
	cases c,
	payments p,
	bank_accounts a
where 
	c.deleted_at is null and
	p.deleted_at is null and
	a.deleted_at is null and
	a.bank_account_id = p.bank_account_id and
	p.case_id = c.case_id and
    c.case_id = :case_id
order by
	p.payment_date desc
'''
        ui.label('Befizetések részletei').style('color: #6E93D6; font-size: 300%; font-weight: 300')
        try:
            data_table4 = ui.table.from_pandas(pd.read_sql_query(text(sql4), params={'case_id':-1}, con=connection), row_key='case_id', pagination=5).classes('w-full')
        except:
            pass

        sql5 = f'''
select
	d.case_id,
	pd.payed_debt_id,
    d.debt_id,
    pd.payment_id,
	pd.debt_amount_covered,
	pd.interest_amount_covered,
	pd.overpayment,
	pd.created_at::date	
from
	payed_debts pd,
	debts d
where
	pd.deleted_at is null and
	d.deleted_at is null and
	d.debt_id = pd.debt_id and
    d.case_id = :case_id
order by 
	pd.created_at desc
'''
        ui.label('Befizetések felosztásának részletei').style('color: #6E93D6; font-size: 300%; font-weight: 300')
        try:
            data_table5 = ui.table.from_pandas(pd.read_sql_query(text(sql5), params={'case_id':-1}, con=connection), row_key='case_id', pagination=5).classes('w-full')
        except:
            pass