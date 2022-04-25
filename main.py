from data_generation import *
from maj_dynamics import *
from experiments import *
from plot import *

# Returns a generator for random profiles
def randomProfiles(numAgents, numAlts, numProfiles):
	for i in range(numProfiles):
		yield profile_generation(numAgents, numAlts)

# Useless function to just get the right number of arguments to plug it in the experiment functions
def allProfiles(numAgents, numAlts, numProfiles):
	return getAllProfiles(numAgents, numAlts)

##### TO CREATE EXPERIMENTS DATA

# dataManipulation = runManipulationExperiment(11, 20000)
# (dataNumAgents, dataCompleteness) = runFrequencyExperiment(25, 5000000, numAgentsMin = 17)

##### READ EXPERIMENT DATA AND GENERATE THE FINAL PLOTS

dataNumAgents = pd.read_pickle("expeData/frequencyNumAgentsData_5000000_25.pkl")
dataCompleteness = pd.read_pickle("expeData/frequencyCompletenessData_5000000_25.pkl")
dataManipulation = pd.read_pickle("expeData/manipulationData_allOrders_20000.pkl")

frequencyNumAgentsPlot(dataNumAgents, 5, criterias = [majUndom, plurUndom, condorcet], fileName = "Plots/finalFreqNumAgents.pdf")
frequencyCompletenessPlot(dataCompleteness, 15, 5, criterias = [majUndom, plurUndom, condorcet], fileName = "Plots/finalFreqCompleteness.pdf")
manipulationPlot(dataManipulation, criterias = [majUndom, plurUndom, condorcet], fileName = "Plots/finalManipulation.pdf")

##### TO GENERATE ALL THE PLOTS

# generateFrequencyNumAgentsPlots(dataNumAgents, 5)
# generateFrequencyCompletenessPlots(dataCompleteness, 15, 5)
# generateManipulationPlots(dataManipulation)