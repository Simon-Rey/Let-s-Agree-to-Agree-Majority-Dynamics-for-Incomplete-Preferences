import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

import matplotlib

from maj_dynamics import *

# Renaming the criteria
def criteriaName(criteria):
	if criteria == "condorcet":
		return "Condorcet Winner"
	if criteria == "unanDominant":
		return "Unanimity Dominant"
	if criteria == "majDominant":
		return "Majority Dominant"
	if criteria == "plurDominant":
		return "Plurality Dominant"
	if criteria == "plurUndom":
		return "Plurality Undominated"
	if criteria == "unanUndom":
		return "Unanimity Undominated"
	if criteria == "majUndom":
		return "Majority Undominated"

# Renaming the effect of the majority dynamics
def effectName(effect):
	if effect == "Good":
		return "Generating Consensus"
	if effect == "Ok":
		return "Preserving Consensus"
	if effect == "Bad":
		return "Preserving Absence of Cons."
	if effect == "Terrible":
		return "Losing Consensus"

# Plots the frequency of each effect based on the number of agents
def frequencyNumAgentsPlot(data, numAlts, criteria = None, criterias = None, fileName = None):
	plt.close('all')

	sns.set_theme()

	data = data.copy(deep = True)

	if criteria != None:
		criterias = [criteria.__name__]
	elif criterias == None:
		criterias = data["criteria"].unique()
	else:
		criterias = [c.__name__ for c in criterias]

	data = data[data["criteria"].isin(criterias)]

	data["criteria"] = data["criteria"].map(criteriaName)
	data["effect"] = data["effect"].map(effectName)
	data["frequency"] *= 100

	g = sns.catplot(
		data = data,
		kind = "point",
		x = "numAgents",
		y = "frequency",
		hue = "effect",
		markers = ["d", "*", "s"] + ["o" for c in criterias],
		linestyles = ["dashed", "dotted", "dashdot", "solid"] + ["-" for c in criterias],
		col = "criteria" if len(criterias) > 1 else None, 
		col_wrap = 4 if len(criterias) > 1 else None,
		col_order = [criteriaName(c) for c in ["unanDominant", "majDominant", "plurDominant", "condorcet",
			"unanUndom", "majUndom", "plurUndom"] if c in criterias] if len(criterias) > 1 else None,
		palette = ['#a1c9f4', '#ffb482', '#8de5a1', '#fab0e4', '#debb9b', '#d0bbff', '#ff9f9b', 
			'#cfcfcf', '#fffea3', '#b9f2f0'],
		legend = False,
		height = 3.5,
	)
	
	g.set_axis_labels("Number of Agents", "Frequency of Occurence (%)")
	g.set_titles("{col_name}")
	
	for ax in g.axes.flatten():
		ax.tick_params(labelbottom = True)

	plt.legend(bbox_to_anchor = (1.95, 0.75), title = "Effect on Consensus")
	# plt.legend(bbox_to_anchor = (1.02, 0.75), title = "Effect on Consensus")
	
	if fileName != None:
		plt.savefig(fileName, bbox_inches = 'tight', dpi = 600)
	else:
		plt.show()

# Generates all the plots based on the number of agents for all criteria
def generateFrequencyNumAgentsPlots(data, numAlts):
	frequencyNumAgentsPlot(data, numAlts, fileName = "Plots/frequencyNumAgentsAll.pdf")
	for criteria in [condorcet, unanDominant, majDominant, plurDominant, plurUndom, unanUndom, majUndom]:
		frequencyNumAgentsPlot(data, numAlts, criteria = criteria, fileName = "Plots/frequencyNumAgents" + criteria.__name__ + ".pdf")

# Plots the frequency of each effect based on the completeness level of the profile
def frequencyCompletenessPlot(data, numAgents, numAlts, criteria = None, criterias = None, fileName = None, binSize = 5):
	plt.close('all')

	sns.set_theme()

	data = data.copy(deep = True)

	data = data[data["numAgents"] == numAgents]

	if criteria != None:
		criterias = [criteria.__name__]
	elif criterias == None:
		criterias = data["criteria"].unique()
	else:
		criterias = [c.__name__ for c in criterias]

	data = data[data["criteria"].isin(criterias)]

	data["criteria"] = data["criteria"].map(criteriaName)
	data["effect"] = data["effect"].map(effectName)

	# Making categories
	newData = {}
	norm = {}
	for line in data.iterrows():
		line = line[1]
		completenessCat = round((100 * line["completeness"]) / binSize) * binSize
		effect = line["effect"]
		crit = line["criteria"]
		if (completenessCat, crit, effect) in newData:
			newData[(completenessCat, crit, effect)]["frequency"] += line["frequency"]
		else:
			newData[(completenessCat, crit, effect)] = {"frequency": line["frequency"], "completeness": completenessCat, "effect": effect, "criteria": crit}
		if effect in ["Generating Consensus", "Preserving Absence of Cons."]:
			if (completenessCat, crit, "noInitConsensus") in norm:	
				norm[(completenessCat, crit, "noInitConsensus")] += line["frequency"]
			else:
				norm[(completenessCat, crit, "noInitConsensus")] = line["frequency"]
		else:
			if (completenessCat, crit, "initConsensus") in norm:	
				norm[(completenessCat, crit, "initConsensus")] += line["frequency"]
			else:
				norm[(completenessCat, crit, "initConsensus")] = line["frequency"]

	for key, value in newData.items():
		if key[2] in ["Generating Consensus", "Preserving Absence of Cons."]:
			if norm[(key[0], key[1], "noInitConsensus")] > 0:
				value["frequency"] /= norm[(key[0], key[1], "noInitConsensus")]
		else:
			if norm[(key[0], key[1], "initConsensus")] > 0:
				value["frequency"] /= norm[(key[0], key[1], "initConsensus")]

	data = pd.DataFrame([d for _, d in newData.items()])

	data["frequency"] *= 100

	g = sns.catplot(
		data = data,
		kind = "point",
		x = "completeness",
		y = "frequency",
		hue = "effect",
		markers = ["d", "*", "s"] + ["o" for c in criterias],
		linestyles = ["dashed", "dotted", "dashdot", "solid"] + ["-" for c in criterias],
		col = "criteria" if len(criterias) > 1 else None, 
		col_wrap = 4 if len(criterias) > 1 else None,
		col_order = [criteriaName(c) for c in ["unanDominant", "majDominant", "plurDominant", "condorcet",
			"unanUndom", "majUndom", "plurUndom"] if c in criterias] if len(criterias) > 1 else None,
		palette = ['#a1c9f4', '#ffb482', '#8de5a1', '#fab0e4', '#debb9b', '#d0bbff', '#ff9f9b', 
			'#cfcfcf', '#fffea3', '#b9f2f0'],
		legend = False,
		height = 3.5,
	)
	
	g.set_axis_labels("Level of Completeness (%)", "Frequency of Occurence (%)")
	g.set_titles("{col_name}")
	complenessLevels = sorted(list(data["completeness"].unique()))
	xticks = ["" for l in complenessLevels]
	xticks[0] = complenessLevels[0]
	xticks[-1] = complenessLevels[-1]
	xticks[int(len(complenessLevels) / 3)] = complenessLevels[int(len(complenessLevels) / 3)]
	xticks[int(2 * len(complenessLevels) / 3)] = complenessLevels[int(2 * len(complenessLevels) / 3)]
	g.set_xticklabels(xticks)
	
	for ax in g.axes.flatten():
		ax.tick_params(labelbottom = True)

	plt.legend(bbox_to_anchor = (1.95, 0.75), title = "Effect on Consensus")
	# plt.legend(bbox_to_anchor = (1.02, 0.75), title = "Effect on Consensus")
	
	if fileName != None:
		plt.savefig(fileName, bbox_inches = 'tight')
	else:
		plt.show()

# Generates all the plots based on completeness level for all criteria
def generateFrequencyCompletenessPlots(data, numAgents, numAlts):
	frequencyCompletenessPlot(data, numAgents, numAlts, fileName = "Plots/frequencyCompletenessAll.pdf")
	for criteria in [condorcet, unanDominant, majDominant, plurDominant, plurUndom, majUndom, unanUndom]:
		frequencyCompletenessPlot(data, numAgents, numAlts, criteria = criteria, fileName = "Plots/frequencyCompleteness" + criteria.__name__ + ".pdf")

# Renaming the manipulation effect
def manipulationName(manipulationType):
	if manipulationType == "consensusPreservation":
		return "Preserving Consensus"
	if manipulationType == "identityPreservation":
		return "Preserving Identity"
	if manipulationType == "identityDestruction":
		return "Losing Identity"
	if manipulationType == "specificConsensus":
		return "Choosing the Consensus"
	if manipulationType == "consensusDestruction":
		return "Losing Consensus"
	if manipulationType == "consensusCreation":
		return "Generating Consensus"
	if manipulationType == "noConsensusPreservation":
		return "Preserving Absence of Consensus"

# Plots the frequency of each type of manipulation
def manipulationPlot(data, criteria = None, criterias = None, fileName = None):
	plt.close('all')

	sns.set_theme()

	data = data.copy(deep = True)

	if criteria != None:
		criterias = [criteria.__name__]
	elif criterias == None:
		criterias = data["criteria"].unique()
	else:
		criterias = [c.__name__ for c in criterias]

	data = data[data["criteria"].isin(criterias)]

	data["criteria"] = data["criteria"].map(criteriaName)
	data["manipulationType"] = data["manipulationType"].map(manipulationName)
	data["frequency"] *= 100

	g = sns.catplot(
		data = data,
		kind = "bar",
		x = "frequency",
		y = "manipulationType",
		order = ["Preserving Consensus", "Preserving Identity", "Losing Consensus", "Losing Identity", 
		"Generating Consensus", "Preserving Absence of Consensus", "Choosing the Consensus"],
		col = "criteria" if len(criterias) > 1 else None, 
		col_wrap = 4 if len(criterias) > 1 else None,
		col_order = [criteriaName(c) for c in ["unanDominant", "majDominant", "plurDominant", "condorcet",
			"unanUndom", "majUndom", "plurUndom"] if c in criterias] if len(criterias) > 1 else None,
		palette = ['#a1c9f4', '#ffb482', '#8de5a1', '#fab0e4', '#debb9b', '#d0bbff', '#ff9f9b', 
			'#cfcfcf', '#fffea3', '#b9f2f0'],
		edgecolor = ".6",
		legend = False,
		height = 3.5,
	)
	
	g.set_axis_labels("Frequency of Occurence (%)", "")#"Type of Manipulation")
	g.set_titles("{col_name}")
	
	for ax in g.axes.flatten():
		ax.tick_params(labelbottom = True)

	# plt.legend(bbox_to_anchor = (1.02, 0.75), title = "Effect on Consensus")
	
	if fileName != None:
		plt.savefig(fileName, bbox_inches = 'tight', dpi = 600)
	else:
		plt.show()

# Generates all the manipulation plots
def generateManipulationPlots(data):
	manipulationPlot(data, fileName = "Plots/manipulationAll.pdf")
	for criteria in [condorcet, unanDominant, majDominant, plurDominant, plurUndom, majUndom, unanUndom]:
		manipulationPlot(data, criteria = criteria, fileName = "Plots/manipulation" + criteria.__name__ + ".pdf")