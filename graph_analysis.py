import igraph, os, time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from make_day_network import * 
from graph_storage import *

def averaged_centrality(func, s_date, e_date):
    '''
    Input: a function that acts on the vertices of the graph
    a string containing the starting date
    a string containing the ending date

    Output: two dictionaries,
    one dictionary mapping group_ids to average centrality over time period based on the metric 
    one dictionary mapping departments to average centrality over specified period based on the metric

    possible functions include: degree, betweenness, closeness, eigenvector_centrality
    '''

    group_graphs, dpt_graphs = make_day_networks(s_date, e_date)
    group_degrees, dpt_degrees = {}, {}

    for graph in group_graphs:
        for grp in graph.vs:
            if grp['id'] in group_degrees:
                group_degrees[grp['id']].append(func(grp))
            else:
                group_degrees[grp['id']] = [func(grp)]

    for graph in dpt_graphs:
        for dpt in graph.vs:
            if dpt['name'] in dpt_degrees:
                dpt_degrees[dpt['name']].append(func(dpt))
            else:
                dpt_degrees[dpt['name']] = [func(dpt)]

    for i in group_degrees:
        group_degrees[i] = sum(group_degrees[i])/len(group_degrees[i])

    for i in dpt_degrees:
        dpt_degrees[i] = sum(dpt_degrees[i])/len(dpt_degrees[i])

    return group_degrees, dpt_degrees

def calc_centrality_min_avg_max(func, graph):
    '''
    TODO: add docstring
    '''
    vals = []

    for grp in  graph.vs:
        vals.append(func(grp))
    
    return min(vals), sum(vals)/len(vals), max(vals)


def weekly_centrality_vals(func, graphs):
    '''
    TODO: add docstring
    '''
    j = 0
    weekly_mins, weekly_avgs, weekly_maxs = [], [], []
    new_min_val, new_avg_val, new_max_val = [], [], []
    while j < len(graphs):
        if j % 7 == 0 and j != 0:
            weekly_mins.append(sum(new_min_val)/7)
            weekly_avgs.append(sum(new_avg_val)/7)
            weekly_maxs.append(sum(new_max_val)/7)
            new_min_val, new_avg_val, new_max_val = [], [], []
        min_val, avg_val, max_val = calc_centrality_min_avg_max(lambda v: v.degree(), graphs[j])
        new_min_val.append(min_val)
        new_avg_val.append(avg_val)
        new_max_val.append(max_val)
        j += 1

    return weekly_mins, weekly_avgs, weekly_maxs

def plot_centrality(func, s_date, e_date, metric_name):
    '''
    Input: a function that acts on the vertices of the graph
    a string containing the starting date
    a string containing the ending date
    a string for the label on the y-axis in order to indicate what is being measured

    Output: None

    Plots a bar graph of the centralities based on the function passed in
    One bar graph for the group network 
    One bar graph for the department network
    '''
    grp_centralities, dpt_centralities = averaged_centrality(func, s_date, e_date)
    grp_y_vals, grp_x_vals = [], []
    dpt_y_vals, dpt_x_vals = [], []
    dpt_key = {}

    for grp in grp_centralities:
        grp_x_vals.append(grp)
        grp_y_vals.append(grp_centralities[grp])

    for i, dpt in enumerate(dpt_centralities):
        dpt_key[i] = dpt
        dpt_y_vals.append(dpt_centralities[dpt])
        dpt_x_vals.append(i)

    fig, axs = plt.subplots(2)
    axs[0].bar(grp_x_vals, grp_y_vals)
    axs[1].bar(dpt_x_vals, dpt_y_vals)
    plt.ylabel(metric_name)
    print(dpt_key)
    plt.show()

def plot_centrality_month(func, s_month, e_month):
    '''
    TODO: add docstring
    '''

    group_graphs, dpt_graphs = unpack_months(s_month, e_month)

    grp_min_vals, grp_avg_vals, grp_max_vals = weekly_centrality_vals(func, group_graphs)
    dpt_min_vals, dpt_avg_vals, dpt_max_vals = weekly_centrality_vals(func, dpt_graphs)

    double_plot([grp_min_vals, grp_avg_vals], [dpt_min_vals, dpt_avg_vals])
    double_plot([grp_max_vals], [dpt_max_vals])

def densities(s_date, e_date):
    '''
    Input: a string containing the starting date
    a string containing the ending date

    Output: an array of tuples for the densities on that day
    '''
    group_graphs, dpt_graphs = unpack_months(s_month, e_month)
    grp_densities, dpt_densities = [], []

    for grp, dpt in zip(group_graphs, dpt_graphs):
        grp_densities.append(grp.density())
        dpt_densities.append(dpt.density())

    return grp_densities, dpt_densities
    
def plot_densities(s_month, e_month):
    '''
    Input: int for the s_month and e_month

    Output: None

    Plots a graph of the densities for both types of graphs
    '''
    group_graphs, dpt_graphs = unpack_months(s_month, e_month)

    grp_densities, dpt_densities = [g.density() for g in group_graphs], [g.density() for g in dpt_graphs]

    double_plot([grp_densities], [dpt_densities])

def plot_global_prop(func, s_month, e_month):
    '''
    TODO: add docstring
    '''
    grp_y_vals, dpt_y_vals = [], []

    group_graphs, dpt_graphs = unpack_months(s_month, e_month)

    for grp, dpt in zip(group_graphs, dpt_graphs):
        grp_y_vals.append(func(grp))
        dpt_y_vals.append(func(dpt))
    
    double_plot([grp_y_vals], [dpt_y_vals])

def aggregate_weekly_vals(func, graphs):
    '''
    TODO: add docstring
    '''
    j= 0
    weekly_vals = []
    new_val = []
    while j < len(graphs):
        if j % 7 == 0 and j != 0:
            weekly_vals.append(sum(new_val)/7)
            new_val = []
        new_val.append(func(graphs[j]))
        j += 1
    
    return weekly_vals

def weekly_aggregate_global(func, s_month, e_month, undirected = False):
    '''
    TODO: add docstring
    '''

    group_graphs, dpt_graphs = unpack_months(s_month, e_month, undirected=undirected)
    grp_y_vals, dpt_y_vals = aggregate_weekly_vals(func, group_graphs), aggregate_weekly_vals(func, dpt_graphs)

    single_plot([dpt_y_vals])

def plot_global_prop_month(func, s_month, e_month, undirected = False):
    '''
    TODO: add docstring
    '''
    grp_y_vals, dpt_y_vals = [], []

    group_graphs, dpt_graphs = unpack_months(s_month, e_month, undirected = undirected)

    for grp, dpt in zip(group_graphs, dpt_graphs):
        grp_y_vals.append(func(grp))
        dpt_y_vals.append(func(dpt))
    
    double_plot([grp_y_vals], [dpt_y_vals])

def double_plot(grp_ys, dpt_ys):
    '''
    TODO: add docstring
    '''
    x_vals = [i for i in range(len(grp_ys[0]))]
    fig, axs = plt.subplots(2)

    for ys in grp_ys:
        axs[0].plot(x_vals, ys)
    for ys in dpt_ys:
        axs[1].plot(x_vals, ys)
    
    plt.xlabel("Date")
    plt.show()

def single_plot(dpt_ys):
    '''
    TODO: add docstring
    '''
    x_vals = [i for i in range(len(dpt_ys[0]))]

    for ys in dpt_ys:
        plt.plot(ys)

    plt.xlabel("Date")
    plt.show()

if __name__ == "__main__":

    tik = time.time()
    weekly_aggregate_global(lambda v: len(v.bridges()), 1, 8)
    tok = time.time()

    print(tok-tik)
