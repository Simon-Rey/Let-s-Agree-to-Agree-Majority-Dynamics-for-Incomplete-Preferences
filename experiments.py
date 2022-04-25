from data_generation import *
from maj_dynamics import *
from plot import *

from itertools import chain, combinations, permutations
from multiprocessing import Pool
from copy import deepcopy

import pandas as pd

import time

# The list of all the criteria
def criteriaList():
	return [condorcet, unanDominant, majDominant, plurDominant, plurUndom, unanUndom, majUndom]

# The list of all the effects
def effectList():
	return ["Good", "Ok", "Bad", "Terrible"]

# Computes the completeness score of a profile
def proportionCompleteness(profile):
	res = 0
	numAlts = len(profile[0][0])
	normalisation = 0
	for ballot in profile:
		for i in range(numAlts):
			for j in range(i + 1, numAlts):
				normalisation += 1
				if ballot[i][j] in [-1, 1]:
					res += 1
	normalisation = max(1, normalisation)
	return res / normalisation

# Compute the disagreement score of a profile
def proportionDisagreement(profile):
	res = 0
	numAgents = len(profile)
	numAlts = len(profile[0][0])
	normalisation = 0
	for i1 in range(numAgents):
		for i2 in range(i1 + 1, numAgents):
			for j1 in range(numAlts):
				for j2 in range(j1 + 1, numAlts):
					normalisation += 1
					if profile[i1][j1][j2] != profile[i2][j1][j2]:
						res += 1
	normalisation = max(1, normalisation)
	return res / normalisation

# The main function for the experiment about the frequency of each effects
def frequencyExperiment(numAgents, numAlts, numTry, profileFunction):
	# Initialize dictionnary for the frequency depending on the number of agents
	resFrequencyAgents = {(numAgents, criteria.__name__, effect): 0
		for criteria in criteriaList() for effect in effectList()}
	# Initialize dictionnary for the frequency depending on the completeness level of the profile
	resFrequencyCompleteness  = {}
	distinctFrequencyLevel = set()

	print((numAgents, numAlts, numTry))
	
	updateOrder = [(i, j) for i in range(numAlts) for j in range(i + 1, numAlts)]
	
	for profile in profileFunction(numAgents, numAlts, numTry):
		
		# Compute completeness level, if it's a new value, initialize the corresponding dictionnary
		completenessLevel = proportionCompleteness(profile)
		if completenessLevel not in distinctFrequencyLevel:
			distinctFrequencyLevel.add(completenessLevel)
			for criteria in criteriaList():
				for effect in effectList():
					resFrequencyCompleteness[(numAgents, criteria.__name__, completenessLevel, effect)] = 0

		# Profile after the dynamics				
		finalProfile = update(profile, updateOrder)
		
		for criteria in criteriaList():

			# Compute consensus before and after and update the frequency accordingly
			consensusBefore = criteria(profile)[0]
			consensusAfter = criteria(finalProfile)[0]
			if consensusBefore and consensusAfter:
				resFrequencyAgents[(numAgents, criteria.__name__, "Ok")] += 1
				resFrequencyCompleteness[(numAgents, criteria.__name__, completenessLevel, "Ok")] += 1
			elif consensusBefore and not consensusAfter:
				resFrequencyAgents[(numAgents, criteria.__name__, "Terrible")] += 1
				resFrequencyCompleteness[(numAgents, criteria.__name__, completenessLevel, "Terrible")] += 1
			elif not consensusBefore and consensusAfter:
				resFrequencyAgents[(numAgents, criteria.__name__, "Good")] += 1
				resFrequencyCompleteness[(numAgents, criteria.__name__, completenessLevel, "Good")] += 1
			elif not consensusBefore and not consensusAfter:
				resFrequencyAgents[(numAgents, criteria.__name__, "Bad")] += 1
				resFrequencyCompleteness[(numAgents, criteria.__name__, completenessLevel, "Bad")] += 1

	return (resFrequencyAgents, resFrequencyCompleteness)

# The function that is called for the pool of processes for the experiment about the frequency of each effect
def frequencyPoolFunction(numAgentsTry):
	(numAgents, numTry) = numAgentsTry
	numAlts = 5
	return frequencyExperiment(numAgents, numAlts, numTry, randomProfiles)

# Runs the experiments about the frequency of each effect in a pool of processes
def runFrequencyExperiment(numAgentsMax, numTryMax, numAgentsMin = 1):
	startingTime = time.time()
	pool = Pool()

	resFrequencyAgents = {}
	resFrequencyCompleteness = {}
	
	tryPerWorker = 100
	for res in pool.imap_unordered(frequencyPoolFunction, [(numAgents, tryPerWorker) for numAgents in range(numAgentsMin, numAgentsMax + 1, 2) for i in range(int(numTryMax / tryPerWorker))]):
		for key, frequency in res[0].items():
			if key in resFrequencyAgents:
				resFrequencyAgents[key] += frequency
			else:
				resFrequencyAgents[key] = frequency

		for key, frequency in res[1].items():
			if key in resFrequencyCompleteness:
				resFrequencyCompleteness[key] += frequency
			else:
				resFrequencyCompleteness[key] = frequency

	pool.close()

	for numAgents in range(numAgentsMin, numAgentsMax + 1, 2):
		for criteria in criteriaList():
			norm = sum(resFrequencyAgents[(numAgents, criteria.__name__, effect)] for effect in ["Ok", "Terrible"])
			if norm > 0:
				for effect in ["Ok", "Terrible"]:
					resFrequencyAgents[(numAgents, criteria.__name__, effect)] /= norm
			norm = sum(resFrequencyAgents[(numAgents, criteria.__name__, effect)] for effect in ["Bad", "Good"])
			if norm > 0:
				for effect in ["Bad", "Good"]:
					resFrequencyAgents[(numAgents, criteria.__name__, effect)] /= norm

	dataNumAgents = pd.DataFrame([{"numAgents": k[0], "criteria": k[1], "effect": k[2], "frequency": v} for k, v in resFrequencyAgents.items()])
	dataNumAgents.to_pickle("frequencyNumAgentsData.pkl")
	
	dataCompleteness = pd.DataFrame([{"numAgents": k[0], "criteria": k[1], "completeness": k[2], "effect": k[3], "frequency": v} for k, v in resFrequencyCompleteness.items()])
	dataCompleteness.to_pickle("frequencyCompletenessData.pkl")
	
	print("Done in {} seconds.".format(time.time() - startingTime))
	
	return (dataNumAgents, dataCompleteness)

# Returns the powerset of an iterable
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

# Returns a generator for all update orders given a number of alternatives
def allUpdateOrders(numAlts):
	baseOrder = [tuple(pair) for pair in combinations(range(numAlts), 2)]
	for subset in powerset(range(len(baseOrder))):
		newOrder = deepcopy(baseOrder)
		for index in subset:
			newOrder[index] = (baseOrder[index][1], baseOrder[index][0])
		for perm in permutations(newOrder):
			yield perm

# Returns a generator for all permutations of the basic order (i.e., with fixed tie-breaking) 
def allUpdateOrdersFixedTieBreaking(numAlts):
	baseOrder = [tuple(pair) for pair in combinations(range(numAlts), 2)]
	for perm in permutations(baseOrder):
		yield perm

# The main function for the experiment about manipulation
def manipulationExperiment(numAgents, numAlts):
	res = {(c.__name__, manipulationType): 0 for manipulationType in ["consensusPreservation", "identityPreservation", 
		"identityDestruction", "specificConsensus", "consensusDestruction", "consensusCreation", 
		"noConsensusPreservation"] for c in criteriaList()}

	profile = profile_generation(numAgents, numAlts)

	allConsensusBefore = {criteria.__name__: criteria(profile) for criteria in criteriaList()}

	# for updateOrder in allUpdateOrdersFixedTieBreaking(numAlts):
	for updateOrder in allUpdateOrders(numAlts):
		finalProfile = update(profile, updateOrder)

		for criteria in criteriaList():

			consensusBefore = allConsensusBefore[criteria.__name__]
			consensusAfter = criteria(finalProfile)

			if consensusBefore[0] and consensusAfter[0]:
				res[(criteria.__name__, "consensusPreservation")] = 1
				if consensusBefore[1] == consensusAfter[1]:
					res[(criteria.__name__, "identityPreservation")] = 1
				else:
					res[(criteria.__name__, "identityDestruction")] = 1
					if consensusAfter[1] == 0:
						res[(criteria.__name__, "specificConsensus")] = 1
			elif consensusBefore[0] and not consensusAfter[0]:
				res[(criteria.__name__, "consensusDestruction")] = 1
				res[(criteria.__name__, "identityDestruction")] = 1
			elif not consensusBefore[0] and consensusAfter[0]:
				res[(criteria.__name__, "consensusCreation")] = 1
				if consensusAfter[1] == 0:
					res[(criteria.__name__, "specificConsensus")] = 1
			elif not consensusBefore[0] and not consensusAfter[0]:
				res[(criteria.__name__, "noConsensusPreservation")] = 1

	return (res, {criteria.__name__: allConsensusBefore[criteria.__name__][0] for criteria in criteriaList()})

# The function that is called for the pool of processes for the manipulation experiment
def manipulationPoolFunction(numAgents):
	numAlts = 4
	return manipulationExperiment(numAgents, numAlts)

# Runs the manipulation experiment with a pool of processes
def runManipulationExperiment(numAgents, numTryMax):
	startingTime = time.time()
	pool = Pool()

	res = {}
	norm = {c.__name__: {"consensusBefore": 0, "notConsensusBefore": 0} for c in criteriaList()}

	i = 0
	for r in pool.imap_unordered(manipulationPoolFunction, [numAgents for i in range(numTryMax)]):
		i += 1
		if i % (numTryMax / 1000) == 0:
			print(i)
		for key, frequency in r[0].items():
			if key in res:
				res[key] += frequency
			else:
				res[key] = frequency
		for criteria in criteriaList():
			if r[1][criteria.__name__]:
				norm[criteria.__name__]["consensusBefore"] += 1
			else:
				norm[criteria.__name__]["notConsensusBefore"] += 1

	pool.close()

	for criteria in criteriaList():
		for manipulationType in ["consensusPreservation", "identityPreservation", "identityDestruction", "consensusDestruction"]:
			if norm[criteria.__name__]["consensusBefore"] > 0:
				res[(criteria.__name__, manipulationType)] /= norm[criteria.__name__]["consensusBefore"]
		for manipulationType in ["consensusCreation", "noConsensusPreservation"]:
			if norm[criteria.__name__]["notConsensusBefore"] > 0:
				res[(criteria.__name__, manipulationType)] /= norm[criteria.__name__]["notConsensusBefore"]
		res[(criteria.__name__, "specificConsensus")] /= norm[criteria.__name__]["consensusBefore"] + norm[criteria.__name__]["notConsensusBefore"]

	data = pd.DataFrame([{"manipulationType": k[1], "criteria": k[0], "frequency": v} for k, v in res.items()])
	data.to_pickle("manipulationData.pkl")
	
	print("Done in {} seconds.".format(time.time() - startingTime))
	
	return data