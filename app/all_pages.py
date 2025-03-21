from nicegui import ui
from pages.sectors import show_sectors
from pages.partners import show_partners
from pages.purchases import show_purchases
from pages.opencases import show_cases
from pages.info import show_info
from pages.report import show_report



def create() -> None:
    ui.page('/sectors')(show_sectors)
    ui.page('/partners')(show_partners)
    ui.page('/purchases')(show_purchases)
    ui.page('/opencases')(show_cases)
    ui.page('/report')(show_report)
    ui.page('/info')(show_info)

if __name__ == '__main__':
    create()