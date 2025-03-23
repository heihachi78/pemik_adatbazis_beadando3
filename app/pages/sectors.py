from sqlalchemy import create_engine, text
from nicegui import ui
import pandas as pd
import theme
import config.database



def show_sectors():
    with theme.frame('Szektorok karbantartása'):
        ui.page_title('Szektorok karbantartása')

        engine = create_engine(config.database.POOL_CONN_INFO)
        connection = engine.connect()

        #database functions
        def select_rows():
            return pd.read_sql_query('select sector_id, name, created_at::date from sectors where deleted_at is null order by sector_id desc', con=connection)


        def insert_row(sector_name: str):
            connection.execute(text("insert into sectors (name) values (:name)"), {"name": sector_name})
            connection.commit()
            ui.notify('Az új rekord felvétele sikeres volt.')
            return select_rows()


        def delete_row(sector_id: int):
            connection.execute(text("update sectors set deleted_at = now() where sector_id = :sector_id"), {"sector_id": sector_id})
            connection.commit()
            ui.notify('A rekord törölve lett.')
            return select_rows()


        def update_row(sector_id: int, name: str):
            connection.execute(text("update sectors set name = :name, updated_at = now() where sector_id = :sector_id"), {"sector_id": sector_id, "name": name})
            connection.commit()
            ui.notify('A rekord módosítva lett.')
            return select_rows()


        #button functions
        def add_data():
            if new_sector_name.value:
                data_table.update_from_pandas(insert_row(new_sector_name.value))
                new_sector_name.set_value(None)
                toggle_add_button()


        def delete_data():
            for row_data in data_table.selected:
                delete_row(row_data["sector_id"])
            data_table.update_from_pandas(select_rows())
            toggle_delete_button()


        def update_data():
            if update_sector_name.value and len(data_table.selected) == 1:
                for row_data in data_table.selected:
                    data_table.update_from_pandas(update_row(row_data["sector_id"], update_sector_name.value))
                update_sector_name.set_value(None)
                toggle_update_button()


        #button toggles
        def toggle_add_button():
            if new_sector_name.value and validate_name(new_sector_name.value) is None:
                add_button.enable()
            else:
                add_button.disable()


        def toggle_delete_button():
            if data_table.selected:
                delete_button.enable()
            else:
                delete_button.disable()


        def toggle_update_button():
            if update_sector_name.value and validate_name(update_sector_name.value) is None and data_table.selected:
                update_button.enable()
            else:
                update_button.disable()


        #validation functions
        def validate_name(value):
            if value and len(value) < 3:
                return 'A szektor nevének legalább 3 karakter hosszúnak kell lennie!'
            if value and len(value) > 100:
                return 'A szektor neve maximum 100 karakter hosszú lehet!'
            return None


        #visibility toggles
        def toggle_new_card_visibility():
            delete_card.set_visibility(False)
            update_card.set_visibility(False)
            new_card.set_visibility(not(new_card.visible))
            data_table.set_selection('none')
            data_table.selected = []
            update_sector_name.set_value(None)
            new_sector_name.set_value(None)
            toggle_add_button()


        def toggle_delete_card_visibility():
            new_card.set_visibility(False)
            update_card.set_visibility(False)
            delete_card.set_visibility(not(delete_card.visible))
            if delete_card.visible:
                data_table.set_selection('multiple')
            else:
                data_table.set_selection('none')
            data_table.selected = []
            update_sector_name.set_value(None)
            new_sector_name.set_value(None)
            toggle_delete_button()


        def toggle_update_card_visibility():
            delete_card.set_visibility(False)
            new_card.set_visibility(False)
            update_card.set_visibility(not(update_card.visible))
            if update_card.visible:
                data_table.set_selection('single')
            else:
                data_table.set_selection('none')
            data_table.selected = []
            update_sector_name.set_value(None)
            new_sector_name.set_value(None)
            toggle_update_button()


        #record selection handling
        def handle_selection():
            toggle_delete_button()
            toggle_update_button()
            if data_table.selected:
                update_sector_name.set_value(data_table.selected[0]['name'])
            else:
                update_sector_name.set_value(None)


        #table column definitions
        columns=[
                {'name': 'sector_id', 'label': 'Szektor ID', 'field': 'sector_id', 'sortable': True},
                {'name': 'name', 'label': 'Név', 'field': 'name', 'sortable': True},
                {'name': 'created_at', 'label': 'Létrehozás időpontja', 'field': 'created_at', 'sortable': True}
            ]


        #UI element definitions
        ui.label('Szektorok karbantartása').style('color: #6E93D6; font-size: 300%; font-weight: 300')

        with ui.row():
            new_card_button = ui.button('+', on_click=toggle_new_card_visibility).props('color=blue')
            delete_card_button = ui.button('-', on_click=toggle_delete_card_visibility).props('color=red')
            update_card_button = ui.button('!', on_click=toggle_update_card_visibility).props('color=green')

        new_card = ui.card()
        with new_card:
            new_sector_name = ui.input(label= 'Új szektor neve', placeholder='írja be az új szektor nevét', on_change=toggle_add_button, validation=validate_name).props('clearable').props('size=100')
            add_button = ui.button('Új szektor hozzáadása', on_click=add_data).props('color=blue')

        delete_card = ui.card()
        with delete_card:
            delete_button = ui.button('A kijelölt szektor(ok) törlése', on_click=delete_data).props('color=red')

        update_card = ui.card()
        with update_card:
            update_sector_name = ui.input(label= 'Szektor neve', on_change=toggle_update_button, validation=validate_name).props('clearable').props('size=100')
            update_button = ui.button('A kijelölt szektor módosítása', on_click=update_data).props('color=green')

        search_field = ui.input('Keresés', placeholder='írja be a keresendő szektor valamely adatát').props('clearable').props('size=100')
        data_table = ui.table.from_pandas(select_rows(), row_key='sector_id', on_select=handle_selection, pagination=5, columns=columns).classes('w-full')
        search_field.bind_value(data_table, 'filter')


        #initial visibility settings
        toggle_add_button()
        toggle_delete_button()
        toggle_update_button()
        new_card.set_visibility(False)
        delete_card.set_visibility(False)
        update_card.set_visibility(False)

    #connection.close()
