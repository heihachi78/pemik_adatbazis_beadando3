from datetime import date
from sqlalchemy import create_engine, text
from nicegui import ui, app
from datetime import datetime
import pandas as pd
import theme
import config.database



def show_closed_cases():
    with theme.frame('Zárt ügyek'):
        ui.page_title('Zárt ügyek')

        engine = create_engine(config.database.POOL_CONN_INFO)
        connection = engine.connect()

        #database functions
        def select_rows():
            return pd.read_sql_query('''with pay_sum as (
	select 
		x.case_id,
		sum(x.amount) as sum_payed,
		max(x.payment_date) as last_payment
	from 
		payments x
	where 
		x.deleted_at is null
	group by
		x.case_id
), int_sum as (
	select 
		t.case_id,
		sum(d.interest_amount_covered) as sum_interest_payed,
		sum(d.overpayment) as sum_overpayment
	from 
		payed_debts d, 
		debts t 
	where 
		t.debt_id = d.debt_id and 
		t.deleted_at is null and 
		t.deleted_at is null
	group by
		t.case_id	
)
select 
	c.case_id, 
	t."name" as partner_name, 
	p.batch_number, 
	c.partner_case_number, 
	c.closed_at::date, 
	c.due_date, 
	c.amount, 
	c.interest_rate * 100 as interest_rate, 
	s.sum_payed,
	i.sum_interest_payed,
	i.sum_overpayment,
	s.last_payment::date,
	c.created_at::date
from 
	cases c 
	left join pay_sum s on s.case_id = c.case_id
	left join int_sum i on i.case_id = c.case_id,
	purchases p, 
	partners t
where 
	c.deleted_at is null and 
	c.purchase_id = p.purchase_id and 
	p.deleted_at is null and 
	t.partner_id = p.partner_id and 
	t.deleted_at is null and
    c.closed_at is not null 
order by 
	c.case_id desc''', con=connection)

        #button functions

        #button toggles

        #validation functions

        #visibility toggles

        #record selection handling
        def on_row_dblclick(e):
            app.storage.user['saved_data']["case_id"] = e.args[1]["case_id"]
            app.storage.user['saved_data']["open"] = False
            ui.navigate.to('/debtors/', new_tab=False)

        #table column definitions last_payment
        columns=[
                {'name': 'case_id', 'label': 'Ügy ID', 'field': 'case_id', 'sortable': True},
                {'name': 'partner_name', 'label': 'Partner', 'field': 'partner_name', 'sortable': True},
                {'name': 'batch_number', 'label': 'Batch', 'field': 'batch_number', 'sortable': True},
                {'name': 'partner_case_number', 'label': 'Partner ügy száma', 'field': 'partner_case_number', 'sortable': True},
                {'name': 'closed_at', 'label': 'Lezárás dátuma', 'field': 'closed_at', 'sortable': True},
                {'name': 'due_date', 'label': 'Eredeti határidő', 'field': 'due_date', 'sortable': True},
                {'name': 'amount', 'label': 'Vásárláskori tartozás', 'field': 'amount', 'sortable': True},
                {'name': 'interest_rate', 'label': 'Vásárlaskori kamat mértéke', 'field': 'interest_rate', 'sortable': True},
                {'name': 'last_payment', 'label': 'Utolsó befizetés', 'field': 'last_payment', 'sortable': True},
                {'name': 'sum_payed', 'label': 'Összes befizetés', 'field': 'sum_payed', 'sortable': True},
                {'name': 'sum_interest_payed', 'label': 'Elszámolt kamat', 'field': 'sum_interest_payed', 'sortable': True},
                {'name': 'sum_overpayment', 'label': 'Túlfizetes', 'field': 'sum_overpayment', 'sortable': True},
                {'name': 'created_at', 'label': 'Létrehozás időpontja', 'field': 'created_at', 'sortable': True}
            ]


        #UI element definitions
        ui.label('Zárt ügyek').style('color: #6E93D6; font-size: 300%; font-weight: 300')

        search_field = ui.input('Keresés', placeholder='írja be a keresendő ügy valamely adatát').props('clearable').props('size=100')
        data_table = ui.table.from_pandas(select_rows(), row_key='case_id', pagination=5, columns=columns).classes('w-full').on('rowDblclick', on_row_dblclick)
        search_field.bind_value(data_table, 'filter')

        #initial visibility settings

    #connection.close()
