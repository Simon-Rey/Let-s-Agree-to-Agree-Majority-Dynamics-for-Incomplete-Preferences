from data_generation import *
from maj_dynamics import *
from experiment import *
from plot import *

# Returns a generator for random profiles
def randomProfiles(numAgents, numAlts, numProfiles):
	for i in range(numProfiles):
		yield profile_generation(numAgents, numAlts)

# Useless function to just get the right number of arguments to plug it in the experiment functions
def allProfiles(numAgents, numAlts, numProfiles):
	return getAllProfiles(numAgents, numAlts)

# dataManipulation = runManipulationExperiment(11, 20000)
# (dataNumAgents, dataCompleteness) = runFrequencyExperiment(25, 5000000, numAgentsMin = 17)

dataNumAgents = pd.read_pickle("frequencyNumAgentsData_5000000_25.pkl")
dataCompleteness = pd.read_pickle("frequencyCompletenessData_5000000_25.pkl")
dataManipulation = pd.read_pickle("manipulationData_allOrders_20000.pkl")

frequencyNumAgentsPlot(dataNumAgents, 5, criterias = [majUndom, plurUndom, condorcet], fileName = "Plots/finalFreqNumAgents.pdf")
frequencyCompletenessPlot(dataCompleteness, 15, 5, criterias = [majUndom, plurUndom, condorcet], fileName = "Plots/finalFreqCompleteness.pdf")
manipulationPlot(dataManipulation, criterias = [majUndom, plurUndom, condorcet], fileName = "Plots/finalManipulation.pdf")

generateFrequencyNumAgentsPlots(dataNumAgents, 5)
generateFrequencyCompletenessPlots(dataCompleteness, 15, 5)
generateManipulationPlots(dataManipulation)