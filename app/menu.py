from nicegui import ui



def menu() -> None:
    ui.link('Home', '/').classes(replace='text-black')
    ui.link('Szektorok', '/sectors/').classes(replace='text-black')
    ui.link('Partnerek', '/partners/').classes(replace='text-black')
    ui.link('Vasarlasok', '/purchases/').classes(replace='text-black')
    ui.link('Riport', '/report/').classes(replace='text-black')
    ui.link('Info', '/info/').classes(replace='text-black')