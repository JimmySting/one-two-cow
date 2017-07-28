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
	context_manager.set("game_in_progress", "game", cPickle.dumps(game))

def load_game():
	return cPickle.loads(str(context_manager.get_param("game_in_progress", "game")))

def get_hint_text(hint_count):
	return "hints" if hint_count > 1 else "hint"

def get_strike_text(strike_count):
	return "strikes" if strike_count > 1 else "strike"

def get_round_over_text(hint_count, strike_count):
	return "The round is over! You have {} {} and {} {} left! Would you like to start a new round?".format(
		   hint_count, get_hint_text(hint_count), strike_count, get_strike_text(strike_count))

@assist.action('welcome-greeting')
def welcome_greeting():
    speech_options = ["Welcome to 'One, Two, Cow!  The game where the number after 16 happens to be...llama! Would you like to hear the rules or start a game?",
                      "Welcome to 'One, Two, Cow!  The counting game where numbers morph into animals! Would you like to hear the rules or start a game?",
                      "Welcome to 'One, Two, Cow!  A counting game that swaps out numbers with your favorite animals! Would you like to hear the rules or start a game?"]

    context_manager.add("choose_game_or_rules", lifespan=5)

    return ask(choice(speech_options))

@assist.context("choose_game_or_rules")
@assist.action("start-game")
def start_new_game():
	"""Prepares a new game of One, Two, Cow for the user."""

	game = Game()
	game.start_game(3)
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
	speech = game.start_round()
	save_game(game)
	return ask(speech)

@assist.context("game_in_progress", "guess")
@assist.action("user-guess", mapping={'user_guess': 'sys.any'})
def evaluate_guess(user_guess, game):
	"""Evaluates a guess from user for a game that is in progress."""

	game = load_game()
	correct_answer = game.get_correct_answer()
	if game.is_guess_correct(user_guess, correct_answer):	
		return correct_guess(game)
	else:
		return incorrect_guess(game, correct_answer)

def incorrect_guess(game, correct_answer):

	speech_options_incorrect = ["Oh no! That is not correct! The correct answer was: {}.".format(correct_answer),
	                            "Uh oh! That wasn't correct! The correct answer was: {}.".format(correct_answer),
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

	speech_options = ["That's correct! What is your next guess?",
	                  "Right answer! What is your next guess?",
	                  "Nice job! Now what comes next?"]

	if game.round_count == game.max_count and game.guess_count == game.max_count and not game.strike_in_progress:
		save_game(game)
		return event("won_game")
	elif game.guess_count == game.max_count and not game.strike_in_progress:
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
		speech = "Okay, here's your hint. {} Now, what is your guess?".format(game.use_hint(game.get_correct_answer()))
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
	speech_options = ["Oh meow! Looks like you ran out of strikes!",
	                  "Oh, the hue-manatee! You're out of strikes!"]
	speech = choic(speech_options) + " Would you like to start a new game or hear about the rules?"
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
	
	#game = load_game()
	#game.end_game()
	speech = "Oh meow! Ok let's end the game right here. Would you like to start a new game or hear about the rules?"
	context_manager.add("choose_game_or_rules", lifespan=3)
	return ask(speech)

if __name__ == '__main__':
    app.run(debug=True)

