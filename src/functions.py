import json as js
from classes import * 
import networkx as nx
from liberty.parser import parse_liberty

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp2d

def KEY(elem):
    return elem.CellNumber

def KEY2(elem):
    return elem[1]

def Generate_Edgelist(json_file):
    name_list = []

    ### function that returns a dictionary with the edges between nodes as keys ###
    ###and the values as a list of strings that show the nodes (cells) and their connections (Y for output, other letters for input)###
    def wires(json):
        modules_list = json["modules"]
        mydict = {}
        for module in modules_list:
            for key, value in modules_list[module]["cells"].items():
                name_list.append(key)  ### add keys to a list that will be used for renaming cells ###

        reverse_lookup_namelist = {}
        i = 0
        for name in name_list:
            reverse_lookup_namelist[name] = i
            i += 1
        
        for module in modules_list:
            for cell in modules_list[module]["cells"]:
                    for key, value in modules_list[module]["cells"][cell]["connections"].items():
                        if (value[0] != '0' and value[0] != '1'):
                            mylist = []
                            mystr =  cell + " "  + str(reverse_lookup_namelist[cell]) + " " + key
                            mylist.append(mystr)
                            if value[0] in mydict:
                                mydict[value[0]].append(mystr)
                            else:
                                mydict[value[0]] = mylist
        mydict_type = {}
        keys = mydict.keys()
        for i in keys:
            mydict_type[i] = []
        for module in modules_list:
            mod = modules_list[module]["cells"]
        for row in mydict:
            for cell in mydict[row]:
                cell_arr = cell.split(" ")
                cell_arr[0] = mod[cell_arr[0]]["type"]
                string = " "
                string = string.join(cell_arr)
                mydict_type[row].append(string)
                print("")

        #return mydict
        return mydict_type

    # outCellnum, inCellNum, in_PinNum, Gate_out, Gate_in
    with open(json_file) as json_file:  # load json file
        data = js.load(json_file)

    ######################inputs############################
    x = wires(data)
    a = []
    temp1 = {}
    for x_ in x:
        is_input = True
        for b in x[x_]: 
            if(b[len(b)-1] == 'Y' or b[len(b)-1] == 'Q'):
                is_input = False
        if(is_input):
            a.append(x_)
            temp1[x_] = x[x_]

        is_input = False
    ##########################outputs#######################
    a2 = []
    temp2 = {}
    for x_ in x:
        if(x[x_][0] == "BUFX2_13 50 Y"):
            print("d")
        is_output = True
        for b in x[x_]: 
            if(b[len(b)-1] != 'Y' and b[len(b)-1] != 'Q'):
                is_output = False
        if(is_output):
            a2.append(x_)
            temp2[x_] = x[x_]

        is_output = False

    i = -1
    for k in temp1:
        temp1[k].append("input"+ str(i) + " " + str(i) + " Y")
        i -= 1
    j = i
    for v in temp2:
        temp2[v].append("output"+ str(j) + " " + str(j) + " A")
        j -= 1

    for p in temp1:
        x[p] = temp1[p]
    for m in temp2:
        x[m] = temp2[m]

    edgelist = []
    removes = []

    for item in x:
        if x[item][0][-3:] == "vdd" or x[item][0][-3:] == "gnd":
            removes.append(item)
            # del x[item]
    for u in removes:
        del x[u]

    ### create edgelist ###
    for key, value in x.items():
        for i in range(0, len(value)):
            if (value[i][-1:] == 'Y' or value[i][-1:] == 'Q'):
                for j in range(0, len(value)):
                    if (value[j][-1:] != 'Y' and value[j][-1:] != 'Q'):
                        edgelist.append(value[i][:-2] + " " + value[j][:-2] + " " + value[j][-1:])
                break


    temp = edgelist
    edgelist = []
    for edge in temp:
        x = edge.split(" ")
        edgelist.append(x)
    return edgelist

def Generate_Nodes(edgelist):
    
    nodes = []
    Curr = []
    for edge in edgelist:
        
        if(Curr.count(edge[1]) == 0): # Is not a node yet
            Curr.append(edge[1])
            nodes.append(Node("output",edge[1],"Y",edge[0]))
    OutCurr = Curr
    Icurr = []
    for edge in edgelist:        
        nodes.append(Node("input" + str(Curr.count(edge[3])) , edge[3], edge[4], edge[2]))
        Icurr.append(edge[3])
        Curr.append(edge[3])

    nodes.sort(key=KEY)
    edgelist.sort(key=KEY2)

    return nodes

def CreateDAG(edgelist,nodes):
    G = nx.DiGraph()
    for i in nodes:
        temp_str = i.CellNumber +' '+ i.pin +' '+ i.gate + ' 0' + ' 0' + ' 0'
        G.add_node(temp_str)
    
    G.add_node("SOURCE")
    G.add_node("SINK")
    for i in nodes:
        CN = int(i.CellNumber)
        if(CN < 0):
            if(len(i.gate) >= 6 and i.gate[0:6] == "output"):
                G.add_edge(i.CellNumber +' '+ i.pin +' '+ i.gate + ' 0' + ' 0' + ' 0', "SINK",weight =0)
            elif(len(i.gate)>=5 and i.gate[0:5] == "input"):
                G.add_edge("SOURCE" , i.CellNumber +' '+ i.pin +' '+ i.gate + ' 0' + ' 0' + ' 0',weight =0)

    for c in edgelist:
        G.add_edge(c[1]+' Y '+c[0] + ' 0' + ' 0' + ' 0', c[3]+' '+c[4]+' '+c[2] + ' 0' + ' 0' + ' 0',weight = 0)
    
    prev_elem = 0
    num = 0
    ob = None
    for b in range (len(nodes)):
        if(nodes[b].type == 'output' and int(nodes[b].CellNumber)>=0):
            for ci in range (b+1,len(nodes)):
                if(nodes[b].CellNumber == nodes[ci].CellNumber):
                    G.add_edge(nodes[ci].CellNumber+' '+nodes[ci].pin+' '+nodes[ci].gate + ' 0' + ' 0' + ' 0',nodes[b].CellNumber+' '+nodes[b].pin+' '+nodes[b].gate + ' 0' + ' 0' + ' 0',weight =0) # need to fix this
                else:
                    break
    nx.draw(G, with_labels = True)
    plt.show()

    return G

def TopologicalSort(G, node):
    successors = []
    topological_arr = []
    successors_iterator = G.successors(node)
    for successor in successors_iterator:
        successors.append(successor)
    for successor in successors:
        successor_arr = successor.split(" ")
        if( successor_arr[1] == "Y" and successor_arr[2][0:5] != "input" and successor_arr[2][0:6] != "output"):
            if(successor not in topological_arr):
                topological_arr.append(successor)
    while(True): 
        successors2 = []     
        for successor in successors:
            successors_iterator = G.successors(successor)
            for successor2 in successors_iterator:
                successors2.append(successor2)
        if("SINK" in successors2):
            break 
        for successor2 in successors2:
            successor_arr = successor2.split(" ")
            if( successor_arr[1] == "Y" and successor_arr[2][0:5] != "input" and successor_arr[2][0:6] != "output"):
                if(successor2 not in topological_arr):
                    topological_arr.append(successor2)
        successors = successors2
    return topological_arr

def AddWeights(G,TopSort):
    for node in TopSort:
        successors = []
        successor_iterator = G.successors(node)
        for successor in successor_iterator:
            successors.append(successor)
        predecessors = []
        predecessor_iterator = G.predecessors(node)
        for predecessor in predecessor_iterator:
            predecessors.append(predecessor)
        Output_Capacitance = 0
        for s in successors:
            s = s.split(" ")
            cn = s[2]
            if(s == "SINK" or (len(cn)>5 and cn[0:6]=="output")):
                Output_Capacitance = 0
                break
            CellName = s[2]
            PinName = s[1]
            Output_Capacitance = Output_Capacitance + GetCap(CellName,PinName)

        for child in predecessors:
            child_str = child
            predecessors_child = []
            predecessor_child_iterator = G.predecessors(child)
            for predecessor in predecessor_child_iterator:
                predecessors_child.append(predecessor)
            input_trans = 0
            bob = predecessors_child[0].split(" ")
            bob = bob[2]
            if(predecessors_child[0] == "SOURCE" or (len(bob)>4 and bob[0:5]=="input")):
                input_trans = 0
            else:
                input_trans = G.node[predecessors_child[0]]["max"]
            child = child.split(" ")
            timing_arc_r,timing_arc_f = CellDelay(child[2], child[1], input_trans, Output_Capacitance)
            G[child_str][node]['weight'] = timing_arc_r[0] + timing_arc_f[0]
        maxawy = 0
        for p in predecessors:
            if(G[p][node]['weight'] > maxawy):
                maxawy = G[p][node]['weight']
        G.node[node]["max"] = maxawy
    return G

def GetCap(CellName,PinName):
    liberty_file = "./osu035.lib"
    library = parse_liberty(open(liberty_file).read())
    CellNumber = 0
    for i in range(18,len(library.groups)):
        if(CellName == library.groups[i].args[0]):
            CellNumber = i
            break
    
    for v in library.groups[CellNumber].groups:
        if(v.args[0]==PinName):
            return v.attributes['capacitance']

def CellDelay(CellName, PinName, Input_Trans, Output_Capacitance):
    liberty_file = "./osu035.lib"
    library = parse_liberty(open(liberty_file).read())
    CellNumber = 0
    for i in range(18,len(library.groups)):
        if(CellName == library.groups[i].args[0]):
            CellNumber = i
            break
    pinTemp = library.groups[CellNumber].groups
    for v in library.groups[CellNumber].groups[len(pinTemp)-1].groups:
        if(PinName == v.attributes["related_pin"].value):
            rise_trans = v.groups[1].attributes
            fall_trans = v.groups[3].attributes
            rise_trans['index_1'][0] = rise_trans['index_1'][0].value.split(", ")
            rise_trans['index_2'][0] = rise_trans['index_2'][0].value.split(", ")
            fall_trans['index_1'][0] = fall_trans['index_1'][0].value.split(", ")
            fall_trans['index_2'][0] = fall_trans['index_2'][0].value.split(", ")
            
            for c in range(len(rise_trans['values'])):
                rise_trans['values'][c] = rise_trans['values'][c].value.split(", ")
            for f in range(len(fall_trans['values'])):
                fall_trans['values'][f] = fall_trans['values'][f].value.split(", ")

            X = rise_trans['index_2'][0]
            Y = []
            Z = []

            for c in range(0, len(rise_trans['index_1'][0])):
                rise_trans['index_1'][0][c] = float(rise_trans['index_1'][0][c])
            for c in range(0, len(rise_trans['index_2'][0])):
                rise_trans['index_2'][0][c] = float(rise_trans['index_2'][0][c])
            
            for w in range (0,len(rise_trans['index_1'][0])):
                for t in range (0,len(rise_trans['index_2'][0])):
                    rise_trans['values'][w][t] = float(rise_trans['values'][w][t]) 



            for d in range (0,len(rise_trans['index_1'][0])-1):
                X = X + rise_trans['index_2'][0]
            
            for s in range (0,len(rise_trans['index_1'][0])):
                for b in range (0,len(rise_trans['index_2'][0])):
                    Y.append(rise_trans['index_1'][0][s])
            
            for w in range (0,len(rise_trans['index_1'][0])):
                for t in range (0,len(rise_trans['index_2'][0])):
                    Z.append(rise_trans['values'][w][t])

            f = interp2d(X, Y, Z, kind='cubic')

            X2 = fall_trans['index_2'][0]
            Y2 = []
            Z2 = []

            for c in range(0, len(fall_trans['index_1'][0])):
                fall_trans['index_1'][0][c] = float(fall_trans['index_1'][0][c])
            for c in range(0, len(fall_trans['index_2'][0])):
                fall_trans['index_2'][0][c] = float(fall_trans['index_2'][0][c])
            
            for w in range (0,len(fall_trans['index_1'][0])):
                for t in range (0,len(fall_trans['index_2'][0])):
                    fall_trans['values'][w][t] = float(fall_trans['values'][w][t]) 



            for d in range (0,len(fall_trans['index_1'][0])-1):
                X2 = X2 + fall_trans['index_2'][0]
            
            for s in range (0,len(fall_trans['index_1'][0])):
                for b in range (0,len(fall_trans['index_2'][0])):
                    Y2.append(fall_trans['index_1'][0][s])
            
            for w in range (0,len(fall_trans['index_1'][0])):
                for t in range (0,len(fall_trans['index_2'][0])):
                    Z2.append(fall_trans['values'][w][t])

            f2 = interp2d(X2, Y2, Z2, kind='cubic')
            val_rise = f(Input_Trans, Output_Capacitance)
            val_fall = f2(Input_Trans, Output_Capacitance)
            return val_rise,val_fall

def ParseSdc(sdc_file):
    f = open(sdc_file, "r")
    lines = []
    for line in f:
        line_data = line.split(" ")

        #array of lines
        if(len(line_data)>0):
            lines.append(line_data)
        if(line_data[0] == "set" and line_data[1] == "PERIOD"):
            return line_data[2][:-1]

def AAT(G, node):
    successors = []
    successor_iterator = G.successors(node)
    for successor in successor_iterator:
        successors.append(successor)
    predecessors = []
    predecessor_iterator = G.predecessors(node)
    for predecessor in predecessor_iterator:
        predecessors.append(predecessor)
    
    if(node == 'SOURCE'):
        for i in range (0 , len(successors)):
            AAT(G, successors[i])
        return 0
    
    AATs = []
    max_AAT = 0
    Node_arr = node.split(" ")
    if(len(predecessors) >= 0):
        for i in range (0 , len(predecessors)):
            if(predecessors[i]=="SOURCE"):
                AATs.append(G.get_edge_data(predecessors[i], node)['weight'])
            else:    
                arr = predecessors[i].split(" ")
                AATs.append(G.get_edge_data(predecessors[i], node)['weight'] + float(arr[3]))
        if(node != "SINK"):
            AATs.append(float(Node_arr[3]))
        max_AAT = max(AATs)
    if(node != "SINK"):
        Node_arr[3] = str(max_AAT)
        seperator = ' '
        NewNode = seperator.join(Node_arr)
        mapping = {node: NewNode}
        G = nx.relabel_nodes(G, mapping, copy=False)
    if len(successors) == 0:
        return 0
    for i in range (0 , len(successors)):
       AAT(G, successors[i])

def RAT(G, node, SINK_RAT):
    successors = []
    successor_iterator = G.successors(node)
    for successor in successor_iterator:
        successors.append(successor)
    predecessors = []
    predecessor_iterator = G.predecessors(node)
    for predecessor in predecessor_iterator:
            predecessors.append(predecessor)
    if(node == 'SINK'):
        for i in range (0 , len(predecessors)):
            RAT(G, predecessors[i],SINK_RAT)
        return 0
    RATs = []
    min_RAT = 100000
    Node_arr = node.split(" ")
    if(node != "SINK" and len(successors) >= 0):
        for i in range (0 , len(successors)):
            if(successors[i] == "SINK"):
                RATs.append(float(SINK_RAT) - G.get_edge_data(node, successors[i])['weight'])
            else:
                arr = successors[i].split(" ")
                RATs.append(float(arr[4]) - G.get_edge_data(node, successors[i])['weight'])   
        if(node != "SOURCE"):
            RATs.append(float(Node_arr[4]))
        min_RAT = min(RATs)
    if(node != "SOURCE"):
        Node_arr[4] = str(min_RAT)
        seperator = ' '
        NewNode = seperator.join(Node_arr)
        mapping = {node: NewNode}
        G = nx.relabel_nodes(G, mapping, copy=False)
    if len(predecessors) == 0:
        return 0
    for i in range (0 , len(predecessors)):
       RAT(G, predecessors[i],SINK_RAT)

def node_slack(G):
    tempo = list(nx.topological_sort(G))
    min =100000
    for node in tempo:
        if(node != "SOURCE" and node != "SINK"):
            Node_arr = node.split(" ")
            Node_arr[5] = str(float(Node_arr[4]) - float(Node_arr[3]))
            if(min > float(Node_arr[5])):
                min = float(Node_arr[5])
            seperator = ' '
            NewNode = seperator.join(Node_arr)
            mapping = {node: NewNode}
            G = nx.relabel_nodes(G, mapping, copy=False)
    return min

