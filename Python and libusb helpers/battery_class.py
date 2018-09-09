import usb1
import binascii
from analyzeReply import *

class BatteryData:
	""" Handles and stores battery data """
	def __init__(self, battery_chem, series_cells, batt_capacity):
		self.chemistry = battery_chem
		self.series_cells = series_cells
		self.capacity = batt_capacity

	def load_action(self, action):
		if action == 'balance charge':
			self.current_action = action
			return True
		elif action == 'charge':
			self.current_action = action
			return True
		elif action == 'fast charge':
			self.current_action = action
			return True
		elif action == 'discharge':
			self.current_action = action
			return True
		elif action == 'storage':
			self.current_action = action
			return True
		else:
			print 'unknown action'
			return False

	def start_action(self):
		return True