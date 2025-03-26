from nicegui import ui, app

def clear_storage():
    app.storage.user['saved_data']["person_id"] = ''


def menu() -> None:
    ui.link('Home', '/').classes(replace='text-black')
    ui.link('Szektorok', '/sectors/').classes(replace='text-black')
    ui.link('Partnerek', '/partners/').classes(replace='text-black')
    ui.link('Vásárlások', '/purchases/').classes(replace='text-black')
    ui.link('Nyitott ügyek', '/opencases/').classes(replace='text-black')
    ui.link('Zárt ügyek', '/closedcases/').classes(replace='text-black')
    ui.link('Személyek', '/persons/').classes(replace='text-black').on('click', clear_storage)
    ui.link('Számlatulajok', '/bank_accounts/').classes(replace='text-black').on('click')
    ui.link('Riport', '/report/').classes(replace='text-black')
    ui.link('Info', '/info/').classes(replace='text-black')