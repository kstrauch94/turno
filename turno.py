import sys
from clingo.application import Application, clingo_main
from clingo import Number
import pprint

import calendar
import textwrap as _textwrap
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Color, Alignment, Border, Side, PatternFill, NamedStyle


import os

from enum import Enum

DAY_NAME = "day_assigned"
NIGHT_NAME = "night_assigned"

DATA_FOLDER = "data"
PERSONS_FILE = DATA_FOLDER + os.sep + "nombres"
SEPARATED_FILE = DATA_FOLDER + os.sep +"no-juntos"
DAYS_BLOCKED_FILE = DATA_FOLDER + os.sep +"dias-bloqueados"
CONSTRAINTS_FILE = DATA_FOLDER + os.sep +"especiales"

# styles
Text_14_bold = Font(size=14, bold=True)
Text_12_bold = Font(size=12, bold=True)
Text_12 = Font(size=12)
Text_12_bold_red = Font(color="00FF0000", size=12, bold=True)

center_aligned_text = Alignment(horizontal="center")

yellow_fill = PatternFill(fill_type="solid", start_color="00FFFF00", end_color="00FFFF00")
brown_fill = PatternFill(fill_type="solid", start_color="00FFCC99", end_color="00FFCC99")

# full styles
weekday_style = NamedStyle(name="weekday")
weekday_style.font = Text_14_bold
weekday_style.alignment = center_aligned_text

normal_bold_style = NamedStyle(name="normal_bold")
normal_bold_style.font = Text_12_bold
normal_bold_style.alignment = center_aligned_text

normal_style = NamedStyle(name="normal")
normal_style.font = Text_12
normal_style.alignment = center_aligned_text

normal_red_style = NamedStyle(name="normal_red")
normal_red_style.font = Text_12_bold_red
normal_red_style.alignment = center_aligned_text


def xlref(row, column, zero_indexed=False):
    if zero_indexed:
        row += 1
        column += 1
    return get_column_letter(column) + str(row)

class ClingoApp(Application):
	def __init__(self, name):
		self.program_name = name
		self.pp = pprint.PrettyPrinter(indent=4)

		self.month = None
		self.year = None
		self.holidays = []

	def __on_model(self, model):
		self.model = model
		cal = self.parse_model()
		self.create_workbook(cal)

	def parse_model(self):
		cal = {}
		total_days = {}
		total_hours = {}

		for atom in self.model.symbols(atoms=True):
			if atom.name == "assigned":

				person = atom.arguments[1].name
				day_num = atom.arguments[2].number

				shift = atom.arguments[0].name

				cal.setdefault(day_num, {"day": [], "night": [], "type,week": (self.day_to_weekday[day_num] ,self.day_to_week[day_num])})[shift].append(person)

				total_days.setdefault(person, 0)
				total_days[person] = total_days[person] + 1
			
			if atom.name == "hours_per_person" and len(atom.arguments) == 2:
				print(atom)
				person = atom.arguments[0].name
				hours = atom.arguments[1].number

				total_hours[person] = hours

		self.pp.pprint(cal)
		
		self.pp.pprint(total_days)
		self.pp.pprint(total_hours)

		return cal

	def create_workbook(self, cal):
		workbook = Workbook()

		self.create_main_sheet(cal, workbook.active)

		sheet_hours = workbook.create_sheet("hours")
		self.create_hours_sheet(cal, sheet_hours)

		workbook.save(filename="out.xlsx")

	def set_sheet_dims(self, sheet):
		dims = {}
		for row in sheet.rows:
			for cell in row:
				if cell.value:
					dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))    
		for col, value in dims.items():
			sheet.column_dimensions[col].width = value + 3

	def create_main_sheet(self, cal, sheet):
		row_offset = 4
		col_offset = 4

		shift_offset = {"day": 1, "night": 3}

		cell = sheet.cell(row=row_offset-2, column=col_offset-1)
		cell.value = f"Turno para el mes {self.month} del año {self.year}"
		cell.font = Text_14_bold
		cell.alignment = center_aligned_text


		cell = sheet.cell(row=row_offset-1, column=col_offset-1)
		cell.value = "Horario"
		cell.style = weekday_style

		cell = sheet.cell(row=row_offset-1, column=col_offset-2)
		cell.value = "Turno"
		cell.style = weekday_style


		weekdaynum_to_weekday = {0: "Lunes", 1: "Martes", 2: "Miercoles", 3: "Jueves", 4: "Viernes", 5: "Sabado", 6: "Domingo"}
		for i in range(0,7):
			cell = sheet.cell(row=row_offset-1, column=col_offset+i)
			cell.value = weekdaynum_to_weekday[i]
			cell.style = weekday_style


		for day in sorted(cal.keys()):
			weekday,week = cal[day]["type,week"]

			cell = sheet.cell(row=row_offset + week*5, column=col_offset+weekday)
			cell.value = day
			cell.style = normal_bold_style
			if weekday >= 5:
				cell.font = Text_12_bold_red
				
			for shift in ["day", "night"]:
				for order, person in enumerate(cal[day][shift], start=0):
					row = row_offset + self.day_to_week[day]*5 + shift_offset[shift] + order
					col = col_offset + self.day_to_weekday[day]
					cell = sheet.cell(row=row, column=col)
					cell.value = person
					cell.style = normal_bold_style
					if shift == "day":
						cell.fill = brown_fill

					if day in self.holidays:
						cell.font = Text_12_bold_red
					if weekday >= 5:
						cell.font = Text_12_bold_red
						cell.fill = yellow_fill


					cell = sheet.cell(row=row, column=col_offset-1)
					cell.value = "7:00pm - 7:00am"
					cell.style = normal_bold_style
					if shift == "day":
						cell.value = "7:00am - 7:00pm"
						cell.fill = brown_fill

					cell = sheet.cell(row=row, column=col_offset-2)
					cell.value = shift
					cell.style = normal_bold_style
					if shift == "day":
						cell.fill = brown_fill

		self.set_sheet_dims(sheet)


	def create_hours_sheet(self, cal, sheet):
		row_offset = 4
		col_offset = 2

		shift_offset = {"day": 1, "night": 3}


		weekdaynum_to_weekday = {0: "Lunes", 1: "Martes", 2: "Miercoles", 3: "Jueves", 4: "Viernes", 5: "Sabado", 6: "Domingo"}
		for i in range(0,7):
			cell = sheet.cell(row=row_offset-1, column=col_offset+i)
			cell.value = weekdaynum_to_weekday[i]
			cell.style = weekday_style


		for day in sorted(cal.keys()):
			weekday,week = cal[day]["type,week"]

			cell = sheet.cell(row=row_offset + week*5, column=col_offset+weekday)
			cell.value = day
			cell.style = normal_bold_style
			cell.fill = yellow_fill
				
			for shift in ["day", "night"]:
				for order, person in enumerate(cal[day][shift], start=0):
					row = row_offset + self.day_to_week[day]*5 + shift_offset[shift] + order
					col = col_offset + self.day_to_weekday[day]
					cell = sheet.cell(row=row, column=col)
					cell.value = self.hours_per_day[day][shift]
					cell.style = normal_style
					if shift == "day":
						cell.fill = brown_fill

					if day in self.holidays:
						cell.font = Text_12_bold_red

		self.set_sheet_dims(sheet)


	def register_options(self, options):
		"""
		See clingo.clingo_main().
		"""

		group = "Turno Options"

		options.add(group, "month", _textwrap.dedent("""Month as a number"""), self.__parse_month)
		options.add(group, "year", _textwrap.dedent("""Year"""), self.__parse_year)
		options.add(group, "holiday", _textwrap.dedent("""Holidays separated by ,"""), self.__parse_holiday)

	def __parse_holiday(self, option):
		self.holidays = [int(h) for h in option.split(",")]
		
		for h in self.holidays:
			if h > 31 or h < 1:
				return False
		
		return True

	def __parse_month(self, option):
		self.month = int(option)
		
		if self.month < 13 and self.month > 0:
			return True
		
		print("Month has to be in the range 1 to 12")
		
		return False

	def __parse_year(self, option):
		self.year = int(option)
		
		if self.year < 2100 and self.year > 2000:
			return True
		
		print("year has to be in the range 2000 to 2100")
		
		return False

	def check_not_none(self, val, msg):
		if val is None:
			print(msg)
			return False
		return True

	def min_max(self, values):

		days, fixed_days, persons, fixed_persons = values.arguments

		val = ((days.number * 4) - fixed_days.number) / (persons.number - fixed_persons.number)
		return Number(int(val))

	def load_info_files(self, ctl):
		persons = self.parse_persons()
		blocks = self.parse_blocks()
		separated = self.parse_separated()
		constraints = self.parse_constraints()

		print(persons)
		print(blocks)
		print(separated)

		ctl.add("base", [], persons)
		ctl.add("base", [], blocks)
		ctl.add("base", [], separated)
		ctl.add("base", [], constraints)
		

	def parse_persons(self):
		persons = ""
		with open(PERSONS_FILE, "r") as _f:
			for person in _f.readlines():
				persons += f"person({person.strip()}).\n"

		return persons

	def parse_blocks(self):
		blocks = ""
		with open(DAYS_BLOCKED_FILE, "r") as _f:
			for block in _f.readlines():
				person, first, last = str(block.strip()).split(",")
				blocks += f"constraint(blocked, ({person}, {first}..{last})).\n"

		return blocks

	def parse_separated(self):
		separated = ""
		with open(SEPARATED_FILE, "r") as _f:
			for person in _f.readlines():
				separated += f"single({person.strip()}).\n"

		return separated

	def parse_constraints(self):
		constraints = ""
		with open(CONSTRAINTS_FILE, "r") as _f:
			for constraint in _f.readlines():
				constraint = constraint.strip().split(",")
				if len(constraint) == 0:
					continue
				if constraint[0] == "constraint":
					constraints += f"constraint({constraint[1]}, ({','.join(constraint[2:])})).\n"
				
				elif constraint[0] == "exception":
					constraints += f"exception({constraint[1]}, ({','.join(constraint[2:])})).\n"

				elif constraint[0] == "special_days":
					constraints += f"special_days({constraint[1]},{constraint[2]}).\n"

		return constraints

	def main(self, ctl, files):

		if not self.check_not_none(self.month, "Please add a month via the --month option"):
			return
			
		if not self.check_not_none(self.year, "Please add a year via the --year option"):
			return

		ctl.load("turno.lp")
		for f in files:
			if "turno.lp" not in f:
				ctl.load(f)
		if not files:
			ctl.load("-")

		self.hours_per_day = {}

		self.day_to_weekday = {}
		self.day_to_week = {}
		days = calendar.monthrange(self.year, self.month)[1]
		for i, week in enumerate(calendar.Calendar().monthdays2calendar(self.year, self.month)):
			for day, weekday in week:
				if day == 0:
					continue
				self.day_to_weekday[day] = weekday
				self.day_to_week[day] = i

				if day in self.holidays:
					day_hours = 12
					night_hours = 12
				elif weekday == 5:
					day_hours = 9
					night_hours = 9
				elif weekday == 6:
					day_hours = 12
					night_hours = 12
				else:
					day_hours = 3
					night_hours = 4

				self.hours_per_day[day] = {"day": day_hours,
									  "night": night_hours}
		atoms = ""
		max_hours = 0
		for day, shifts in self.hours_per_day.items():
			for shift, hours in shifts.items():
				atoms += f"hours({shift},{day},{hours}).\n"

				max_hours += hours*2
		
		self.load_info_files(ctl)

		ctl.add("base", [], atoms)

		ctl.add("base", [], f"max_hours({max_hours}).\n")

		s1 = ".\n".join([f"day_to_weekday({day},{weekday})" for day, weekday in self.day_to_weekday.items()]) + ".\n"
		ctl.add("base", [], s1)
		
		s2 = ".\n".join([f"day_to_week({day},{week})" for day, week in self.day_to_week.items()]) + ".\n"
		ctl.add("base", [], s2)

		ctl.add("base", [], f"max_days({days}).")

		ctl.ground([("base", [])], self)
		ctl.solve(on_model=self.__on_model)

		cal = self.parse_model()
clingo_main(ClingoApp(sys.argv[0]), sys.argv[1:])