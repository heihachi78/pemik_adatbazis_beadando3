from nicegui import ui

def content() -> None:
    with ui.column():
        with open('README.md', 'r') as file:
            data = file.read().replace('\n', '  \n')
        ui.markdown(data).style('font-size: 150%; font-weight: 300')