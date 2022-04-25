import numpy as np

import copy
import sys

from data_generation import check_transitivity
from functools import reduce

# The actual majority dynamics process, update the profile prof given the update order order
def update(prof, order):
	majority_pref = reduce(np.add, prof)
	new_prof = copy.deepcopy(prof)
	alt_number = len(prof[0])
	vot_number = len(prof)
	for pair in order:  # pair is an ordered pair of alternatives
		for x in range(0, vot_number):
			if new_prof[x][pair[0]][pair[1]] == 0:
				if majority_pref[pair[0]][pair[1]] >= 0:
					new_prof[x][pair[0]][pair[1]] = 1
					new_prof[x][pair[1]][pair[0]] = -1
				else:
					new_prof[x][pair[0]][pair[1]] = -1
					new_prof[x][pair[1]][pair[0]] = 1
				done = False
				while not done:
					done = True
					for k in range(0, alt_number):
						for q in range(0, alt_number):
							for r in range(0, alt_number):
								if new_prof[x][k][q] == 1 and new_prof[x][q][r] == 1 and new_prof[x][k][r] < 1:
									new_prof[x][k][r] = 1
									new_prof[x][r][k] = -1
									done = False
		majority_pref = reduce(np.add, new_prof)
	return new_prof

# Returns a tuple (Boolean, Winner) with Boolean indicating whether a Condorcet winner exists in the 
# profile prof and Winner the actual Condorcet winner (or None if none exists)
def condorcet(prof):
	alt_number = len(prof[0])
	gen_majority_pref = reduce(np.add, prof)
	for i in range(0, alt_number):
		condorcet_winner = True
		for j in range(0, alt_number):
			if i != j:
				if gen_majority_pref[i][j] <= 0:
					condorcet_winner = False
					break
		if condorcet_winner:
			return (True, i)
	return (False, None)

# Returns a score vector for a given ballot in which a 0 at an alternative position indicates that the alternative
# is beaten by at least one other, and a 1 indicates that it is never beaten
def individual_one_approval_scores(preference):
	alt_number = len(preference)
	scores = []
	for i in range(0, alt_number):
		score = 1
		for j in range(0, alt_number):
			if preference[i][j] == -1:
				score = 0
				break
		scores.append(score)
	return scores

# Returns a score vector for a profile in which the number at an alternative position indicates the number
# of ballot in which the alternative is never beaten
def total_one_approval_scores(profile): 
	scores = []
	for i in range(0, len(profile[0])):
		score = 0
		for j in range(0, len(profile)):
			score = score + individual_one_approval_scores(profile[j])[i]
		scores.append(score)
	return scores

# Returns the alternatives with the highest number of ballots in which they are never beaten
def one_approval_winner(profile):
	totalScores = total_one_approval_scores(profile)
	winning_score = np.max(totalScores)
	winners = []
	for i in range(0, len(profile[0])):
		if totalScores[i] == winning_score:
			winners.append(i)
	return winners

# Returns the alternatives that are never beaten in all the ballots
def one_approval_top(profile):
	winning_score = len(profile)
	totalScores = total_one_approval_scores(profile)
	winners = []
	for i in range(0, len(profile[0])):
		if totalScores[i] == winning_score:
			winners.append(i)
	return winners

# Returns the alternatives that are never beaten in a majority of ballots
def one_approval_maj(profile):
	winning_score = len(profile) / 2
	totalScores = total_one_approval_scores(profile)
	winners = []
	for i in range(0, len(profile[0])):
		if totalScores[i] > winning_score:
			winners.append(i)
	return winners

# Returns True if the alternative is dominant in the ballot preference
def is_dominant(preference, alternative):
	for i in range(0, len(preference)):
		if i != alternative:
			if preference[alternative][i] != 1:
				return False
	return True

# Returns a tuple (Boolean, Winner) with Boolean indicating whether a UnanDominant winner exists in the 
# profile prof and Winner the actual UnanDominant winner (or None if none exists)
def unanDominant(profile):
	for i in range(0, len(profile[0])):
		this_is_dominant = True
		for n in range(0, len(profile)):
			if not is_dominant(profile[n], i):
				this_is_dominant = False
		if this_is_dominant:
			return (True, i)
	return (False, None)

# Returns a tuple (Boolean, Winner) with Boolean indicating whether a MajDominant winner exists in the 
# profile prof and Winner the actual MajDominant winner (or None if none exists)
def majDominant(profile):
	alt_number = len(profile[0])
	vot_number = len(profile)
	for i in range(0, alt_number):
		dominance_number = 0
		for n in range(0, vot_number):
			if is_dominant(profile[n], i):
				dominance_number += 1
		if dominance_number > vot_number / 2:
			return (True, i)
	return (False, None)

# Returns a tuple (Boolean, Winner) with Boolean indicating whether a unique PlurDominant winner exists in the 
# profile prof and Winner the actual unique PlurDominant winner (or None if none exists)
def plurDominant(profile):
	alt_number = len(profile[0])
	dominances = []
	for i in range(alt_number):
		dominance_number = 0
		for n in range(0, len(profile)):
			if is_dominant(profile[n], i):
				dominance_number += 1
		dominances.append(dominance_number)
	winning_score = np.max(dominances)
	winners = []
	for i in range(alt_number):
		if dominances[i] == winning_score and winning_score != 0:
			winners.append(i)
	if len(winners) == 1:
		return (True, winners[0])
	return (False, winners)

# Returns a tuple (Boolean, Winner) with Boolean indicating whether a unique PlurUndom winner exists in the 
# profile prof and Winner the actual unique PlurUndom winner (or None if none exists)
def plurUndom(profile):
	appWinners = one_approval_winner(profile)
	if len(appWinners) == 1:
		return (True, appWinners[0])
	return (False, None)

# Returns a tuple (Boolean, Winner) with Boolean indicating whether a unique UnanUndom winner exists in the 
# profile prof and Winner the actual unique UnanUndom winner (or None if none exists)
def unanUndom(profile):
	unanWinners = one_approval_top(profile)
	if len(unanWinners) == 1:
		return (True, unanWinners[0])
	return (False, None)

# Returns a tuple (Boolean, Winner) with Boolean indicating whether a unique MajUndom winner exists in the 
# profile prof and Winner the actual unique MajUndom winner (or None if none exists)
def majUndom(profile):
	majWinners = one_approval_maj(profile)
	if len(majWinners) == 1:
		return (True, majWinners[0])
	return (False, None)