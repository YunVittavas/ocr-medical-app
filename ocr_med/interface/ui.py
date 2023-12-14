import dearpygui.dearpygui as dpg
import os

APPS_UI_INIT_FILE_PATH = os.path.join(os.path.dirname(__file__) , "ui.ini")
APPS_UI_TITLE = "Cybathlon 2024 - BCILAB MAHIDOL Team"
APPS_UI_WIDTH_DEFAULT = 600
APPS_UI_HEIGHT_DEFAULT = 600

APPS_WINDOW_HEIGHT_DEFAULT = 200
APPS_WINDOW_WIDTH_DEFAULT = 200


# --- Step 1 : Initialize Viewport (Border, OuterFrame) ---
def ui_init():
    dpg.create_context()
    dpg.configure_app(init_file=APPS_UI_INIT_FILE_PATH)
    dpg.create_viewport(title=APPS_UI_TITLE , width=APPS_UI_WIDTH_DEFAULT , height=APPS_UI_HEIGHT_DEFAULT)

    dpg.setup_dearpygui()
    ui_applyDisabledTheme() # Add global disabled theme


# --- Step 3 : Start Renderer Loop ---
def ui_startRenderer():
    # TODO: start render thred here
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


# --- Global Disabled Theme ---
def ui_applyDisabledTheme():
    bg_color = [40, 40, 40, 160]
    gray_color = [60, 60, 60, 160]
    with dpg.theme() as disabled_theme:

        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, gray_color)
            dpg.add_theme_color(dpg.mvThemeCol_Button, bg_color)

        with dpg.theme_component(dpg.mvSliderInt, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, gray_color)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive , gray_color)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, bg_color)

    dpg.bind_theme(disabled_theme)


# --- Step 2 : Draw Elements ---
def ui_draw():
    pass