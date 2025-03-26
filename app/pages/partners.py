from sqlalchemy import create_engine, text
from nicegui import ui, app
import pandas as pd
import theme
import config.database


def show_partners():
    with theme.frame('Partnerek karbantartása'):
        ui.page_title('Partnerek karbantartása')

        engine = create_engine(config.database.POOL_CONN_INFO)
        connection = engine.connect()


        #sector data for dropdown
        def get_sectors():
            qr = pd.read_sql_query('SELECT sector_id, name FROM sectors WHERE deleted_at is null ORDER BY name', con=connection)
            ret = {}
            for i in range(len(qr)):
                ret[int(qr['sector_id'][i])] = qr['name'][i]
            return ret


        #database functions
        def select_rows():
            return pd.read_sql_query('SELECT p.partner_id, p.name, p.sector_id, s.name as sector_name, p.created_at::date FROM partners p, sectors s WHERE p.sector_id = s.sector_id and p.deleted_at is null ORDER BY p.partner_id desc', con=connection)


        def insert_row(partner_name: str, sector_id: int):
            connection.execute(text("insert into partners (name, sector_id) values (:name, :sector_id)"), {"name": partner_name, "sector_id": sector_id})
            connection.commit()
            ui.notify('Az új rekord felvétele sikeres volt.')
            return select_rows()


        def delete_row(partner_id: int):
            connection.execute(text("update partners set deleted_at = now() where partner_id = :partner_id"), {"partner_id": partner_id})
            connection.commit()
            ui.notify('A rekord törölve lett.')
            return select_rows()


        def update_row(partner_id: int, name: str, sector_id: int):
            connection.execute(text("update partners set name = :name, sector_id = :sector_id, updated_at = now() where partner_id = :partner_id"), {"partner_id": partner_id, "name": name, "sector_id": sector_id})
            connection.commit()
            ui.notify('A rekord módosítva lett.')
            return select_rows()


        #button functions
        def add_data():
            if new_partner_name.value and new_partner_sector_id.value and new_partner_sector_id.value in sector_list.keys():
                data_table.update_from_pandas(insert_row(new_partner_name.value, new_partner_sector_id.value))
                new_partner_name.set_value(None)
                new_partner_sector_id.set_value(None)
                toggle_add_button()


        def delete_data():
            for row_data in data_table.selected:
                delete_row(row_data["partner_id"])
            data_table.update_from_pandas(select_rows())
            toggle_delete_button()


        def update_data():
            if update_partner_name.value and len(data_table.selected) == 1 and update_partner_sector_id.value and update_partner_sector_id.value in sector_list.keys():
                for row_data in data_table.selected:
                    data_table.update_from_pandas(update_row(row_data["partner_id"], update_partner_name.value, update_partner_sector_id.value))
                update_partner_name.set_value(None)
                update_partner_sector_id.set_value(None)
                toggle_update_button()


        #button toggles
        def toggle_add_button():
            if new_partner_name.value and validate_name(new_partner_name.value) is None and new_partner_sector_id.value and new_partner_sector_id.value in sector_list.keys():
                add_button.enable()
            else:
                add_button.disable()


        def toggle_delete_button():
            if data_table.selected:
                delete_button.enable()
            else:
                delete_button.disable()


        def toggle_update_button():
            if update_partner_name.value and validate_name(update_partner_name.value) is None and data_table.selected and update_partner_sector_id.value and update_partner_sector_id.value in sector_list.keys():
                update_button.enable()
            else:
                update_button.disable()


        #validation functions
        def validate_name(value):
            if value and len(value) < 3:
                return 'A partner nevének legalább 3 karakter hosszúnak kell lennie!'
            if value and len(value) > 100:
                return 'A partner neve maximum 100 karakter hosszú lehet!'
            return None


        #visibility toggles
        def toggle_new_card_visibility():
            delete_card.set_visibility(False)
            update_card.set_visibility(False)
            new_card.set_visibility(not(new_card.visible))
            data_table.set_selection('none')
            data_table.selected = []
            update_partner_name.set_value(None)
            update_partner_sector_id.set_value(None)
            new_partner_name.set_value(None)
            new_partner_sector_id.set_value(None)
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
            update_partner_name.set_value(None)
            update_partner_sector_id.set_value(None)
            new_partner_name.set_value(None)
            new_partner_sector_id.set_value(None)
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
            update_partner_name.set_value(None)
            update_partner_sector_id.set_value(None)
            new_partner_name.set_value(None)
            new_partner_sector_id.set_value(None)
            toggle_update_button()


        #record selection handling
        def handle_selection():
            toggle_delete_button()
            toggle_update_button()
            if data_table.selected:
                update_partner_name.set_value(data_table.selected[0]['name'])
                update_partner_sector_id.set_value(data_table.selected[0]['sector_id'])
            else:
                update_partner_name.set_value(None)
                update_partner_sector_id.set_value(None)

        def on_row_dblclick(e):
            app.storage.user['saved_data']["partner_name"] = e.args[1]["name"]
            ui.navigate.to('/purchases/', new_tab=False)


        #table column definitions
        columns=[
                {'name': 'partner_id', 'label': 'Partner ID', 'field': 'partner_id', 'sortable': True},
                {'name': 'name', 'label': 'Név', 'field': 'name', 'sortable': True},
                {'name': 'sector_id', 'label': 'Szektor ID', 'field': 'sector_id', 'sortable': True, 'classes': 'hidden', 'headerClasses': 'hidden'},
                {'name': 'sector_name', 'label': 'Szektor', 'field': 'sector_name', 'sortable': True},
                {'name': 'created_at', 'label': 'Létrehozás időpontja', 'field': 'created_at', 'sortable': True}
            ]

        sector_list = get_sectors()


        #UI element definitions
        ui.label('Partnerek karbantartása').style('color: #6E93D6; font-size: 300%; font-weight: 300')

        with ui.row():
            new_card_button = ui.button('+', on_click=toggle_new_card_visibility).props('color=blue')
            delete_card_button = ui.button('-', on_click=toggle_delete_card_visibility).props('color=red')
            update_card_button = ui.button('!', on_click=toggle_update_card_visibility).props('color=green')

        new_card = ui.card()
        with new_card:
            new_partner_name = ui.input(label= 'Új partner neve', placeholder='írja be az új partner nevét', on_change=toggle_add_button, validation=validate_name).props('clearable').props('size=100')
            new_partner_sector_id = ui.select(label= 'Szektor választása', options=sector_list, with_input=True, on_change=toggle_add_button).props('size=100')
            add_button = ui.button('Új partner hozzáadása', on_click=add_data).props('color=blue')

        delete_card = ui.card()
        with delete_card:
            delete_button = ui.button('A kijelölt partner(ek) törlése', on_click=delete_data).props('color=red')

        update_card = ui.card()
        with update_card:
            update_partner_name = ui.input(label= 'Partner neve', on_change=toggle_update_button, validation=validate_name).props('clearable').props('size=100')
            update_partner_sector_id = ui.select(label= 'Szektor választása', options=sector_list, with_input=True, on_change=toggle_update_button).props('size=100')
            update_button = ui.button('A kijelölt partner módosítása', on_click=update_data).props('color=green')

        search_field = ui.input('Keresés', placeholder='írja be a keresendő partner valamely adatát').props('clearable').props('size=100')
        data_table = ui.table.from_pandas(select_rows(), row_key='partner_id', on_select=handle_selection, pagination=5, columns=columns).classes('w-full').on('rowDblclick', on_row_dblclick)
        data_table.set_filter(str(app.storage.user['saved_data']["sector_name"]))
        search_field.bind_value(data_table, 'filter')


        #initial visibility settings
        toggle_add_button()
        toggle_delete_button()
        toggle_update_button()
        new_card.set_visibility(False)
        delete_card.set_visibility(False)
        update_card.set_visibility(False)

    #connection.close()
