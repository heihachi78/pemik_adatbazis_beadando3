from datetime import date
from sqlalchemy import create_engine, text
from nicegui import ui
from datetime import datetime
import pandas as pd
import theme
import config.database



def show_open_cases():
    with theme.frame('Nyitott ugyek karbantartása'):
        ui.page_title('Nyitott ugyek karbantartása')

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
		sum(d.interest_amount_covered) as sum_interest_payed
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
	c.due_date, 
	c.amount, 
	c.interest_rate * 100 as interest_rate, 
	c.current_due_date, 
	c.current_amount, 
	c.current_interest_amount, 
	c.current_interest_rate * 100 as current_interest_rate, 
	s.sum_payed,
	i.sum_interest_payed,
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
    c.closed_at is null   
order by 
	c.case_id desc''', con=connection)


        def update_row(case_id: int, current_interest_rate: float):
            connection.execute(text("update cases set current_interest_rate = :current_interest_rate/100, updated_at = now() where case_id = :case_id"), 
                               {"case_id": case_id, "current_interest_rate": current_interest_rate})
            connection.commit()
            ui.notify('A rekord módosítva lett.')
            return select_rows()


        #button functions
        def update_data():
            toggle_update_button()
            for row_data in data_table.selected:
                data_table.update_from_pandas(update_row(row_data["case_id"], updated_interest_rate.value))
            clear_updated_values()


        #button toggles
        def toggle_update_button():
            if updated_interest_rate.value and validate_interest_rate(updated_interest_rate.value) is None and data_table.selected:
                update_button.enable()
            else:
                update_button.disable()


        #validation functions
        def validate_interest_rate(value):
            if value and value < 0.1:
                return 'A kamat legkisebb erteke 0.001 lehet!'
            if value and value > 100:
                return 'A kamat legnagyobb erteke 100 lehet!'
            return None


        #visibility toggles
        def toggle_update_card_visibility():
            data_table.selected = []
            update_card.set_visibility(not(update_card.visible))
            if update_card.visible:
                data_table.set_selection('single')
            else:
                data_table.set_selection('none')
            clear_updated_values()
            toggle_update_button()


        #record selection handling
        def handle_selection():
            toggle_update_button()
            if data_table.selected:
                updated_interest_rate.set_value(data_table.selected[0]['current_interest_rate'])
            else:
                clear_updated_values()


        def clear_updated_values():
            updated_interest_rate.set_value(None)


        #table column definitions last_payment
        columns=[
                {'name': 'case_id', 'label': 'Ugy ID', 'field': 'case_id', 'sortable': True},
                {'name': 'partner_name', 'label': 'Partner', 'field': 'partner_name', 'sortable': True},
                {'name': 'batch_number', 'label': 'Batch', 'field': 'batch_number', 'sortable': True},
                {'name': 'partner_case_number', 'label': 'Partner ugy szama', 'field': 'partner_case_number', 'sortable': True},
                {'name': 'due_date', 'label': 'Eredeti hatarido', 'field': 'due_date', 'sortable': True},
                {'name': 'amount', 'label': 'Vasarlaskori tartozas', 'field': 'amount', 'sortable': True},
                {'name': 'interest_rate', 'label': 'Vasarlaskori kamat merteke', 'field': 'interest_rate', 'sortable': True},
                {'name': 'last_payment', 'label': 'Utolso befizetes', 'field': 'last_payment', 'sortable': True},
                {'name': 'current_due_date', 'label': 'Kamat szamitas napja', 'field': 'current_due_date', 'sortable': True},
                {'name': 'current_amount', 'label': 'Aktualis toke tartozas', 'field': 'current_amount', 'sortable': True},
                {'name': 'current_interest_amount', 'label': 'Aktualis kamat tartozas', 'field': 'current_interest_amount', 'sortable': True},
                {'name': 'current_interest_rate', 'label': 'Aktualis kamat merteke', 'field': 'current_interest_rate', 'sortable': True},
                {'name': 'sum_payed', 'label': 'Osszes befizetes', 'field': 'sum_payed', 'sortable': True},
                {'name': 'sum_interest_payed', 'label': 'Elszamolt kamat', 'field': 'sum_interest_payed', 'sortable': True},
                {'name': 'created_at', 'label': 'Létrehozás időpontja', 'field': 'created_at', 'sortable': True}
            ]


        #UI element definitions
        ui.label('Nyitott ugyek karbantartása').style('color: #6E93D6; font-size: 300%; font-weight: 300')

        with ui.row():
            update_card_button = ui.button('!', on_click=toggle_update_card_visibility).props('color=green')

        update_card = ui.card()
        with update_card:
            updated_interest_rate = ui.number(label= 'Uj kamat merteke', suffix='%', format="%.000f", min=0.1, max=100.0, on_change=toggle_update_button, validation=validate_interest_rate, precision=0.1).props('clearable').props('size=25')
            update_button = ui.button('Ugy modositasa', on_click=update_data).props('color=green')

        search_field = ui.input('Keresés', placeholder='írja be a keresendő ugy valamely adatát').props('clearable').props('size=100')
        data_table = ui.table.from_pandas(select_rows(), row_key='case_id', on_select=handle_selection, pagination=5, columns=columns).classes('w-full')
        search_field.bind_value(data_table, 'filter')

        #initial visibility settings
        toggle_update_button()
        update_card.set_visibility(False)

    #connection.close()
