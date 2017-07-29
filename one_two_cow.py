import pickle
from random import shuffle

class Game():
	"""Class defition for One, Two, Cow game"""

	def __init__(self):
		self.game_in_progress = False

		animals = ["dog", "cat", "cow", "sheep", "elephant", "pig", "duck", "monkey", "lion", "turkey", "horse"]
		#animal_hints = {"dog":"woof", "cat":"meow", "cow":"moo", "sheep":"baa", "elephant":"The one with the trunk..."}
		link = "https://www.google.com/logos/fnbx/animal_sounds/{}.mp3"
		animal_hints = {"dog":("Woof!", link.format("dog")), "cat":("Meow!",link.format("cat")), "cow":("Moo!",link.format("cow")), "sheep":("Baa!",link.format("sheep")), \
		                "elephant":("The one with the trunk...",link.format("elephant")), "pig":("Oink!", link.format("pig")), "duck":("Quack!", link.format("duck")), \
		                "monkey":("Ooh! Aah! Aah!", link.format("ape")), "lion":("Roar!", link.format("lion")), "turkey":("Gobble! Gobble!", link.format("turkey")), \
		                "horse":("Neigh!", link.format("horse"))}

		states = ["rhode island", "new york", "california", "texas", "alaska"]
		state_hints = {"rhode island": "providence", "new york":"albany", "california":"sacramento", "texas":"austin", "alaska":"juneau"}

		self.swap_values = {"animals":animals, "states":states}
		self.hint_values = {"animals":animal_hints, "states":state_hints}

	def start_game(self, max_count = 5, game_type = "animals"):
		self.max_count = max_count
		self.game_type = game_type
		self.game_in_progress = True
		self.hints = 25
		self.strikes = 3
		self.round_count = 0
		self.strike_in_progress = False
		numbers_to_swap = range(1, self.max_count+1)
		shuffle(numbers_to_swap)
		shuffle(self.swap_values[self.game_type])
		self.swap = zip(numbers_to_swap, self.swap_values[self.game_type])
		self.game_sequence = range(1, self.max_count+1)

	def end_game(self):
		self.game_in_progress = False

	def start_round(self):
		if self.game_in_progress:
			self.guess_count = 1
			if not self.strike_in_progress:
				self.round_count += 1

			# swap number with animal/state fort this round
			swap_value = self.get_swap_value()
			number_to_swap = self.get_number_to_swap()
			self.game_sequence[number_to_swap-1] = swap_value

			resp = "Welcome to round {}.".format(self.round_count)
			resp = resp + " The goal is to count to {}.".format(self.max_count)
			resp = resp + " The number, {}, has been swapped with {}!".format(number_to_swap, swap_value)
			resp = resp + " What is your first guess?"
			return resp

		else:
			return "Game is not in progress! Please start a game before starting round."

	def get_correct_answer(self):
		return str(self.game_sequence[self.guess_count-1])

	def get_guess(self):
		return str(raw_input("Enter an number: ")).lower()

	def is_guess_correct(self, guess, correct_answer):
		return guess.lower() == str(correct_answer)

	def use_hint(self, correct_answer):
		""" Returns link to hint audio if available and hint text"""

		self.hints -= 1
		try:
			number = int(correct_answer) - 1
			return ("It's the number after {}.".format(number), None)
		except:
			return (self.hint_values[self.game_type][correct_answer])

	def correct_guess(self):
		self.guess_count += 1
		self.strike_in_progress = False

	def incorrect_guess(self):
		self.strikes -= 1
		self.strike_in_progress = True

	def get_swap_value(self):
		return self.swap[self.round_count-1][1]

	def get_number_to_swap(self):
		return self.swap[self.round_count-1][0]

	@classmethod
	def save_game(cls, game, filename):
		with open(filename, 'wb') as output:
		    pickle.dump(game, output, pickle.HIGHEST_PROTOCOL)

	@classmethod
	def load_game(cls, filename):
		with open(filename, 'rb') as input:
			return pickle.load(input)




	

		