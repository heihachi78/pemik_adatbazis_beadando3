from datetime import date
from sqlalchemy import create_engine, text
from nicegui import ui, app
from datetime import datetime
import pandas as pd
import theme
import config.database



def show_bank_accounts():
    with theme.frame('Számlatulajok karbantartása'):
        ui.page_title('Számlatulajok karbantartása')

        engine = create_engine(config.database.POOL_CONN_INFO)
        connection = engine.connect()


        #partner data for dropdown
        def get_accounts():
            qr = pd.read_sql_query('select c.bank_account_id, c.account_number from bank_accounts c where c.deleted_at is null order by c.account_number', con=connection)
            ret = {}
            for i in range(len(qr)):
                ret[int(qr['bank_account_id'][i])] = qr['account_number'][i]
            return ret

        def get_persons():
            qr = pd.read_sql_query('''select p.person_id, concat(p.first_name, ' ', p.last_name, ' (', p.birth_date, ')') as full_name from persons p where p.deleted_at is null and p.death_date is null''', con=connection)
            ret = {}
            for i in range(len(qr)):
                ret[int(qr['person_id'][i])] = qr['full_name'][i]
            return ret
        
        def has_payment(person_id: int, bank_account_id: int):
            return connection.execute(text("select count(*) from payments where person_id = :person_id and bank_account_id = :bank_account_id and deleted_at is null"),  {"person_id": person_id, "bank_account_id": bank_account_id}).fetchone()[0]

        #database functions
        def select_rows():
            return pd.read_sql_query('''
select 
	a.account_holder_id, 
	p.person_id,
	b.bank_account_id,
	concat(p.first_name, ' ', p.last_name, ' (', p.birth_date, ')') as owner_name, 
	b.account_number,
	a.valid_from, 
	a.valid_to
from 
	account_holders a, 
	persons p, 
	bank_accounts b
where 
	a.deleted_at is null and 
	p.deleted_at is null and 
	p.person_id = a.person_id and 
	b.bank_account_id = a.bank_account_id
order by
    a.account_holder_id desc
''', con=connection)


        def insert_row(from_date: date,
                       to_date: date,
                       person_id: int,
                       account_id: int):
            connection.execute(text("INSERT INTO public.account_holders( \
                                person_id, \
                                bank_account_id, \
                                valid_from, \
                                valid_to, \
                                created_at) \
                                VALUES ( \
                                :person_id, \
                                :bank_account_id, \
                                :valid_from, \
                                :valid_to, \
                                now())"),
                               {"person_id": person_id, 
                                "bank_account_id": account_id, 
                                "valid_from": from_date, 
                                "valid_to": to_date})
            connection.commit()
            ui.notify('Az új rekord felvétele sikeres volt.')
            return select_rows()


        def delete_row(account_holder_id: int):
            connection.execute(text("update account_holders set deleted_at = now() where account_holder_id = :account_holder_id"), {"account_holder_id": account_holder_id})
            connection.commit()
            ui.notify('A rekord törölve lett.')
            return select_rows()


        def update_row(account_holder_id: int, 
                       from_date: date,
                       to_date: date,
                       person_id: int,
                       account_id: int):
            connection.execute(text("update account_holders set \
                                    valid_from = :from_date, \
                                    valid_to = :to_date, \
                                    person_id = :person_id, \
                                    bank_account_id = :account_id, \
                                    updated_at = now() \
                                    where account_holder_id = :account_holder_id"), 
                               {"account_holder_id": account_holder_id, 
                                "from_date": from_date, 
                                "to_date": to_date,
                                "person_id": person_id,
                                "account_id": account_id})
            connection.commit()
            ui.notify('A rekord módosítva lett.')
            return select_rows()


        #button functions
        def add_data():
            toggle_add_button()
            data_table.update_from_pandas(insert_row(new_from.value,
                                                     new_to.value,
                                                     new_person_id.value,
                                                     new_account_id.value))
            clear_new_values()

        def delete_data():
            toggle_delete_button()
            for row_data in data_table.selected:
                delete_row(row_data["account_holder_id"])
            data_table.update_from_pandas(select_rows())

        def update_data():
            toggle_update_button()
            for row_data in data_table.selected:
                data_table.update_from_pandas(update_row(row_data["account_holder_id"], 
                                                         updated_from.value,
                                                         updated_to.value,
                                                         updated_person_id.value,
                                                         updated_account_id.value,))
            clear_updated_values()


        #button toggles
        def toggle_add_button():
            if new_person_id.value and new_person_id.value in person_list.keys() and \
                new_account_id.value and new_account_id.value in account_list.keys() and \
                new_from.value and (not new_to.value or (new_to.value > new_from.value)):
                add_button.enable()
            else:
                add_button.disable()


        def toggle_delete_button():
            if data_table.selected:
                delete_button.enable()
            else:
                delete_button.disable()


        def toggle_update_button():
            if updated_person_id.value and updated_person_id.value in person_list.keys() and \
                updated_account_id.value and updated_account_id.value in account_list.keys() and \
                updated_from.value and (not updated_to.value or (updated_to.value > updated_from.value)) and \
                data_table.selected:
                update_button.enable()
            else:
                update_button.disable()


        #validation functions
        def validate_person(value):
            if not value:
                return 'A személy kiválasztása kötelező!'
            if not (value in person_list.keys()):
                return 'A személy érvénytelen!'
            return None

        def validate_accounts(value):
            if not value:
                return 'A számla kiválasztása kötelező!'
            if not (value in person_list.keys()):
                return 'A számla érvénytelen!'
            return None
        
        def validate_new_date(value):
            if not new_from.value:
                return 'Az érvényesség kezdete kötelező!'
            if new_to.value and new_to.value <= new_from.value:
                return 'Az érvényesség vége nem lehet korábbi mint az érvényesség kezdete!'
            return None              

        def validate_updated_date(value):
            if not updated_from.value:
                return 'Az érvényesség kezdete kötelező!'
            if updated_to.value and updated_to.value <= updated_from.value:
                return 'Az érvényesség vége nem lehet korábbi mint az érvényesség kezdete!'
            return None

        def validate_new_date2(value):
            if new_to.value and new_to.value <= new_from.value:
                return 'Az érvényesség vége nem lehet korábbi mint az érvényesség kezdete!'
            return None              

        def validate_updated_date2(value):
            if updated_to.value and updated_to.value <= updated_from.value:
                return 'Az érvényesség vége nem lehet korábbi mint az érvényesség kezdete!'
            return None


        #visibility toggles
        def toggle_new_card_visibility():
            data_table.selected = []
            delete_card.set_visibility(False)
            update_card.set_visibility(False)
            new_card.set_visibility(not(new_card.visible))
            data_table.set_selection('none')
            clear_updated_values()
            clear_new_values()
            toggle_add_button()


        def toggle_delete_card_visibility():
            data_table.selected = []
            new_card.set_visibility(False)
            update_card.set_visibility(False)
            delete_card.set_visibility(not(delete_card.visible))
            if delete_card.visible:
                data_table.set_selection('multiple')
            else:
                data_table.set_selection('none')
            clear_updated_values()
            clear_new_values()
            toggle_delete_button()


        def toggle_update_card_visibility():
            data_table.selected = []
            delete_card.set_visibility(False)
            new_card.set_visibility(False)
            update_card.set_visibility(not(update_card.visible))
            if update_card.visible:
                data_table.set_selection('single')
            else:
                data_table.set_selection('none')
            clear_updated_values()
            clear_new_values()
            toggle_update_button()


        #record selection handling
        def handle_selection():
            if delete_card.visible and data_table.selected:
                s = []
                for sl in data_table.selected:
                    if has_payment(sl['person_id'], sl['bank_account_id']) > 0:
                        s.append(sl)
                for ss in s:
                    data_table.selected.remove(ss)
                data_table.update()
            toggle_delete_button()
            toggle_update_button()
            if data_table.selected:
                updated_from.set_value(data_table.selected[0]['valid_from'])
                updated_to.set_value(data_table.selected[0]['valid_to'])
                updated_person_id.set_value(data_table.selected[0]['person_id'])
                updated_account_id.set_value(data_table.selected[0]['bank_account_id'])
            else:
                clear_updated_values()
                clear_new_values()

        def clear_updated_values():
            updated_from.set_value(None)
            updated_to.set_value(None)
            updated_person_id.set_value(None)
            updated_account_id.set_value(None)
            
        def clear_new_values():
            new_from.set_value(None)
            new_to.set_value(None)
            new_person_id.set_value(None)
            new_account_id.set_value(None)

        def on_row_dblclick(e):
            app.storage.user['saved_data']["account"] = e.args[1]["account_number"]
            ui.navigate.to('/accounts/', new_tab=False)
            

        #table column definitions
        columns=[
                {'name': 'account_holder_id', 'label': 'Bankszámla összerendelés ID', 'field': 'account_holder_id', 'sortable': True},
                {'name': 'person_id', 'label': 'Person ID', 'field': 'person_id', 'sortable': True, 'classes': 'hidden', 'headerClasses': 'hidden'},
                {'name': 'bank_account_id', 'label': 'BA ID', 'field': 'bank_account_id', 'sortable': True, 'classes': 'hidden', 'headerClasses': 'hidden'},
                {'name': 'owner_name', 'label': 'Tulajdonos', 'field': 'owner_name', 'sortable': True},
                {'name': 'account_number', 'label': 'Bankszámlaszám', 'field': 'account_number', 'sortable': True},
                {'name': 'valid_from', 'label': 'Érvényes (tól)', 'field': 'valid_from', 'sortable': True},
                {'name': 'valid_to', 'label': 'Érvényes (ig)', 'field': 'valid_to', 'sortable': True}
            ]

        person_list = get_persons()
        account_list = get_accounts()


        #UI element definitions
        ui.label('Számlatulajok karbantartása').style('color: #6E93D6; font-size: 300%; font-weight: 300')

        with ui.row():
            new_card_button = ui.button('+', on_click=toggle_new_card_visibility).props('color=blue')
            delete_card_button = ui.button('-', on_click=toggle_delete_card_visibility).props('color=red')
            update_card_button = ui.button('!', on_click=toggle_update_card_visibility).props('color=green')

        new_card = ui.card()
        with new_card:
            new_person_id = ui.select(label= 'Személy választása', options=person_list, with_input=True, on_change=toggle_add_button, validation=validate_person).props('size=100')
            new_account_id = ui.select(label= 'Bankszámlaszám választása', options=account_list, with_input=True, on_change=toggle_add_button, validation=validate_person).props('size=100')
            with ui.row():
                with ui.input('Érvényes (tól)', on_change=toggle_add_button, validation=validate_new_date).props('size=15') as new_from:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(new_from):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with new_from.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                with ui.input('Érvényes (ig)', on_change=toggle_add_button, validation=validate_new_date2).props('size=15').props('clearable') as new_to:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(new_to):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with new_to.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            add_button = ui.button('Új összerendelés hozzáadása', on_click=add_data).props('color=blue')

        delete_card = ui.card()
        with delete_card:
            delete_button = ui.button('A kijelölt összerendelés(ek) törlése', on_click=delete_data).props('color=red')

        update_card = ui.card()
        with update_card:
            updated_person_id = ui.select(label= 'Személy választása', options=person_list, with_input=True, on_change=toggle_update_button, validation=validate_person).props('size=100')
            updated_account_id = ui.select(label= 'Bankszámlaszám választása', options=account_list, with_input=True, on_change=toggle_update_button, validation=validate_accounts).props('size=100')
            with ui.row():
                with ui.input('Érvényes (tól)', on_change=toggle_update_button, validation=validate_updated_date).props('size=15') as updated_from:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(updated_from):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with updated_from.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                with ui.input('Érvényes (ig)', on_change=toggle_update_button, validation=validate_updated_date2).props('size=15').props('clearable') as updated_to:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(updated_to):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with updated_to.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            update_button = ui.button('Összerendelés módositása', on_click=update_data).props('color=green')

        search_field = ui.input(label='Keresés', placeholder='írja be a keresendő összerendelés valamely adatát').props('clearable').props('size=100')
        data_table = ui.table.from_pandas(select_rows(), row_key='account_holder_id', on_select=handle_selection, pagination=5, columns=columns).classes('w-full').on('rowDblclick', on_row_dblclick)
        if app.storage.user['saved_data']["person_name"] and app.storage.user['saved_data']["person_name"] != '':
            data_table.set_filter(str(app.storage.user['saved_data']["person_name"]))
        else:
            data_table.set_filter(str(app.storage.user['saved_data']["bank_account"]))
        search_field.bind_value(data_table, 'filter')

        #initial visibility settings
        toggle_add_button()
        toggle_delete_button()
        toggle_update_button()
        new_card.set_visibility(False)
        delete_card.set_visibility(False)
        update_card.set_visibility(False)

    #connection.close()
