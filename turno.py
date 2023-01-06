import sys
from clingo.application import Application, clingo_main
from clingo import Number
import pprint

import calendar
import textwrap as _textwrap

DAY_NAME = "day_assigned"
NIGHT_NAME = "night_assigned"

PERSONS_FILE = "nombres"
SEPARATED_FILE = "no-juntos"
DAYS_BLOCKED_FILE = "dias-bloqueados"
CONSTRAINTS_FILE = "especiales"

class ClingoApp(Application):
	def __init__(self, name):
		self.program_name = name
		self.pp = pprint.PrettyPrinter(indent=4)

		self.month = None
		self.year = None
		self.holidays = []

	def __on_model(self, model):
		cal = {}
		totals = {}

		for atom in model.symbols(atoms=True):
			if "assigned" not in atom.name:
				continue

			person = atom.arguments[1].name
			day_num = atom.arguments[2].number

			shift = atom.arguments[0].name

			cal.setdefault(day_num, {"day": [], "night": [], "type,week": (self.day_to_weekday[day_num] ,self.day_to_week[day_num])})[shift].append(person)

			totals.setdefault(person, 0)
			totals[person] = totals[person] + 1

		self.pp.pprint(cal)
		
		self.pp.pprint(totals)

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
		print(days,fixed_days,persons,fixed_persons)
		print(int(val), val)
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

		for f in files:
			ctl.load(f)
		if not files:
			ctl.load("-")

		hours_per_day = {}

		# do these 2 with a data structure and then convert to string
		# also, have them be class vars so I can access later!
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

				hours_per_day[day] = {"day": day_hours,
									  "night": night_hours}
		atoms = ""
		max_hours = 0
		for day, shifts in hours_per_day.items():
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

		# use this info to make the excel thing?
		calendar.Calendar().monthdays2calendar(self.year, self.month)

clingo_main(ClingoApp(sys.argv[0]), sys.argv[1:])