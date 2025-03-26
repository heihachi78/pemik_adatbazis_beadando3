from datetime import date
from sqlalchemy import create_engine, text
from nicegui import ui, app
from datetime import datetime
import pandas as pd
import theme
import config.database



def show_debtors():
    with theme.frame('Adósok karbantartása'):
        ui.page_title('Adósok karbantartása')

        engine = create_engine(config.database.POOL_CONN_INFO)
        connection = engine.connect()


        #sector data for dropdown
        def get_debtor_types():
            qr = pd.read_sql_query('select t.debtor_type_id, t."name" debtor_type from debtor_types t where t.deleted_at is null', con=connection)
            ret = {}
            for i in range(len(qr)):
                ret[int(qr['debtor_type_id'][i])] = qr['debtor_type'][i]
            return ret

        def get_persons():
            qr = pd.read_sql_query('''select p.person_id, concat(p.first_name, ' ', p.last_name, ' (', p.birth_date, ')') as full_name from persons p where p.deleted_at is null and p.death_date is null''', con=connection)
            ret = {}
            for i in range(len(qr)):
                ret[int(qr['person_id'][i])] = qr['full_name'][i]
            return ret
        
        def has_payment(person_id: int):
            return connection.execute(text("select count(*) from payments where person_id = :person_id and case_id = :case_id and deleted_at is null"),  {"person_id": person_id, "case_id": app.storage.user['saved_data']["case_id"]}).fetchone()[0]


        #database functions
        def select_rows():
            return pd.read_sql_query('''
select
	t."name" as debtor_type,
	concat(p.first_name, ' ', p.last_name) as full_name,
	p.birth_date,
	c."name" as birth_city,
	p.birth_name,
	p.mother_name,
	p.death_date,
	d.created_at::date as created_at,
	d.debtor_id,
    t.debtor_type_id,
    d.case_id,
    d.person_id
from 
	debtors d, 
	persons p,
	cities c,
	debtor_types t
where 
	d.deleted_at is null and 
	d.person_id = p.person_id and 
	p.deleted_at is null and 
	c.deleted_at is null and
	c.city_id = p.birth_place_city_id and 
	t.debtor_type_id = d.debtor_type_id and 
	t.deleted_at is null
order by
    d.debtor_id desc
            ''', con=connection)


        def insert_row(person_id: int, case_id: int, debtor_type_id: int):
            connection.execute(text("insert into debtors (person_id, debtor_type_id, case_id) values (:person_id, :debtor_type_id, :case_id)"), 
                               {"person_id": person_id, "case_id": case_id, "debtor_type_id": debtor_type_id})
            connection.commit()
            ui.notify('Az új rekord felvétele sikeres volt.')
            return select_rows()


        def delete_row(debtor_id: int):
            connection.execute(text("update debtors d set deleted_at = now() where d.debtor_id = :debtor_id"), {"debtor_id": debtor_id})
            connection.commit()
            ui.notify('A rekord törölve lett.')
            return select_rows()


        def update_row(debtor_type_id: int, debtor_id: int):
            connection.execute(text("update debtors set debtor_type_id = :debtor_type_id, updated_at = now() where debtor_id = :debtor_id"), 
                               {"debtor_type_id": debtor_type_id, "debtor_id": debtor_id})
            connection.commit()
            ui.notify('A rekord módosítva lett.')
            return select_rows()


        #button functions
        def add_data():
            toggle_add_button()
            data_table.update_from_pandas(insert_row(new_person_id.value, app.storage.user['saved_data']["case_id"], new_debtor_type_id.value))
            clear_new_values()

        def delete_data():
            toggle_delete_button()
            for row_data in data_table.selected:
                delete_row(row_data["debtor_id"])
            data_table.update_from_pandas(select_rows())

        def update_data():
            toggle_update_button()
            for row_data in data_table.selected:
                data_table.update_from_pandas(update_row(updated_debtor_type_id.value, row_data["debtor_id"]))
            clear_updated_values()


        #button toggles
        def toggle_add_button():
            if new_debtor_type_id.value and \
                new_person_id.value in persons and \
                validate_type(new_debtor_type_id.value) is None and \
                validate_person(new_person_id.value) is None:
                add_button.enable()
            else:
                add_button.disable()


        def toggle_delete_button():
            if data_table.selected:
                delete_button.enable()
            else:
                delete_button.disable()


        def toggle_update_button():
            if updated_debtor_type_id.value and \
               data_table.selected:
               update_button.enable()
            else:
                update_button.disable()


        #validation functions
        def validate_person(value):
            for r in data_table.rows:
                if r['person_id'] == new_person_id.value:
                    return 'Ez a személy már szerepel az adósok között!'
            return None
        
        def validate_type(value):
            for r in data_table.rows:
                if r['debtor_type_id'] == new_debtor_type_id.value and new_debtor_type_id.value == 1:
                    return 'Ez a típus már szerepel az adósok között!'
            return None

        #visibility toggles
        def toggle_new_card_visibility():
            if app.storage.user['saved_data']["open"]:
                data_table.selected = []
                delete_card.set_visibility(False)
                update_card.set_visibility(False)
                new_card.set_visibility(not(new_card.visible))
                data_table.set_selection('none')
                clear_updated_values()
                clear_new_values()
                toggle_add_button()


        def toggle_delete_card_visibility():
            if app.storage.user['saved_data']["open"]:
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
            if app.storage.user['saved_data']["open"]:
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
                    if has_payment(sl['person_id']) > 0:
                        s.append(sl)
                for ss in s:
                    data_table.selected.remove(ss)
                data_table.update()
            toggle_delete_button()
            toggle_update_button()
            if data_table.selected:
                updated_debtor_type_id.set_value(data_table.selected[0]['debtor_type_id'])
            else:
                clear_updated_values()
                clear_new_values()

        def clear_updated_values():
            updated_debtor_type_id.set_value(None)

        def clear_new_values():
            new_person_id.set_value(None)
            new_debtor_type_id.set_value(None)

        def on_row_dblclick(e):
            app.storage.user['saved_data']["person_id"] = e.args[1]["person_id"]
            ui.navigate.to('/persons/', new_tab=False)


        #table column definitions
        columns=[
                {'name': 'debtor_id', 'label': 'Adós ID', 'field': 'debtor_id', 'sortable': True},
                {'name': 'case_id', 'label': 'Ügy ID', 'field': 'case_id', 'sortable': True},
                {'name': 'person_id', 'label': 'Személy ID', 'field': 'person_id', 'sortable': True, 'classes': 'hidden', 'headerClasses': 'hidden'},
                {'name': 'debtor_type_id', 'label': 'Adós típus ID', 'field': 'debtor_type_id', 'sortable': True, 'classes': 'hidden', 'headerClasses': 'hidden'},
                {'name': 'debtor_type', 'label': 'Adós típusa', 'field': 'debtor_type', 'sortable': True},
                {'name': 'full_name', 'label': 'Adós teljes neve', 'field': 'full_name', 'sortable': True},
                {'name': 'birth_date', 'label': 'Születési dátum', 'field': 'birth_date', 'sortable': True},
                {'name': 'birth_city', 'label': 'Születési hely', 'field': 'birth_city', 'sortable': True},
                {'name': 'mother_name', 'label': 'Anyja neve', 'field': 'mother_name', 'sortable': True},
                {'name': 'birth_name', 'label': 'Születési név', 'field': 'birth_name', 'sortable': True},
                {'name': 'death_date', 'label': 'Halál dátuma', 'field': 'death_date', 'sortable': True},
                {'name': 'created_at', 'label': 'Létrehozás időpontja', 'field': 'created_at', 'sortable': True}
            ]

        debtor_types = get_debtor_types()
        persons = get_persons()


        #UI element definitions
        ui.label('Adósok karbantartása').style('color: #6E93D6; font-size: 300%; font-weight: 300')

        with ui.row():
            new_card_button = ui.button('+', on_click=toggle_new_card_visibility).props('color=blue')
            delete_card_button = ui.button('-', on_click=toggle_delete_card_visibility).props('color=red')
            update_card_button = ui.button('!', on_click=toggle_update_card_visibility).props('color=green')

        new_card = ui.card()
        with new_card:
            new_debtor_type_id = ui.select(label= 'Adós típus választása', options=debtor_types, with_input=True, on_change=toggle_add_button, validation=validate_type).props('size=100')
            new_person_id = ui.select(label= 'Adós személyének választása', options=persons, with_input=True, on_change=toggle_add_button, validation=validate_person).props('size=100')
            add_button = ui.button('Új adós hozzáadása', on_click=add_data).props('color=blue')

        delete_card = ui.card()
        with delete_card:
            delete_button = ui.button('A kijelölt adós(ok) törlése', on_click=delete_data).props('color=red')

        update_card = ui.card()
        with update_card:
            updated_debtor_type_id = ui.select(label= 'Adós típus választása', options=debtor_types, with_input=True, on_change=toggle_update_button).props('size=100')
            update_button = ui.button('Adós módosítása', on_click=update_data).props('color=green')

        search_field = ui.input('Keresés', placeholder='írja be a keresendő adós valamely adatát').props('clearable').props('size=100')
        data_table = ui.table.from_pandas(select_rows(), row_key='debtor_id', on_select=handle_selection, pagination=5, columns=columns).classes('w-full').on('rowDblclick', on_row_dblclick)
        data_table.set_filter(str(app.storage.user['saved_data']["case_id"]))
        search_field.bind_value(data_table, 'filter')


        #initial visibility settings
        toggle_add_button()
        toggle_delete_button()
        toggle_update_button()
        new_card.set_visibility(False)
        delete_card.set_visibility(False)
        update_card.set_visibility(False)

    #connection.close()
