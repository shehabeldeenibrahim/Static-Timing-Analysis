import json as js
 
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import networkx as nx
from functions import * 
from classes import * 
import sys, getopt

def main(argv):

    try:
        args, opts = getopt.getopt(argv,"j:sdc:lib")
    except getopt.error: 
        print("input error") 
        sys.exit(2)

    netlist_path = argv[0]
    lef_path = argv[1]
    def_path = argv[2]
    i = 0
    for opt in argv:
        if(i >= len(argv)-1):
            break
        if opt == '-j':
            json_file = argv[i+1]
        elif opt == ("-sdc"):
            sdc_ = argv[i+1]
        elif opt == ("-lib"):
            lib = argv[i+1]
        i+=1
    print(json_file, sdc_)
    return json_file, sdc_

json_file, sdc = main(sys.argv[1:])
#json_file = "testcases/AND_temp.json"
edgelist = Generate_Edgelist(json_file)
nodes = Generate_Nodes(edgelist)
DAG = CreateDAG(edgelist,nodes)
TopSort = TopologicalSort(DAG, "SOURCE")
DAG = AddWeights(DAG,TopSort)
AAT(DAG,"SOURCE")
SINK_RAT = ParseSdc(sdc)
RAT(DAG,"SINK",SINK_RAT)
SLACK = node_slack(DAG)
nx.draw(DAG, with_labels = True)
plt.show()
print(SLACK)