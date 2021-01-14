import igraph, os, time, struct
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from gephistreamer import graph, streamer
import csv

from make_day_network import * 
from graph_storage import *
from graph_analysis import *
from dpt_analysis import *
from _datetime import date

month_to_days = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

def convert_files(date):
    '''
    TODO: add docstring
    '''
    fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "New Data\dt={}\\{}.txt".format(date, date))
    destpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "csvs\{}-csv.csv".format(date))
    # read tab-delimited file
    with open(fpath,'r') as fin:
        cr = csv.reader(fin, delimiter='\t')
        filecontents = [line for line in cr]

    # write comma-delimited file (comma is the default delimiter)
    with open(destpath, 'w', newline= '') as f:
        writer = csv.writer(f)
        writer.writerows(filecontents)

def convert_month(m):
    '''
    TODO: add docstring
    '''
    for date in all_dates_month(m):
        convert_files(date)

def make_gephi_csvs(fpath):
    '''
    TODO: add docstring
    '''
    date = fpath.split()[-1][:-4]
    node_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "MergedWeek\Dept Only Graphs\Gephi\ Nodes Week of {}.csv".format(date))
    edge_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "MergedWeek\Dept Only Graphs\Gephi\ Edges Week of {}.csv".format(date))

    node_data, edge_data = [['Id', 'Label']], [['Source', 'Target', 'Type', 'Weight']]
    nodes = set()

    with open(fpath, 'r') as f:
        cr = csv.reader(f)
        for line in cr:
            nodes.add(line[0])
            nodes.add(line[1])
            edge_data.append([line[0], line[1], 'Directed', line[-1]])

    for node in nodes:
        node_data.append([node, node])

    with open(node_path, 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerows(node_data)

    with open(edge_path, 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerows(edge_data)

def weekly_community_global(func, s_month, e_month):
    '''
    TODO: add docstring
    '''

    dates_to_comms = make_all_comms(s_month, e_month)
    comm_y_vals = []
    for dt in dates_to_comms:
        comm_y_vals.append(func(dates_to_comms[dt]))

    print(comm_y_vals)
    weekly_comm_y_vals = aggregate_weekly_from_vals(comm_y_vals)
    
    single_plot([weekly_comm_y_vals])

def aggregate_weekly_from_vals(in_vals):
    '''
    TODO: add docstring
    '''
    j= 0
    weekly_vals = []
    max_vals = len(in_vals)
    new_val = []
    while j < max_vals:
        if j % 7 == 0 and j != 0:
            weekly_vals.append(sum(new_val)/7)
            print('week', j, ":", new_val)
            new_val = []
        new_val.append(in_vals.pop(0))
        j += 1
    
    return weekly_vals

def average_indy_vals(func, graph):
    '''
    TODO: add docstring
    '''
    r = []
    for v in graph.vs:
        if func(v) != "nan":
            r.append(func(v))

    return sum(r)/len(r)

def weekly_community_vertex_props(func, s_month, e_month):
    '''
    TODO: add docstring
    '''
    dates_to_comms = make_all_comms(s_month, e_month)
    indy_y_vals = [average_indy_vals(func, dates_to_comms[g].giant()) for g in dates_to_comms]

    averaged_vals = aggregate_weekly_from_vals(indy_y_vals)

    single_plot([averaged_vals])

def subgraphs_and_giant(func, s_month, e_month):
    '''
    TODO: add docstring
    '''

    dates_to_comms = make_all_comms(s_month, e_month)
    giants_y_vals = [func(dates_to_comms[g].giant()) for g in dates_to_comms]
    
    subgraphs = [dates_to_comms[g].subgraphs() for g in dates_to_comms]
    subgraph_y_vals = []
    for day in subgraphs:
        vals = [func(g) for g in day]
        subgraph_y_vals.append(sum(vals)/len(vals))

    giants_y_vals, subgraph_y_vals = aggregate_weekly_from_vals(giants_y_vals), aggregate_weekly_from_vals(subgraph_y_vals)
    
    single_plot([giants_y_vals, subgraph_y_vals])

def subgraphs_and_giants_vertex_avgs(func, s_month, e_month):
    '''
    TODO: add docstring
    '''
    dates_to_comms = make_all_comms(s_month, e_month)
    giants_y_vals = [average_indy_vals(func, dates_to_comms[g].giant()) for g in dates_to_comms]

    subgraphs = [dates_to_comms[g].subgraphs() for g in dates_to_comms]
    subgraph_y_vals = []
    for day in subgraphs:
        vals = [average_indy_vals(func, g) for g in day]
        print(vals)
        for i, val in enumerate(vals):
            if val == None:
                vals[i] = 0
        subgraph_y_vals.append(sum(vals)/len(vals))

    giants_y_vals, subgraph_y_vals = aggregate_weekly_from_vals(giants_y_vals), aggregate_weekly_from_vals(subgraph_y_vals)

    single_plot([giants_y_vals, subgraph_y_vals])

def all_departments(s_month, e_month):
    '''
    TODO: add docstring
    '''
    total_depts = set()

    dpt_graphs = unpack_months(s_month, e_month)[1]
    for g in dpt_graphs:
        for d in g:
            total_depts.add(d['id'])

    return total_depts


def find_comm_changes(s_month, e_month, department, max_sim_members):
    '''
    TODO add docstring
    '''

    dates_to_comms = make_all_comms(s_month, e_month)
    print(list(dates_to_comms['2020-01-01']))

    switches = 0
    last_comm = []
    for date in dates_to_comms:
        comms = list(dates_to_comms[date])
        cur_comm = []

        # gets the community that it is in 
        for comm in comms:
            to_check = set(comm)
            if department in to_check:
                cur_comm = comm
        
        if last_comm == []:
            continue
        else:
            #finds the size of the intersection of the switch
            num_sim_members = len(set(last_comm) & set(cur_comm)) 
            if num_sim_members > max_sim_members:
                switches += 1
            last_comm = cur_comm.copy()

    return switches

def get_all_comm_changes(s_month, e_month, max_sim_members):
    '''
    TODO: add docstring
    '''
    all_dpts, all_changes = all_departments(s_month, e_month), {}

    for dpt in all_dpts:
        all_changes[dpt] = find_comm_changes(s_month, e_month, dpt, max_sim_members)

    return all_changes

def get_bridges(s_month, e_month, undirected=False):
    '''
    TODO: add docstring
    '''

    graphs = unpack_months(s_month, e_month, undirected=undirected)
    grp_bridges, dpt_bridges = [], []

    for i in graphs[0]:
        grp_bridges.append(i.bridges())

    for i in graphs[1]:
        dpt_bridges.append(i.bridges())

    return grp_bridges, dpt_bridges

def graphs_with_bridges_cut(s_month, e_month, undirected=False):
    '''
    TODO: add docstring
    '''
    graphs = unpack_months(s_month, e_month, undirected=undirected)
    bridges = get_bridges(s_month, e_month, undirected=undirected)

    new_grp_graphs, new_dpt_graphs = [], []
    for g, b in zip(graphs[0], bridges[0]):
        new_g = g.copy()
        new_g.delete_edges(b)
        new_grp_graphs.append(new_g)

    for g, b in zip(graphs[1], bridges[1]):
        new_g = g.copy()
        new_g.delete_edges(b)
        new_dpt_graphs.append(new_g)

    return new_grp_graphs, new_dpt_graphs

def plot_centrality_month_bridges(func, s_month, e_month):
    '''
    TODO: add docstring
    '''

    group_graphs, dpt_graphs = graphs_with_bridges_cut(s_month, e_month)
    uncut_grp_graphs, uncut_dpt_graphs = unpack_months(s_month, e_month)

    grp_min_vals, grp_avg_vals, grp_max_vals = weekly_centrality_vals(func, group_graphs)
    dpt_min_vals, dpt_avg_vals, dpt_max_vals = weekly_centrality_vals(func, dpt_graphs)
    unc_grp_min_vals, unc_grp_avg_vals, unc_grp_max_vals = weekly_centrality_vals(func, uncut_grp_graphs)
    unc_dpt_min_vals, unc_dpt_avg_vals, unc_dpt_max_vals = weekly_centrality_vals(func, uncut_dpt_graphs)

    double_plot([grp_min_vals, grp_avg_vals, unc_grp_min_vals, unc_grp_avg_vals], [dpt_min_vals, dpt_avg_vals, unc_dpt_min_vals, unc_dpt_avg_vals])
    double_plot([grp_max_vals, unc_grp_max_vals], [dpt_max_vals, unc_dpt_max_vals])


def weekly_aggregate_global(func, s_month, e_month, undirected = False):
    '''
    TODO: add docstring
    '''

    group_graphs, dpt_graphs = graphs_with_bridges_cut(s_month, e_month, undirected=undirected)
    unc_grps, unc_dpts = unpack_months(s_month, e_month, undirected=undirected)
    grp_y_vals, dpt_y_vals = aggregate_weekly_vals(func, group_graphs), aggregate_weekly_vals(func, dpt_graphs)
    unc_grp_ys, unc_dpt_ys = aggregate_weekly_vals(func, unc_grps), aggregate_weekly_vals(func, unc_dpts)

    single_plot([dpt_y_vals, unc_dpt_ys])

def visualize_graphs(s_month, e_month, undirected = False):
    graphs = graphs_with_bridges_cut(s_month, e_month)[1]

    for g in graphs:
        layout = g.layout_fruchterman_reingold()
        igraph.plot(g, layout=layout)

def get_all_bridges(s_month, e_month):
    '''
    TODO: add docstring
    '''
    graphs = unpack_months(s_month, e_month)[1]
    bridges = get_bridges(s_month, e_month)[1]

    new_bridges = []
    bridge_counts = {}
    for g, b in zip(graphs, bridges):
        to_add = []
        for cs in bridges:
            for c in cs: 
                try:
                    e = g.es[c]
                    source = e.source_vertex['name']
                    target = e.target_vertex['name']
                    for i in [source, target]:
                        if i in bridge_counts:
                            bridge_counts[i] += 1
                        else:
                            bridge_counts[i] = 1
                    to_add.append((e.source_vertex['name'], e.target_vertex['name']))
                except:
                    pass
        new_bridges.append(to_add)

    return bridge_counts

if __name__ == "__main__":

    #directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "MergedWeek\Dept Only Graphs")
    #for entry in os.scandir(directory):
    #    if entry.path.endswith(".csv") and entry.is_file():
    #        make_gephi_csvs(entry.path)

    tik = time.time()
    bridges = get_all_bridges(1,8)
    tok = time.time()
    print(tok-tik)

    pass