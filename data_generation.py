from itertools import product

import random
import dill

import numpy as np

# Returns True or False depending on whether the preference given in input satisfies 
# transitivity or not
def check_transitivity(pref):
	for k in range(0, len(pref)):
		for q in range(0, len(pref)):
			for r in range(0, len(pref)):
				if pref[k][q] == 1 and pref[q][r] == 1:
					if pref[k][r] != 1:
						return False
	return True

# Returns a symmetric version of the preference given in input
def fix_symmetry_diagonal(pref):
	fixed_pref = pref
	for q in range(0, len(pref)):
		for j in range(0, len(pref)):
			if j > q:
				fixed_pref[q][j] = -pref[j][q]
			elif j == q:
				fixed_pref[q][j] = 0
	return fixed_pref

# Randomly generates incomplete preference with alt_number alternatives
def generate_incomplete_random_preference(alt_number):
	random_pref = np.random.randint(-1, 2, (alt_number, alt_number))
	some_pref = fix_symmetry_diagonal(random_pref)
	while not check_transitivity(some_pref):
		random_pref = np.random.randint(-1, 2, (alt_number, alt_number))
		some_pref = fix_symmetry_diagonal(random_pref)
	return some_pref

# Randomly generates a profile of incomplete preferences with n voters and m alternatives
def profile_generation(n, m):
	vot_number = n
	alt_number = m
	profile = []
	for _ in range(vot_number):
		some_pref = generate_incomplete_random_preference(alt_number)
		profile.append(some_pref)
	return profile

# Generates all incomplete preferences with numAlts alternatives by looping through all possible 
# completions of the triangle below the diagonal in the matrix representing the preferences
def getAllBallots(numAlts):
	lenLowerDiagonal = int(numAlts * (numAlts - 1) / 2)
	for lowerDiagonal in product([-1, 0, 1], repeat = lenLowerDiagonal):
		ballot = np.zeros((numAlts, numAlts))
		k = 0
		for i in range(numAlts):
			for j in range(i):
				ballot[i][j] = lowerDiagonal[k]
				k += 1
		ballot = fix_symmetry_diagonal(ballot)
		if check_transitivity(ballot):
			yield ballot

# Returns all the profiles with numVoters voters and numAlts alternatives
def getAllProfiles(numVoters, numAlts):
	return product(getAllBallots(numAlts), repeat = numVoters)