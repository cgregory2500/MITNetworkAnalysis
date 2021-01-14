import igraph, os, time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

from make_day_network import * 
from graph_storage import *
from graph_analysis import *
from _datetime import date

def create_dpt_vals_weekly(func, graphs, dpt_vals, week):
    '''
    TODO: add docstring
    '''
    weekly_vals = {}
    for graph in graphs:
        for v in graph.vs():
            if v['name'] in weekly_vals:
                weekly_vals[v['name']].append(func(v))
            else:
                weekly_vals[v['name']] = [func(v)]

    for dpt in weekly_vals:
        if dpt in dpt_vals:
            dpt_vals[dpt][week] = sum(weekly_vals[dpt])/len(weekly_vals[dpt])
        else:
            dpt_vals[dpt] = {week: sum(weekly_vals[dpt])/len(weekly_vals[dpt])}

    return dpt_vals

def department_weekly_vals(func, graphs):
    '''
    TODO: add docstring
    '''
    dpt_vals = {}

    week = 0
    while len(graphs) >= 7:
        dpt_vals = create_dpt_vals_weekly(func, graphs[:7], dpt_vals, week)
        graphs = graphs[6:]
        week += 1

    return dpt_vals

def plot_department_centralities_month(func, s_month, e_month, department1, department2):
    '''
    TODO: add docstring
    '''

    group_graphs, dpt_graphs = unpack_months(s_month, e_month)

    overall_vals = department_weekly_vals(func, dpt_graphs)

    dpt1_vals = overall_vals[department1]
    dpt2_vals = overall_vals[department2]

    double_plot([dpt1_vals], [dpt2_vals])

def create_plot(x_vals, y_vals, y_axis, x_axis, func_name, department):
    '''
    TODO: add docstring
    '''

    # resets the figure
    plt.clf()

    new_name= department.split('/')
    print(new_name[0])
    fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Graphs\Weekly Averaged {} of {} from January through July 2020.png".format(func_name, new_name[0]))

    plt.plot(y_vals)
    plt.ylabel(y_axis)
    plt.xlabel(x_axis)

    plt.suptitle("Weekly Averaged {} of {} from January through July 2020".format(func_name, new_name[0]))
    plt.savefig(fpath)


def plot_all_departments(func, s_month, e_month, func_name):
    '''
    TODO: add docstring
    '''
    dpt_graphs = unpack_months(s_month, e_month)[1]
    overall_vals = department_weekly_vals(func, dpt_graphs)

    for department in overall_vals:
        x_vals = [i for i in range(0, 35)]
        y_vals = []
        for week in x_vals:
            if week not in overall_vals[department]:
                y_vals.append(0)
            else:
                y_vals.append(overall_vals[department][week])
        create_plot(x_vals, y_vals, func_name, "Week", func_name, department)

def make_all_comms(s_month, e_month):
    '''
    TODO: add docstring
    '''
    date_to_comms = {}
    dpt_graphs = unpack_months(s_month, e_month, undirected = True)[1]
    community_analysis = [graph.community_multilevel() for graph in dpt_graphs]

    for graph, date in zip(community_analysis, all_dates(s_month, e_month)):
        date_to_comms[date] = graph

    return date_to_comms

def plot_communities(s_month, e_month):
    '''
    TODO: add docstring
    '''
    
    dpt_graphs = unpack_months(s_month, e_month, undirected = True)[1]
    community_analysis = [graph.community_multilevel() for graph in dpt_graphs]
    i = 0
    for graph, date in zip(dpt_graphs, all_dates(s_month, e_month)):
        print(i)
        i += 1

        comms = graph.community_multilevel()
        fpath_plot = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Communities/{} Department Community Graph groups-marked.png".format(date))
        igraph.plot(comms, target = fpath_plot, vertex_size=[10 for a in graph.vs], mark_groups = True)

        fpath_txt = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Communities/{} Department Community Graph Key groups-marked.txt".format(date))
        txt_file = open(fpath_txt, 'wt')
        txt_file.write(str(comms))
        txt_file.close()


if __name__ == "__main__":
    tik = time.time()
    plot_communities(1, 8)
    tok = time.time()
    print(tok-tik)
    pass