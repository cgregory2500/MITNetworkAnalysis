import igraph, os, csv
import pandas as pd
import time

month_to_days = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

def add_node(graph, node_attr):
    '''
    Input: an igraph graph object, 
        a dictionary of node_attributes
    Output: None
    
    Adds a new node to the graph with the node attributes attached
    '''

    graph.add_vertices(1)
    for attr in node_attr:
        graph.vs[-1][attr] = node_attr[attr]
    return 

def get_node_index(graph, attr):
    '''
    Input: an igraph graph object,
        a tuple with the name and value of the attribute being searched for
    Output: integer of the index of the node based on the passed in attributes

    searches the graph for the particular node with the attributes that are passed in 
    '''
    return graph.vs.select(lambda v: v.attributes()[attr[0]] == attr[1])[0].index

def node_exists(graph, attr):
    '''
    Input: igraph graph object,
        tuple of attr name and value
    Output: 
    '''
    if len(graph.vs.select(lambda v: v.attributes()[attr[0]] == attr[1])):
        return True
    return False

def add_edge(graph, sender, receiver, edge_attr):
    '''
    Input: an igraph graph object, 
        id of sender node in the graph, 
        id of receiver node in graph,
        dictionary of edge attr
    Output: None

    Adds a new edge to the graph with the edge attributes related to the edge
    '''

    #gets the indexes in the vs of graph 
    sender_index = graph.vs.select(lambda v: v.attributes()[sender[0]] == sender[1])[0].index
    receiver_index = graph.vs.select(lambda v: v.attributes()[receiver[0]] == receiver[1])[0].index

    #adds the edge to the graph
    graph.add_edges([(sender_index, receiver_index)])

    # gets the id of the edge
    edge_id = graph.get_eid(sender_index, receiver_index)

    # adds all specified attributes to the edge
    for attr in edge_attr:
        graph.es[edge_id][attr] = edge_attr[attr]

    return

def create_email_network(fpath, undirected = False):
    '''
    Input: a tsv data file
    Output: an igraph Graph object for the departments, 
        an igraph Graph object for the individual group ids

    makes an undirected graph based on the email communications of that day
    '''
    data = pd.read_csv(fpath, sep="\t")
    if undirected:
        group_graph, dpt_graph = igraph.Graph(), igraph.Graph()
    else:
        group_graph, dpt_graph = igraph.Graph(directed = True), igraph.Graph(directed = True)
    group_graph.es['weight'], dpt_graph.es['weight'] = 1, 1

    for line in data.iterrows():
        pt = list(line[1])

        #makes sure the nodes are in the graph and adds if not
        for dpt in [pt[:2], pt[2:4]]:
            if not node_exists(dpt_graph, ("name", dpt[0])):
                add_node(dpt_graph, {"id": dpt[0], "name": dpt[0]})
            if not node_exists(group_graph, ("id", dpt[1])):
                add_node(group_graph, {"id": dpt[1], "dpt_name": dpt[0]})

        add_edge(dpt_graph, ("name", pt[0]), ("name", pt[2]), {"emails": pt[-1], "weight": pt[-1]})
        add_edge(group_graph, ("id", pt[1]), ("id", pt[3]), {"emails": pt[-1], "weight": pt[-1]})

    return group_graph, dpt_graph

def make_day_networks(s_date, e_date, undirected=False):
    '''
    Input: s_date - a string that denotes the start of the time period (inclusive)
    e_date - a string that denotes the end of the time period (inclusive)

    Output: two lists, 
    list of igraph graph objects that are based on the group_ids
    list of igraph graph objects that are based on the department names
    '''
    split_s_date, split_e_date = s_date.split("-"), e_date.split("-")
    
    group_graphs, dpt_graphs = [], []
    for i in range(int(split_e_date[-1]) - int(split_s_date[-1])):
        new_day = str((int(split_s_date[-1]) +i))
        if len(new_day) == 1:
            new_day = '0' + new_day
        current_date = "2020-" + split_s_date[1] + "-" + new_day
        fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "text\dt={}\\{}.txt".format(current_date, current_date))
        new_group, new_dpt = create_email_network(fpath, undirected = undirected)
        group_graphs.append(new_group)
        dpt_graphs.append(new_dpt)

    return group_graphs, dpt_graphs

def create_day_networks_month(month, undirected=False):
    '''
    TODO: add docstring
    '''
    end_day = str(month_to_days[month])
    new_month = str(month)
    if len(new_month) == 1:
        new_month = "0" + new_month

    s_date = '2020-' + new_month + '-01'
    e_date = '2020-' + new_month + '-' + end_day

    return make_day_networks(s_date, e_date, undirected=undirected)

def all_dates_month(m):
    '''
    TODO: add docstring
    '''
    dates = []
    
    month = str(m)
    if len(month) == 1:
        month = '0' + month

    for d in range(1, month_to_days[m]):
        day = str(d)
        if len(day) ==1:
            day = '0' + day
        
        dates.append('2020-' + month + '-' + day)

    return dates

def all_dates(s_month, e_month):
    '''
    TODO: add docstring
    '''
    dates = []

    for m in range(e_month - s_month):
        dates += all_dates_month(s_month + m)

    return dates

def merge_week(dates):
    '''
    TODO: add docstring
    '''
    group_to_department, group_contacts = {}, {}
    for date in dates:
        fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "text\dt={}\\{}.txt".format(date, date))
        data = pd.read_csv(fpath, sep="\t")

        for line in data.iterrows():
            data = list(line[1])

            group_to_department[data[1]], group_to_department[data[3]] = data[0], data[2]

            if (data[1], data[3]) not in group_contacts:
                group_contacts[(data[1], data[3])] = data[-1]
            else:
                group_contacts[(data[1], data[3])] += data[-1]

    new_data = []
    for contact in group_contacts:
        g1, g2, num = contact[0], contact[1], group_contacts[contact]
        d1, d2 = group_to_department[g1], group_to_department[g2]

        new_data.append([d1, g1, d2, g2, num])

    destpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "MergedWeek\Week of {}.csv".format(dates[0]))
    with open(destpath, 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerows(new_data)

def merge_week_dept(dates):
    '''
    TODO: add docstring
    '''
    group_contacts = {}
    for date in dates:
        fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "text\dt={}\\{}.txt".format(date, date))
        data = pd.read_csv(fpath, sep="\t")

        for line in data.iterrows():
            data = list(line[1])

            if (data[0], data[2]) not in group_contacts:
                group_contacts[(data[0], data[2])] = data[-1]
            else:
                group_contacts[(data[0], data[2])] += data[-1]

    new_data = []
    for contact in group_contacts:
        d1, d2, num = contact[0], contact[1], group_contacts[contact]

        new_data.append([d1, d2, num])

    destpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "MergedWeek\Dept Only Graphs\Week of {}.csv".format(dates[0]))
    with open(destpath, 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerows(new_data)

def merge_week_months(s_month, e_month, dept_only = False):
    '''
    TODO: add docstring
    '''

    dates = all_dates(s_month, e_month)

    inc = 0
    while merge_week_months:
        print(inc)
        inc+=1

        if dept_only:
            merge_week_dept(dates[:7])
        else:
            merge_week(dates[:7])
        if len(dates) >= 7:
            dates = dates[7:]
        else:
            break


if __name__ == "__main__":
    tik = time.time()

    merge_week_months(1, 9, dept_only=True)

    tok = time.time()
    print(tok-tik)
