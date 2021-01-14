import igraph, os
import pandas as pd
import time, pickle

from make_day_network import *

month_to_days = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

def pickle_graph(date, undirected =False):
    '''
    TODO: add docstring
    '''
    fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "New Data\dt={}\\{}.txt".format(date, date))
    network = create_email_network(fpath, undirected = undirected)
    if undirected:
        new_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pickles\{}-new-undirected.pickle".format(date, date))
    else:
        new_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pickles\{}-new.pickle".format(date, date))
    pickle_out = open(new_path, 'wb')
    pickle.dump(network, pickle_out)
    pickle_out.close()

def unpack_graph(date, undirected = False):
    '''
    TODO: add docstring
    '''
    if undirected:
        fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pickles\{}-new-undirected.pickle".format(date, date))
    else:
        fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pickles\{}-new.pickle".format(date, date))
    pickle_in = open(fpath, 'rb')
    network = pickle.load(pickle_in)
    pickle_in.close()
    return network

def pickle_month(month, undirected = False):
    '''
    TODO: add docstring
    '''
    l_date = month_to_days[month]
    month = str(month)
    if len(month) == 1:
        month = '0' + month
    
    for i in range(1, l_date + 1):
        new_day = str(i)
        if len(new_day) == 1:
            new_day = '0' + new_day
        current_date = "2020-" + month + "-" + new_day
        pickle_graph(current_date, undirected=undirected)


def pickle_months(s_month, e_month, undirected = False):
    '''
    TODO: add docstring
    '''
    for i in range(e_month - s_month):
        print(i+s_month)
        pickle_month(i+s_month, undirected=undirected)

def unpack_month(month, undirected = False):
    '''
    TODO: add docstring
    '''
    grp_graphs, dpt_graphs = [], []
    l_date = month_to_days[month]
    month = str(month)
    if len(month) == 1:
        month = '0' + month

    for i in range(1, l_date + 1):
        new_day = str(i)
        if len(new_day) == 1:
            new_day = '0' + new_day
        current_date = "2020-" + month + "-" + new_day
        grp_graph, dpt_graph = unpack_graph(current_date, undirected=undirected)
        grp_graphs.append(grp_graph)
        dpt_graphs.append(dpt_graph)

    return grp_graphs, dpt_graphs

def unpack_months(s_month, e_month, undirected = False):
    '''
    TODO: add docstring
    '''
    grp_graphs, dpt_graphs = [], []
    for i in range(e_month - s_month):
        print(i+s_month)
        new_grp, new_dpt = unpack_month(i + s_month, undirected = undirected)
        grp_graphs += new_grp
        dpt_graphs += new_dpt

    return grp_graphs, dpt_graphs

if __name__ == "__main__":
    tik = time.time()
    pickle_months(1, 9, undirected = True)
    tok = time.time()
    print(tok-tik)
    pass