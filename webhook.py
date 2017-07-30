import os
import cPickle

from one_two_cow import Game
from flask import Flask
from flask_assistant import Assistant, ask, tell, event, context_manager
from random import choice

import logging
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

app = Flask(__name__)
assist = Assistant(app, '/')

def save_game(game):
	#context_manager.set("game_in_progress", "game", cPickle.dumps(game))
	game_content = {"game_type":game.game_type, "round_count":game.round_count, "game_sequence":game.game_sequence, "guess_count":game.guess_count, "hints":game.hints, \
	                "strikes":game.strikes, "strike_in_progress":game.strike_in_progress, "swap":game.swap}
	context_manager.set("game_in_progress", "game_content", cPickle.dumps(game_content))

def load_game():
	game = Game()
	game.game_in_progress = True
	game_content = cPickle.loads(str(context_manager.get_param("game_in_progress", "game_content")))
	game.game_type = game_content["game_type"]
	game.round_count = int(game_content["round_count"])
	game.game_sequence = game_content["game_sequence"]
	game.guess_count = int(game_content["guess_count"])
	game.hints = int(game_content["hints"])
	game.strikes = int(game_content["strikes"])
	game.strike_in_progress = game_content["strike_in_progress"]
	game.swap = game_content["swap"]
	return game

def get_hint_text(hint_count):
	return "hint" if hint_count == 1 else "hints"

def get_strike_text(strike_count):
	return "strike" if strike_count == 1 else "strikes"

def get_round_over_text(hint_count, strike_count):
	return "The round is over! You have {} {} and {} {} left! Would you like to start a new round?".format(
		   hint_count, get_hint_text(hint_count), strike_count, get_strike_text(strike_count))

words_to_number = {"zero":0, "one":1, "two":2, "too":2, "to":2, "three":3, "four":4, "for":4, "five":5, "six":6, "seven":7, "eight":8, "ate":8, "nine":9, "ten":10}
def convert_guess(guess):
	# Converts a potential number guess to an integer - takes care of homonyms since any word can pe provided with guess
	return str(words_to_number[guess]) if guess in words_to_number.keys() else guess

@assist.action('welcome-greeting')
def welcome_greeting():
    speech_options = ["Welcome to 'One, Two, Cow'! The game where the number after 9 could be...elephant! Would you like to hear the rules or start a game?",
                      "Welcome to 'One, Two, Cow'! The counting game where numbers morph into animals! Would you like to hear the rules or start a game?",
                      "Welcome to 'One, Two, Cow'! A counting game that swaps out numbers with your favorite animals! Would you like to hear the rules or start a game?"]

    context_manager.add("choose_game_or_rules", lifespan=5)

    return ask(choice(speech_options))

@assist.context("choose_game_or_rules")
@assist.action("start-game")
def start_new_game():
	"""Prepares a new game of One, Two, Cow for the user."""

	game = Game()
	game.new_game(5)
	context_manager.add("game_in_progress")
	context_manager.add("start-game-followup", lifespan=3)
	save_game(game)
	speech_options = ["Great! Let's start a new game of One, Two, Cow! Are you ready to start round 1?",
	                  "Okay! Let's start a new game of One, Two, Cow! Are you ready to start the first round?",
	                  "Sure! Starting a new game of One, Two, Cow! Are you ready to begin?"]
	return ask(choice(speech_options))

@assist.context("start-game-followup")
@assist.action("start-game-yes")
def first_round_confirmation():
	return event("start_round")

@assist.context("game_in_progress")
@assist.action("start-round")
def start_round(game):
	"""Starts a round of a game in progress. Swaps new number."""

	game = load_game()
	context_manager.add("guess", lifespan=1)
	#speech = game.start_round()

	# new stuff
	game.guess_count = 1
	if not game.strike_in_progress:
		game.round_count += 1
	(number_to_swap, swap_value) = game.swap_number()

	speech = "Welcome to round {}.".format(game.round_count)
	speech = speech + " The goal is to count to {}.".format(len(game.game_sequence))
	speech = speech + " The number, {}, has been swapped with {}!".format(number_to_swap, swap_value)
	speech = speech + " What is your first guess?"

	save_game(game)
	return ask(speech)

@assist.context("game_in_progress", "guess")
@assist.action("user-guess", mapping={'user_guess': 'sys.any'})
def evaluate_guess(user_guess, game):
	"""Evaluates a guess from user for a game that is in progress."""

	game = load_game()
	correct_answer = game.get_correct_answer()
	if game.is_guess_correct(convert_guess(user_guess), correct_answer):	
		return correct_guess(game)
	else:
		return incorrect_guess(game, correct_answer)

def incorrect_guess(game, correct_answer):

	speech_options_incorrect = ["Oh no! That is not correct! The correct answer was: {}.".format(correct_answer),
	                            "Sorry! That wasn't correct! The correct answer was: {}.".format(correct_answer)]

	game.incorrect_guess()
	save_game(game)
	if game.strikes == 0:
		return event("game_over")
	else:
		speech = choice(speech_options_incorrect)
		speech =  speech + " " + get_round_over_text(game.hints, game.strikes)
		context_manager.add("user_round_response", lifespan=5)
		return ask(speech)

def correct_guess(game):

	speech_options = ["That's correct! What comes next?",
	                  "Right answer! What is your next guess?",
	                  "Nice job! Now what comes next?"]

	max_count = len(game.game_sequence)
	if game.round_count == max_count and game.guess_count == max_count and not game.strike_in_progress:
		save_game(game)
		return event("won_game")
	elif game.guess_count == max_count and not game.strike_in_progress:
		speech =  "Correct! " + get_round_over_text(game.hints, game.strikes)
		context_manager.add("user_round_response", lifespan=5)
		save_game(game)
		return ask(speech)
	else:
		game.correct_guess()
		save_game(game)
	  	context_manager.add("guess", lifespan=1)
		return ask(choice(speech_options))

@assist.context("user_round_response")
@assist.action("round-response")
def round_response(round_response, game):
	save_game(load_game())
	if 'n' in round_response:
		return event("end_game")
	else:
		return event("start_round") 

@assist.context("game_in_progress")
@assist.action("give-hint")
def give_hint(game):
	"""Gives hint for current answer"""

	game = load_game()
	if game.hints != 0:
		(hint_text, hint_link) = game.use_hint(game.get_correct_answer())
		speech = "<speak>Okay, here's your hint. <audio src='{}'>{}</audio> Now, what is your next guess?</speak>".format(hint_link, hint_text)
	else:
		speech = "Gosh! You are out of hints! Guess again!"
	
	context_manager.add("guess", lifespan=1)
	save_game(game)
	return ask(speech)

@assist.context("game_in_progress")
@assist.action("game-over")
def game_over(game):
	game = load_game()
	context_manager.get("game_in_progress").lifespan = 0
	game.end_game()
	speech_options = ["Oh no! You are turtle-ly out of strikes!",
	                  "Oh, the hue-manatee! You're out of strikes!"]
	speech = choice(speech_options) + " Would you like to start a new game or hear about the rules?"
	context_manager.add("choose_game_or_rules", lifespan=3)
	return ask(speech)

@assist.context("game_in_progress")
@assist.action("won-game")
def won_game(game):
	game = load_game()
	context_manager.get("game_in_progress").lifespan = 0
	game.end_game()
	speech = "Oh llama! You won the game! Would you like to start a new game or hear about the rules?"
	context_manager.add("choose_game_or_rules", lifespan=3)
	return ask(speech)

@assist.context("game_in_progress")
@assist.action("end-game")
def end_game(game):
	"""Ends current game of One, Two, Cow."""
	
	speech_options = ["Ok, no problem! Thanks for playing One, Two Cow!",
	                  "Sure thing! Thanks for playing One, Two Cow!"]
	return tell(choice(speech_options))

if __name__ == '__main__':
    app.run(debug=True)

