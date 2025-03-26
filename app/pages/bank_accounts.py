from datetime import date
from sqlalchemy import create_engine, text
from nicegui import ui, app
from datetime import datetime
import pandas as pd
import theme
import config.database



def show_persons():
    with theme.frame('Személyek karbantartása'):
        ui.page_title('Személyek karbantartása')

        engine = create_engine(config.database.POOL_CONN_INFO)
        connection = engine.connect()


        #partner data for dropdown
        def get_cities():
            qr = pd.read_sql_query('select c.city_id, c."name" as city_name from cities c where c.deleted_at is null order by c."name"', con=connection)
            ret = {}
            for i in range(len(qr)):
                ret[int(qr['city_id'][i])] = qr['city_name'][i]
            return ret

        def get_genders():
            qr = pd.read_sql_query('select c.gender_id, c."name" as gender_name from genders c where c.deleted_at is null order by c."name"', con=connection)
            ret = {}
            for i in range(len(qr)):
                ret[int(qr['gender_id'][i])] = qr['gender_name'][i]
            return ret
        
        def has_payment(person_id: int):
            return connection.execute(text("select count(*) from payments where person_id = :person_id and deleted_at is null"),  {"person_id": person_id}).fetchone()[0]

        #database functions
        def select_rows():
            return pd.read_sql_query('''
SELECT 
	p.person_id, 
	p.first_name, 
	p.last_name, 
	p.birth_place_city_id,
	c."name" as city_name,
	p.birth_date, 
	p.birth_name, 
	p.mother_name, 
	p.death_date, 
	p.gender_id,
	g."name" as gender_name,
	p.created_at::date
FROM 
	public.persons p,
	cities c,
	genders g
WHERE
	p.deleted_at is null and
	c.city_id = p.birth_place_city_id and 
	c.deleted_at is null and
	g.gender_id = p.gender_id and 
	g.deleted_at is null
ORDER BY
    p.person_id DESC
''', con=connection)


        def insert_row(first_name: str, 
                       last_name: str, 
                       birth_name: str, 
                       mother_name: str, 
                       birth_date: date,
                       death_date: date,
                       gender_id: int,
                       city_id: int):
            connection.execute(text("insert into persons (first_name, \
                                    last_name, \
                                    birth_name, \
                                    mother_name, \
                                    birth_date, \
                                    death_date, \
                                    gender_id, \
                                    birth_place_city_id \
                                    ) values ( \
                                    :first_name, \
                                    :last_name, \
                                    :birth_name, \
                                    :mother_name, \
                                    :birth_date, \
                                    :death_date, \
                                    :gender_id, \
                                    :city_id)"), 
                               {"first_name": first_name, 
                                "last_name": last_name, 
                                "birth_name": birth_name, 
                                "mother_name": mother_name, 
                                "birth_date": birth_date,
                                "death_date": death_date,
                                "gender_id": gender_id,
                                "city_id": city_id})
            connection.commit()
            ui.notify('Az új rekord felvétele sikeres volt.')
            return select_rows()


        def delete_row(person_id: int):
            connection.execute(text("update persons set deleted_at = now() where person_id = :person_id"), {"person_id": person_id})
            connection.commit()
            ui.notify('A rekord törölve lett.')
            return select_rows()


        def update_row(person_id: int, 
                       first_name: str, 
                       last_name: str, 
                       birth_name: str, 
                       mother_name: str,
                       birth_date: date,
                       death_date: date,
                       gender_id: int,
                       city_id: int):
            connection.execute(text("update persons set \
                                    first_name = :first_name, \
                                    last_name = :last_name, \
                                    birth_name = :birth_name, \
                                    mother_name = :mother_name, \
                                    birth_date = :birth_date, \
                                    death_date = :death_date, \
                                    gender_id = :gender_id, \
                                    birth_place_city_id = :city_id, \
                                    updated_at = now() \
                                    where person_id = :person_id"), 
                               {"person_id": person_id, 
                                "first_name": first_name, 
                                "last_name": last_name,
                                "birth_name": birth_name,
                                "mother_name": mother_name,
                                "birth_date": birth_date,
                                "death_date": death_date,
                                "gender_id": gender_id,
                                "city_id": city_id})
            connection.commit()
            ui.notify('A rekord módosítva lett.')
            return select_rows()


        #button functions
        def add_data():
            toggle_add_button()
            data_table.update_from_pandas(insert_row(new_first_name.value, 
                                                     new_last_name.value, 
                                                     new_birth_name.value, 
                                                     new_mothers_name.value,
                                                     new_birth_date.value,
                                                     new_death_date.value,
                                                     new_gender_id.value,
                                                     new_city_id.value))
            clear_new_values()

        def delete_data():
            toggle_delete_button()
            for row_data in data_table.selected:
                delete_row(row_data["person_id"])
            data_table.update_from_pandas(select_rows())

        def update_data():
            toggle_update_button()
            for row_data in data_table.selected:
                data_table.update_from_pandas(update_row(row_data["person_id"], 
                                                         updated_first_name.value, 
                                                         updated_last_name.value, 
                                                         updated_birth_name.value,
                                                         updated_mothers_name.value,
                                                         updated_birth_date.value,
                                                         updated_death_date.value,
                                                         updated_gender_id.value,
                                                         updated_city_id.value))
            clear_updated_values()


        #button toggles
        def toggle_add_button():
            if new_first_name.value and validate_first_name(new_first_name.value) is None and \
                new_last_name.value and validate_last_name(new_last_name.value) is None and \
                new_mothers_name.value and validate_mothers_name(new_mothers_name.value) is None and \
                new_birth_date.value and (not(new_death_date.value) or new_death_date.value > new_birth_date.value) and \
                new_gender_id.value and \
                new_city_id.value and new_city_id.value in city_list.keys():
                add_button.enable()
            else:
                add_button.disable()


        def toggle_delete_button():
            if data_table.selected:
                delete_button.enable()
            else:
                delete_button.disable()


        def toggle_update_button():
            if updated_first_name.value and validate_first_name(updated_first_name.value) is None and \
                updated_last_name.value and validate_last_name(updated_last_name.value) is None and \
                updated_mothers_name.value and validate_mothers_name(updated_mothers_name.value) is None and \
                updated_birth_date.value and (not(updated_death_date.value) or updated_death_date.value > updated_birth_date.value) and \
                updated_gender_id.value and \
                updated_city_id.value and updated_city_id.value in city_list.keys() and \
                data_table.selected:
                update_button.enable()
            else:
                update_button.disable()


        #validation functions
        def validate_first_name(value):
            if value is None:
                return 'Nem lehet üres a vezetéknév!'
            if value and len(value) < 2:
                return 'A vezetéknév legalább 2 karakter kell legyen!'
            if value and len(value) > 100:
                return 'A vezetéknév maximum 100 karakter hosszú lehet!'
            return None

        def validate_last_name(value):
            if value is None:
                return 'Nem lehet üres a keresztnév!'
            if value and len(value) < 2:
                return 'A keresztnév legalább 2 karakter kell legyen!'
            if value and len(value) > 100:
                return 'A keresztnév maximum 100 karakter hosszú lehet!'
            return None
        
        def validate_mothers_name(value):
            if value is None:
                return 'Nem lehet üres az anyja neve!'
            if value and len(value) < 2:
                return 'Az anyja neve legalább 2 karakter kell legyen!'
            if value and len(value) > 100:
                return 'Az anyja neve maximum 100 karakter hosszú lehet!'
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
                for sl in data_table.selected:
                    if has_payment(sl['person_id']) > 0:
                        data_table.selected.remove(sl)
                data_table.update()
            toggle_delete_button()
            toggle_update_button()
            if data_table.selected:
                updated_first_name.set_value(data_table.selected[0]['first_name'])
                updated_last_name.set_value(data_table.selected[0]['last_name'])
                updated_birth_name.set_value(data_table.selected[0]['birth_name'])
                updated_mothers_name.set_value(data_table.selected[0]['mother_name'])
                updated_birth_date.set_value(data_table.selected[0]['birth_date'])
                updated_death_date.set_value(data_table.selected[0]['death_date'])
                updated_gender_id.set_value(data_table.selected[0]['gender_id'])
                updated_city_id.set_value(data_table.selected[0]['birth_place_city_id'])
            else:
                clear_updated_values()
                clear_new_values()

        def clear_updated_values():
            updated_first_name.set_value(None)
            updated_last_name.set_value(None)
            updated_birth_name.set_value(None)
            updated_mothers_name.set_value(None)
            updated_birth_date.set_value(None)
            updated_death_date.set_value(None)
            updated_gender_id.set_value(None)
            updated_city_id.set_value(None)
            
        def clear_new_values():
            new_first_name.set_value(None)
            new_last_name.set_value(None)
            new_birth_name.set_value(None)
            new_mothers_name.set_value(None)
            new_birth_date.set_value(None)
            new_death_date.set_value(None)
            new_gender_id.set_value(None)
            new_city_id.set_value(None)
            

        #table column definitions
        columns=[
                {'name': 'person_id', 'label': 'Személy ID', 'field': 'person_id', 'sortable': True},
                {'name': 'first_name', 'label': 'Vezetéknév', 'field': 'first_name', 'sortable': True},
                {'name': 'last_name', 'label': 'Keresztnév', 'field': 'last_name', 'sortable': True},
                {'name': 'birth_place_city_id', 'label': 'City ID', 'field': 'birth_place_city_id', 'sortable': True, 'classes': 'hidden', 'headerClasses': 'hidden'},
                {'name': 'city_name', 'label': 'Születési hely', 'field': 'city_name', 'sortable': True},
                {'name': 'birth_date', 'label': 'Születési dátum', 'field': 'birth_date', 'sortable': True},
                {'name': 'mother_name', 'label': 'Anyja neve', 'field': 'mother_name', 'sortable': True},
                {'name': 'death_date', 'label': 'Halál dátuma', 'field': 'death_date', 'sortable': True},
                {'name': 'gender_id', 'label': 'Gender ID', 'field': 'gender_id', 'sortable': True, 'classes': 'hidden', 'headerClasses': 'hidden'},
                {'name': 'gender_name', 'label': 'Neme', 'field': 'gender_name', 'sortable': True},
                {'name': 'created_at', 'label': 'Létrehozás időpontja', 'field': 'created_at', 'sortable': True}
            ]

        city_list = get_cities()
        gender_list = get_genders()


        #UI element definitions
        ui.label('Személyek karbantartása').style('color: #6E93D6; font-size: 300%; font-weight: 300')

        with ui.row():
            new_card_button = ui.button('+', on_click=toggle_new_card_visibility).props('color=blue')
            delete_card_button = ui.button('-', on_click=toggle_delete_card_visibility).props('color=red')
            update_card_button = ui.button('!', on_click=toggle_update_card_visibility).props('color=green')

        new_card = ui.card()
        with new_card:
            new_first_name = ui.input(label= 'Vezetéknév', placeholder='írja be az új személy vezetéknevét', on_change=toggle_add_button, validation=validate_first_name).props('clearable').props('size=100')
            new_last_name = ui.input(label= 'Keresztnév', placeholder='írja be az új személy keresztnevét', on_change=toggle_add_button, validation=validate_last_name).props('clearable').props('size=100')
            new_birth_name = ui.input(label= 'Születési név', placeholder='írja be az új személy születési nevét', on_change=toggle_add_button).props('clearable').props('size=100')
            new_mothers_name = ui.input(label= 'Anyja neve', placeholder='írja be az új személy anyja nevét', on_change=toggle_add_button, validation=validate_mothers_name).props('clearable').props('size=100')
            new_gender_id = ui.select(label= 'Nem választása', options=gender_list, with_input=True, on_change=toggle_add_button).props('size=100')
            with ui.row():
                with ui.input('Születés dátuma', on_change=toggle_add_button).props('size=15') as new_birth_date:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(new_birth_date):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with new_birth_date.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                new_city_id = ui.select(label= 'Születési hely választása', options=city_list, with_input=True, on_change=toggle_add_button).props('size=50')
                with ui.input('Halál dátuma', on_change=toggle_add_button).props('size=15') as new_death_date:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(new_death_date):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with new_death_date.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            add_button = ui.button('Új személy hozzáadása', on_click=add_data).props('color=blue')

        delete_card = ui.card()
        with delete_card:
            delete_button = ui.button('A kijelölt személy(ek) törlése', on_click=delete_data).props('color=red')

        update_card = ui.card()
        with update_card:
            updated_first_name = ui.input(label= 'Vezetéknév', placeholder='írja be a személy vezetéknevét', on_change=toggle_update_button, validation=validate_first_name).props('clearable').props('size=100')
            updated_last_name = ui.input(label= 'Keresztnév', placeholder='írja be a személy keresztnevét', on_change=toggle_update_button, validation=validate_last_name).props('clearable').props('size=100')
            updated_birth_name = ui.input(label= 'Születési név', placeholder='írja be a személy születési nevét', on_change=toggle_update_button).props('clearable').props('size=100')
            updated_mothers_name = ui.input(label= 'Anyja neve', placeholder='írja be a személy anyja nevét', on_change=toggle_update_button, validation=validate_mothers_name).props('clearable').props('size=100')
            updated_gender_id = ui.select(label= 'Nem választása', options=gender_list, with_input=True, on_change=toggle_update_button).props('size=100')
            with ui.row():
                with ui.input('Születés dátuma', on_change=toggle_update_button).props('size=15') as updated_birth_date:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(updated_birth_date):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with updated_birth_date.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                updated_city_id = ui.select(label= 'Születési hely választása', options=city_list, with_input=True, on_change=toggle_update_button).props('size=50')
                with ui.input('Halál dátuma', on_change=toggle_update_button).props('size=15') as updated_death_date:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(updated_death_date):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with updated_death_date.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            update_button = ui.button('Személy módositása', on_click=update_data).props('color=green')

        search_field = ui.input(label='Keresés', placeholder='írja be a keresendő személy valamely adatát').props('clearable').props('size=100')
        data_table = ui.table.from_pandas(select_rows(), row_key='person_id', on_select=handle_selection, pagination=5, columns=columns).classes('w-full')
        data_table.set_filter(str(app.storage.user['saved_data']["person_id"]))
        search_field.bind_value(data_table, 'filter')

        #initial visibility settings
        toggle_add_button()
        toggle_delete_button()
        toggle_update_button()
        new_card.set_visibility(False)
        delete_card.set_visibility(False)
        update_card.set_visibility(False)

    #connection.close()
