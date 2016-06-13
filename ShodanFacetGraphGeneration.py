###
# - By Ketil.dk 
# - 
# - I wanted to get a better understanding of the usage of a API, so shodan seemed like a great place to start.
# - ShodanFacetBarGeneration.py takes a search chriteria and generates graphs and shares a bit of data
# - You can give it common shodan search chriteria like net:x.x.x.0/24  or search for a technology like apache, synology, IIS or the like
###


###------IMPORTS

#shodan api
import shodan

#System API
import sys

#os api (creating folders)
import os

#matlip plot related apis libs
import numpy as np
import matplotlib.pyplot as plt

#for piechart
from pylab import *

#import shutil for svg copy to target folder
from shutil import copyfile

#Import yaml support so we can store the config in config.yml
#Consider using configparser instead https://martin-thoma.com/configuration-files-in-python/
import yaml



###------CODE STUFF

#Import config.yml as object cfg
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#Shodan API key
API_KEY = cfg["Settings"]["apikey"]


#lists for port facet content
Portlabels = []
ports = []

#lists for org facet content
OrgName = []
OrgAmount = []

#lists for country facet content
CountryCode = []
CountryFacetAmount =[] 
ColorData = []
ColorPercentageValues = []


FACETS = [('org',10),('port',5),('country', 10)]
FACET_TITLES = {'org': 'Top 10 Organizations','port': 'Top 5 Ports','country': 'Top 20 Countries'}

if len(sys.argv) == 1:
    print 'Usage: %s <search query>' % sys.argv[0]
    sys.exit(1)

def max(list):
        max = list[0]
        for elm in list[1:]:
                if elm > max:
                        max = elm
        return max

def percentage(part, whole):
  return 100 * float(part)/float(whole)


try:
    api = shodan.Shodan(API_KEY)
    query = ' '.join(sys.argv[1:])
    result = api.count(query, facets=FACETS)

    print 'Shodan Summary Information'
    print 'Query: %s' % query
    print 'Total Results: %s\n' % result['total']

    for facet in result['facets']:
        print FACET_TITLES[facet]
        for term in result['facets'][facet]:
            print '%s: %s' % (term['value'], term['count'])

	    #Fill port lists for chart
	    if str(facet) == "port":
		Portlabels.append(term['value'])
		ports.append(term['count'])

            #Fill port lists for chart
            if str(facet) == "org":
                OrgName.append(term['value'])
                OrgAmount.append(term['count'])

            #Fill port lists for chart
            if str(facet) == "country":
                CountryCode.append(term['value'])
                CountryFacetAmount.append(term['count'])
        print ''

except Exception, e:
    print 'Error: %s' % e
    sys.exit(1)


#Create Port Pie Chart
fig = figure(1)

ax = fig.add_subplot(211)
#ax = axes([0.1, 0.1, 0.8, 0.8])
pie(ports,labels=Portlabels, autopct='%1.1f%%', shadow=True)
title('Top 5: ' +str(' '.join(sys.argv[1:]))+ ' port distribution', bbox={'facecolor':'0.8', 'pad':5})

#Create Organizational
plt.subplot(212)
width = .35
ind = np.arange(len(OrgAmount))
plt.bar(ind, OrgAmount)
plt.xticks(ind + width / 2, OrgName)
fig.autofmt_xdate()
plt.title("Organizations by open ports: " +  str(' '.join(sys.argv[1:])))
plt.show()


#Per Country Distribution
#Assign colour values to a given country based on CountryFacetAmount
print "Generate BlankMap-ColorCSS" + " for map"
dictionary = dict(zip(CountryCode, CountryFacetAmount))

for key,rate in dictionary.items():
	rate = percentage(rate,max(CountryFacetAmount))
        if rate == 0:
                fill = "#FFFFFF"
        elif rate < 10:
                fill = "#E6E6E6"
        elif rate < 20:
                fill = "#CCCCCC"
        elif rate < 30:
                fill = "#B2B2B2"
        elif rate < 40:
                fill = "#999999"
        elif rate < 50:
                fill = "#808080"
        elif rate < 60:
                fill = "#666666"
        elif rate < 70:
                fill = "#4C4C4C"
        elif rate < 80:
                fill = "#333333"
        elif rate < 90:
                fill = "#1A1A1A"
        elif rate < 101:
                fill = "#000000"     
        else:
                fill = "#FFFFFF"

        #country names need to be lowercase             
        ColorData.append('.'+ key.lower() +' { fill: ' + fill+ ' }')

#Create results folder if it does not exist.
ResultFolder = 'Results' 
if not os.path.exists(ResultFolder): os.makedirs(ResultFolder)

#Create scan folder
ScanFolder = ' '.join(sys.argv[1:])
if not os.path.exists(ResultFolder + "/" + ScanFolder): os.makedirs(ResultFolder + "/" + ScanFolder)

#Create file based on the facet search criteria and generated data (for svg worldmap)
f = open(ResultFolder + "/"  + ScanFolder + "/" + "BlankMap-ColorCSS" +  ".css","w")

#put css code into css file
for item in ColorData:
        f.write("%s\n" % item)
f.close()

#copy svg file to target data folder
copyfile("BlankMap-World.svg", ResultFolder + "/"  + ScanFolder + "/WorldMapPlot.svg")

fig.savefig(ResultFolder + "/"  + ScanFolder +'/DataPlot.png')
