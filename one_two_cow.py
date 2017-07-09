from random import shuffle

class Game():
	"""Class defition for One, Two, Cow game"""

	def __init__(self):
		self.game_in_progress = False

		animals = ["dog", "cat", "cow", "sheep", "elephant"]
		animal_hints = {"dog'":"woof", "cat":"meow", "cow":"moo", "sheep":"baa", "elephant":"The one with the trunk..."}

		states = ["rhode island", "new york", "california", "texas", "alaska"]
		state_hints = {"rhode island": "providence", "new york":"albany", "california":"sacramento", "texas":"austin", "alaska":"juneau"}

		self.swap_values = {"animals":animals, "states":states}
		self.hint_values = {"animals":animal_hints, "states":state_hints}

	def start_game(self, max_count = 5, game_type = "animals"):
		self.max_count = max_count
		self.game_type = game_type
		self.game_in_progress = True
		self.hints = 3
		self.strikes = 3
		self.round_count = 0
		self.strike_in_progress = False
		numbers_to_swap = range(1, self.max_count+1)
		shuffle(numbers_to_swap)
		shuffle(self.swap_values[self.game_type])
		self.swap = zip(numbers_to_swap, self.swap_values[self.game_type])
		self.game_sequence = range(1, self.max_count+1)

	def end_game(self):
		print("Thanks for playing!")
		self.game_in_progress = False

	def start_round(self):
		if self.game_in_progress:
			self.guess_count = 1
			if not self.strike_in_progress:
				self.round_count += 1

			print("\n\n\n\n\n\n\n\n\n\n\n\n\nWelcome to round "+str(self.round_count))
			print("The goal is to count to "+str(self.max_count))

			# swap number with animal/state fort this round
			swap_value = self.get_swap_value()
			number_to_swap = self.get_number_to_swap()
			print("The number, "+str(number_to_swap)+", has been swapped with "+swap_value+"!")
			self.game_sequence[number_to_swap-1] = swap_value
			
			strikes_at_start_of_round = self.strikes
			while self.strikes == strikes_at_start_of_round and self.guess_count <= self.max_count:
				correct_answer = self.get_correct_answer()
				guess = self.get_guess()
				self.evaluate_guess(guess, correct_answer)

			self.end_round()

		else:
			print("Game is not in progress! Please start a game before starting round.")

	def get_correct_answer(self):
		return str(self.game_sequence[self.guess_count-1])

	def get_guess(self):
		return str(raw_input("Enter an number: ")).lower()

	def evaluate_guess(self, guess, correct_answer):
		guess_evaluated = False

		while not guess_evaluated:
			if guess == "hint" and self.hints != 0:
				self.use_hint(correct_answer)
				guess = self.get_guess()
			elif guess == "hint" and self.hints == 0:
				print("Gosh! You are out of hints! Guess again!")
				guess = self.get_guess()
			elif self.is_guess_correct(guess, correct_answer):
				guess_evaluated = True
				self.correct_guess()
			else:
				guess_evaluated =True
				self.incorrect_guess(correct_answer)


	def end_round(self):
		if self.strikes == 0:
			print("Three strikes are up! Game over!")
			self.end_game()

		elif self.round_count == self.max_count and not self.strike_in_progress:
			print("Oh llama! You won the game!")
			self.end_game()

		else:
			valid_responses = ['y','n']
			is_valid_response = False
			while not is_valid_response:
				response = str(raw_input("Round over! You have "+str(self.strikes)+ " strikes and "+str(self.hints)+ " hints left. Would you like to continue? (y/n): ")).lower()
				if response[0] in valid_responses:
					is_valid_response = True
					if response == 'y':
						self.start_round()
					elif response == 'n':
						self.end_game()


	def is_guess_correct(self, guess, correct_answer):
		return guess.lower() == str(correct_answer)

	def use_hint(self, correct_answer):
		self.hints -= 1
		try:
			number = int(correct_answer)
			print("It's the number after "+str(number-1)+"...")
		except:
			print(self.hint_values[self.game_type][correct_answer])

	def correct_guess(self):
		self.guess_count += 1
		self.strike_in_progress = False
		print("That's correct!")

	def incorrect_guess(self, correct_answer):
		self.strikes -= 1
		self.strike_in_progress = True
		print("Oh no! That is not correct! The correct answer was: "+str(correct_answer))

	def get_swap_value(self):
		return self.swap[self.round_count-1][1]

	def get_number_to_swap(self):
		return self.swap[self.round_count-1][0]



	

		