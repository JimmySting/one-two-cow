import pickle
from random import shuffle

# Animal values and hints
animals = ["dog", "cat", "cow", "sheep", "elephant", "pig", "duck", "monkey", "lion", "turkey", "horse"]
link = "https://www.google.com/logos/fnbx/animal_sounds/{}.mp3"
animal_hints = {"dog":("Woof!", link.format("dog")), "cat":("Meow!",link.format("cat")), "cow":("Moo!",link.format("cow")), "sheep":("Baa!",link.format("sheep")), \
                "elephant":("The one with the trunk...",link.format("elephant")), "pig":("Oink!", link.format("pig")), "duck":("Quack!", link.format("duck")), \
                "monkey":("Ooh! Aah! Aah!", link.format("ape")), "lion":("Roar!", link.format("lion")), "turkey":("Gobble! Gobble!", link.format("turkey")), \
                "horse":("Neigh!", link.format("horse"))}

# State values and hints
states = ["rhode island", "new york", "california", "texas", "alaska"]
state_hints = {"rhode island": "providence", "new york":"albany", "california":"sacramento", "texas":"austin", "alaska":"juneau"}

class Game():
	"""Class defition for One, Two, Cow game"""

	def __init__(self):
		self.game_in_progress = False
		self.swap_values = {"animals":animals, "states":states}
		self.hint_values = {"animals":animal_hints, "states":state_hints}

	def new_game(self, max_count = 5, game_type = "animals"):
		"""Sets up a new game by resetting all values and generates new sequence"""
		self.game_type = game_type
		self.game_in_progress = True
		self.hints = 3
		self.strikes = 3
		self.round_count = 0
		self.guess_count = 1
		self.strike_in_progress = False
		numbers_to_swap = range(1, max_count+1)
		shuffle(numbers_to_swap)
		shuffle(self.swap_values[self.game_type])
		self.swap = zip(numbers_to_swap, self.swap_values[self.game_type])
		self.game_sequence = range(1, max_count+1)

	def end_game(self):
		self.game_in_progress = False

	def swap_number(self):
		"""Udpates the game sequence based on the round count"""
		swap_value = self.get_swap_value()
		number_to_swap = self.get_number_to_swap()
		self.game_sequence[number_to_swap-1] = swap_value
		return (number_to_swap, swap_value)

	def get_correct_answer(self):
		answer = self.game_sequence[self.guess_count-1]
		try:
			return str(int(answer))
		except:
			return answer

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
		return int(self.swap[self.round_count-1][0])

	@classmethod
	def save_game(cls, game, filename):
		with open(filename, 'wb') as output:
		    pickle.dump(game, output, pickle.HIGHEST_PROTOCOL)

	@classmethod
	def load_game(cls, filename):
		with open(filename, 'rb') as input:
			return pickle.load(input)




	

		