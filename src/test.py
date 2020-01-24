import networkx as nx
from matplotlib import pyplot as plt

def AAT(G, node):
    successors = []
    successor_iterator = G.successors(node)
    for successor in successor_iterator:
        successors.append(successor)
    predecessors = []
    predecessor_iterator = G.predecessors(node)
    for predecessor in predecessor_iterator:
            predecessors.append(predecessor)
    AATs = []
    max_AAT = 0
    Node_arr = node.split(" ")
    if(len(predecessors) >= 0):
        for i in range (0 , len(predecessors)):
            arr = predecessors[i].split(" ")
            AATs.append(G.get_edge_data(predecessors[i], node)['weight'] + int(arr[3]))
        AATs.append(int(Node_arr[3]))
        max_AAT = max(AATs)
    Node_arr[3] = str(max_AAT)
    seperator = ' '
    NewNode = seperator.join(Node_arr)
    mapping = {node: NewNode}
    G = nx.relabel_nodes(G, mapping, copy=False)
    if len(successors) == 0:
        return 0
    for i in range (0 , len(successors)):
       AAT(G, successors[i])

def RAT(G, node):
    successors = []
    successor_iterator = G.successors(node)
    for successor in successor_iterator:
        successors.append(successor)
    predecessors = []
    predecessor_iterator = G.predecessors(node)
    for predecessor in predecessor_iterator:
            predecessors.append(predecessor)
    RATs = []
    min_RAT = 100000
    Node_arr = node.split(" ")
    if(len(successors) >= 0):
        for i in range (0 , len(successors)):
            arr = successors[i].split(" ")
            RATs.append(int(arr[4]) - G.get_edge_data(node, successors[i])['weight'])
        RATs.append(int(Node_arr[4]))
        min_RAT = min(RATs)
    Node_arr[4] = str(min_RAT)
    seperator = ' '
    NewNode = seperator.join(Node_arr)
    mapping = {node: NewNode}
    G = nx.relabel_nodes(G, mapping, copy=False)
    if len(predecessors) == 0:
        return 0
    for i in range (0 , len(predecessors)):
       RAT(G, predecessors[i])


### slack for each node ###
def node_slack(G):
    for node in G:
        Node_arr = node.split(" ")
        Node_arr[5] = str(int(Node_arr[3]) - int(Node_arr[4]))
        seperator = ' '
        NewNode = seperator.join(Node_arr)
        mapping = {node: NewNode}
        G = nx.relabel_nodes(G, mapping, copy=False)

crit_path = []

### critical path without final node ###
def critical_path(G, node):
    successors = []
    successor_iterator = G.successors(node)
    for successor in successor_iterator:
        successors.append(successor)
    if len(successors) == 0:
        return
    else:
        Node_arr = node.split(" ")
        for i in range (0 , len(successors)):
            successor_node = successors[i].split(" ")
            if Node_arr[5] == successor_node[5]:
                crit_path.append(node)
                critical_path(G, successors[i])
    
def get_last_node(G):
    y = nx.topological_sort(G)
    arr = []
    for i in y:
        arr.append(i)
    return arr[len(arr)-1]

def get_first_node(G):
    y = nx.topological_sort(G)
    arr = []
    for i in y:
        arr.append(i)
    return arr[0]

def main_call(G, one, eight):
    AAT(G, one)

    eight = get_last_node(G)

    RAT(G, eight)

    node_slack(G)
    
    
    ### for critical path ###

    one = get_first_node(G)

    critical_path(G, one)
    ### appending final node to critical path ###
    eight = get_last_node(G)
    crit_path.append(eight)
    print(crit_path)

G = nx.DiGraph()
one = "-9 Y input-9 0 100 0"
two = "11 C NAND3X1_3 0 100 0"
three = "-8 Y input-8 0 100 0"
four = "10 B NAND3X1_2 0 100 0"
five = "-7 Y input-7 0 100 0"
six = "9 C NAND3X1_1 0 100 0"
seven = "-6 Y input-6 0 100 0"
eight = "14 A NOR2X1_2 0 100 0"
G.add_node("-9 Y input-9 0 100 0")
G.add_node("11 C NAND3X1_3 0 100 0")
G.add_node("-8 Y input-8 0 100 0")
G.add_node("10 B NAND3X1_2 0 100 0")
G.add_node("-7 Y input-7 0 100 0")
G.add_node("9 C NAND3X1_1 0 100 0")
G.add_node("-6 Y input-6 0 100 0")
G.add_node(eight)


G.add_edge(one,two)
G.add_edge(two,three)
G.add_edge(three,four)
G.add_edge(one,five)
G.add_edge(five,six)
G.add_edge(six,seven)
G.add_edge(seven,eight)
G.add_edge(four,eight)

G[one][two]['weight'] = 2
G[two][three]['weight'] = 3
G[three][four]['weight'] = 4
G[one][five]['weight'] = 3
G[five][six]['weight'] = 4
G[six][seven]['weight'] = 5
G[seven][eight]['weight'] = 20
G[four][eight]['weight'] = 10


main_call(G, one, eight)


#labels = nx.get_edge_attributes(G,'weight')
nx.draw(G, with_labels = True)
plt.show()