import PySimpleGUI as sg
from clingo.application import clingo_main
from turno import ClingoApp
import multiprocess as mp

import os, sys, errno

FILE_PATHS = {"cons":  "data" + os.sep + "constraints", "names": "data" + os.sep + "nombres"}
DAY = "day"
NIGHT = "night"
WEEKDAY = "weekday"
SAT = "sat"
SUN = "sun"

NO_FILTER = "No filter"
CONSTRAINT_TYPES = ["constraint,blocked", "constraint,blocked_shift", "single", "constraint,type_count", "constraint,at_most_once_a_week", "exception,even_distribution", "special_days"]
        

def create_folder(path):
    """
    from http://stackoverflow.com/posts/5032238/revisions

    :param path: folder to be created
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

class ConstraintGUI:

    def __init__(self):
        self.event_to_popup = {}
        self.event_to_popup["c_blocked"] = self.blocked_popup
        self.event_to_popup["c_blocked_shift"] = self.blocked_shift_popup
        self.event_to_popup["c_single"] = self.single_popup
        self.event_to_popup["c_type_count"] = self.type_count_popup
        self.event_to_popup["c_at_most_once_a_week"] = self.at_most_once_a_week_popup
        self.event_to_popup["c_even_distribution"] = self.even_distribution_popup
        self.event_to_popup["c_special_days"] = self.special_days_popup
        

        try:
            with open(FILE_PATHS["cons"], "r") as _f:
                self.lines = sorted(_f.read().split("\n"))
                self.lines = [line for line in self.lines if line != ""]
                self.lines = sorted(set(self.lines))
        except FileNotFoundError:
            self.lines = []

        try:
            with open(FILE_PATHS["names"], "r") as _f:
                self.names = sorted(_f.read().split("\n"))
                self.names = [name for name in self.names if name != ""]
        except FileNotFoundError:
            self.names = []

        self.fontsize = 14
        self.window_width, self.window_height = 1500, 600

        sg.theme('DarkAmber')   # Add a touch of color

    def blocked_popup(self):
        layout = [ 
                    [sg.Text("Name: "), sg.Combo(self.names, default_value=self.names[0], key="name")],
                    [sg.Text("Start Date: "),  sg.Combo(list(range(1,32)), default_value=1, key="date")],
                    [sg.Text("Amount: "),  sg.Combo(list(range(1,32)), default_value=1, key="amount")],
                    [sg.Button("Add"), sg.Button("Cancel")],
                ]
        window = sg.Window("Blocked Constraint", layout=layout, size=(200,200), 
                        auto_size_text=True, resizable=True,finalize=True,
                        modal=True)

        return_val = []
        while True:  # Event Loop
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':
                break

            elif event == "Add":
                for i in range(values["amount"]):
                    return_val.append(f"constraint,blocked,{values['name']},{values['date']+i}")
                break

        window.close()

        return return_val

    def blocked_shift_popup(self):
        layout = [ 
                    [sg.Text("Name: "), sg.Combo(self.names, default_value=self.names[0], key="name")],
                    [sg.Text("Date: "),  sg.Combo(list(range(1,32)), default_value=1, key="date")],
                    [sg.Text("shift: "),  sg.Combo([DAY,NIGHT], default_value=DAY, key="shift")],
                    [sg.Button("Add"), sg.Button("Cancel")],
                ]
        window = sg.Window("Shift Blocked Constraint", layout=layout, size=(200,200), 
                        auto_size_text=True, resizable=True,finalize=True,
                        modal=True)

        return_val = []
        while True:  # Event Loop
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':
                break

            elif event == "Add":
                return_val.append(f"constraint,blocked_shift,{values['name']},{values['shift']},{values['date']}")
                break

        window.close()

        return return_val

    def single_popup(self):
        layout = [ 
                    [sg.Text("Name: "), sg.Combo(self.names, default_value=self.names[0], key="name")],
                    [sg.Button("Add"), sg.Button("Cancel")],
                ]
        window = sg.Window("Single Constraint", layout=layout, size=(200,200), 
                        auto_size_text=True, resizable=True,finalize=True,
                        modal=True)

        return_val = []
        while True:  # Event Loop
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':
                break

            elif event == "Add":
                return_val.append(f"single,{values['name']}")
                break

        window.close()

        return return_val

    def type_count_popup(self):
        layout = [ 
                    [sg.Text("Name: "), sg.Combo(self.names, default_value=self.names[0], key="name")],
                    [sg.Text("Day Type: "), sg.Combo([SAT,SUN,WEEKDAY], default_value=SAT, key="daytype")],
                    [sg.Text("Shift: "), sg.Combo([DAY,NIGHT], default_value=DAY, key="shift")],
                    [sg.Text("Date: "), sg.Combo(list(range(1,32)), default_value=self.names[0], key="date")],

                    [sg.Button("Add"), sg.Button("Cancel")],
                ]
        window = sg.Window("Type Count Constraint", layout=layout, size=(200,200), 
                        auto_size_text=True, resizable=True,finalize=True,
                        modal=True)

        return_val = []
        while True:  # Event Loop
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':
                break

            elif event == "Add":
                return_val.append(f"constraint,type_count,{values['name']},{values['daytype']},{values['shift']},{values['date']}")
                break

        window.close()

        return return_val

    def at_most_once_a_week_popup(self):
        layout = [ 
                    [sg.Text("Name: "), sg.Combo(self.names, default_value=self.names[0], key="name")],
                    [sg.Text("Day Type: "), sg.Combo([SAT,SUN,WEEKDAY], default_value=SAT, key="daytype")],
                    [sg.Button("Add"), sg.Button("Cancel")],
                ]
        window = sg.Window("At most once a week Constraint", layout=layout, size=(200,200), 
                        auto_size_text=True, resizable=True,finalize=True,
                        modal=True)

        return_val = []
        while True:  # Event Loop
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':
                break

            elif event == "Add":
                return_val.append(f"constraint,at_most_once_a_week,{values['name']},{values['daytype']}")
                break

        window.close()

        return return_val

    def even_distribution_popup(self):
        layout = [ 
                    [sg.Text("Name: "), sg.Combo(self.names, default_value=self.names[0], key="name")],
                    [sg.Button("Add"), sg.Button("Cancel")],
                ]
        window = sg.Window("Even Distribution Exception", layout=layout, size=(200,200), 
                        auto_size_text=True, resizable=True,finalize=True,
                        modal=True)

        return_val = []
        while True:  # Event Loop
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':
                break

            elif event == "Add":
                return_val.append(f"exception,even_distribution,{values['name']}")
                break

        window.close()

        return return_val

    def special_days_popup(self):
        layout = [ 
                    [sg.Text("Name: "), sg.Combo(self.names, default_value=self.names[0], key="name")],
                    [sg.Text("Amount: "), sg.Combo(list(range(1,32)), default_value=1, key="amount")],
                    [sg.Button("Add"), sg.Button("Cancel")],
                ]
        window = sg.Window("Special Days Constraint", layout=layout, size=(200,200), 
                        auto_size_text=True, resizable=True,finalize=True,
                        modal=True)

        return_val = []
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':
                break

            elif event == "Add":
                return_val.append(f"special_days,{values['name']},{values['amount']}")
                break
        
        window.close()

        return return_val

    def clingo_run_popup(self):
        process = None

        layout = [
                    [sg.Text("Month: "), sg.Push(), sg.Combo(list(range(1,13)), default_value=1, key="run_month")],
                    [sg.Text("Year: "), sg.Push(), sg.InputText("2023", key="run_year")],
                    [sg.Text("Holidays: "), sg.Push(), sg.InputText(key="run_holidays")],
                    [sg.Button("Run", key="e_run"), sg.Button("Cancel", key="e_cancel")],
                    [sg.Multiline("", size=(50, 10), key="run_output", expand_x=True, expand_y=True)],
                 ]
        
        window = sg.Window("Run Program", layout=layout, size=(400,400), 
                auto_size_text=True, resizable=True,finalize=True,
                modal=True)

        while True:  # Event Loop
            event, values = window.read(timeout=500, timeout_key="run_window_timeout")

            if event == sg.WIN_CLOSED or event == 'Cancel':
                if process is not None:
                    process.terminate()
                break

            elif event == "e_run":
                if process is not None:
                    continue

                if values["run_holidays"] == "":
                    values["run_holidays"] = "0"
                clingo_app_arguments = ["--month",    f"{values['run_month']}",
                                        "--year",     f"{values['run_year']}", 
                                        "--holidays", f"{values['run_holidays']}"]

                process = mp.Process(target=clingo_main, args=(ClingoApp(), clingo_app_arguments))

                process.start()

            elif event == "e_cancel":
                if process is not None:
                    window["run_output"].update("Process terminated!")

                    process.terminate()
                    process = None

            if event == "run_window_timeout":
                if process is not None:
                    if not process.is_alive():
                        window["run_output"].update("Process Finished!")
                        process = None
                    else:
                        window["run_output"].update("Process running...")

        window.close()

    def main_window(self):
        font = ("Arial", self.fontsize)
        sg.set_options(font=font)
        menu_def = [['File', ['Save::save_event', "Run::run_event"]]]

        const_add_layout = [
                    [sg.Menu(menu_def, tearoff=False)],
                    [sg.Text("Add constraint blocked:"), sg.Push(), sg.Button("Add", key="c_blocked")],
                    [sg.Text("Add constraint blocked shift:"), sg.Push(), sg.Button("Add", key="c_blocked_shift")],
                    [sg.Text("Add constraint single:"), sg.Push(), sg.Button("Add", key="c_single")],
                    [sg.Text("Add constraint type count:"), sg.Push(), sg.Button("Add", key="c_type_count")],
                    [sg.Text("Add constraint at most once a week:"), sg.Push(), sg.Button("Add", key="c_at_most_once_a_week")],
                    [sg.Text("Add exception even distribution:"), sg.Push(), sg.Button("Add", key="c_even_distribution")],
                    [sg.Text("Add special days:"), sg.Push(), sg.Button("Add", key="c_special_days")],
                    [sg.Button('Delete', key="delete_constraint")],
                   ]
        
        const_filter_layout = [
                                [sg.Text("Filter by name", key="t_filter_name"), sg.Push(), sg.Combo([NO_FILTER]+self.names, default_value=NO_FILTER, key="filter_name")],
                                [sg.Text("Filter by type", key="t_filter_type"), sg.Push(), sg.Combo([NO_FILTER]+CONSTRAINT_TYPES, default_value=NO_FILTER, key="filter_type")],
                                [sg.Button("Filter", key="e_filter"), sg.Button("Clear", key="e_clear_filter")],
                              ]

        name_layout = [
                        [ sg.Button("Add", key="add_name"), sg.Push(), sg.InputText(key="new_name")],
                        [sg.Button("Delete", key="delete_name")],
                      ]

        layout = [
                    [sg.Listbox(self.lines, size=(50, len(self.lines)), key='selected_constraint', expand_y=True), sg.Frame(title="", layout=const_add_layout), sg.Frame(title="", layout=const_filter_layout)],
                    [sg.Listbox(self.names, size=(50, len(self.names)), key='selected_name', expand_y=True), sg.Frame(title="", layout=name_layout)],
                 ]

        self.main_window = sg.Window('Window Title', layout, size=(self.window_width, self.window_height),
                        auto_size_text= True, resizable=True, finalize=True)
        self.main_window.set_min_size((500, 250))

        while True:  # Event Loop
            event, values = self.main_window.read()
            # print(event, values)
            if event == sg.WIN_CLOSED or event == 'Exit' or event =="c_blocked_cancel":
                break
            elif event == 'delete_constraint':
                if len(values["selected_constraint"]) > 0:
                    # change the "output" element to be the value of "input" element
                    self.lines.remove(values["selected_constraint"][0])
                    self.lines = sorted(set(self.lines))
                    self.main_window["selected_constraint"].update(sorted(self.lines))

            elif event == 'delete_name':
                if len(values["selected_name"]) > 0:
                    # change the "output" element to be the value of "input" element
                    self.names.remove(values["selected_name"][0])
                    self.names = sorted(set(self.names))
                    self.main_window["selected_name"].update(sorted(self.names))

            elif event == "add_name":
                if values["new_name"] not in self.names and values["new_name"] != "":
                    self.names.append(values["new_name"])
                    self.main_window["selected_name"].update(sorted(self.names))
                    self.main_window["new_name"].update("")

            elif event == "e_filter":
                filtered_list = self.filter_constraints(values["filter_name"], values["filter_type"])
                self.main_window["selected_constraint"].update(filtered_list)

            elif event == "e_clear_filter":
                self.main_window["filter_name"].update(NO_FILTER)
                self.main_window["filter_type"].update(NO_FILTER)
                self.main_window["selected_constraint"].update(self.lines)
            
            elif event in self.event_to_popup:
                if self.check_names():
                    self.add_to_lines(self.event_to_popup[event]())

            elif event == "Save::save_event":
                
                create_folder("data")

                with open(FILE_PATHS["cons"], "w") as _f:
                    _f.write("\n".join(self.lines))
                with open(FILE_PATHS["names"], "w") as _f:
                    _f.write("\n".join(self.names))

            elif event == "Run::run_event":
                self.clingo_run_popup()

        self.main_window.close()

    def check_names(self):
        if self.names == []:
            sg.popup_ok("There are no names!", no_titlebar=True)
            return False
        return True

    def filter_constraints(self, name_filter, type_filter):
        return [line for line in self.lines if 
                                 (name_filter in line or name_filter == NO_FILTER)
                                  and 
                                  (type_filter in line or type_filter == NO_FILTER)]

    def add_to_lines(self, new_lines):
        if new_lines is not None:
            self.lines.extend(new_lines)
            self.lines = sorted(set(self.lines))
            self.main_window["selected_constraint"].update(self.lines)

if __name__ == "__main__":
    mp.freeze_support()
    app = ConstraintGUI()
    app.main_window()