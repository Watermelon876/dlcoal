
from __future__ import division

from math import *

from rasmus import stats, treelib
import compbio.coal
from compbio.coal import *

import dlcoal
from dlcoal.ctypes_export import *


#=============================================================================
# export c functions

ex = Exporter(globals())
export = ex.export


if dlcoal.dlcoalc:

    # replace python function with c
    export(dlcoal.dlcoalc, "prob_coal_counts", c_double,
           [c_int, "a", c_int, "b", c_double, "t", c_double, "n"])
    compbio.coal.prob_coal_counts = prob_coal_counts

    export(dlcoal.dlcoalc, "prob_multicoal_recon_topology", c_double,
           [c_int_p, "ptree", c_int, "nnodes", c_int_p, "recon", 
            c_int_p, "pstree", c_int, "nsnodes", c_double_p, "sdists",
            c_double_p, "popsizes"])

    export(dlcoal.dlcoalc, "prob_locus_coal_recon_topology", c_double,
           [c_int_p, "ptree", c_int, "nnodes", c_int_p, "recon", 
            c_int_p, "plocus_tree", c_void_p, "iltree", c_int, "nlnodes", 
            c_double_p, "popsizes", c_double_p, "stimes",
            c_int_p, "daughters", c_int, "ndaughters"])

    export(dlcoal.dlcoalc, "prob_locus_coal_recon_topology_samples", c_double,
           [c_int_p, "ptree", c_int, "nnodes", c_int_p, "recon", 
            c_int_p, "plocus_tree", c_int, "nlocus_nodes", 
            c_int_p, "locus_recon", c_int_p, "locus_events",
            c_double_p, "popsizes", 
            c_int_p, "pstree", c_int, "nsnodes", c_double_p, "stimes",
            c_int_p, "daughters", c_int, "ndaughters", 
            c_double, "birth", c_double, "death",
            c_int, "nsamples", c_double, "pretime", c_double, "premean"])




pmrt = compbio.coal.prob_multicoal_recon_topology
def prob_multicoal_recon_topology(tree, recon, stree, n,
                                  lineages=None, top_stats=None):

    ptree, nodes, nodelookup = dlcoal.make_ptree(tree)
    pstree, snodes, snodelookup = dlcoal.make_ptree(stree)
    recon2 = dlcoal.make_recon_array(tree, recon, nodes, snodelookup)

    popsizes = compbio.coal.init_popsizes(stree, n)
    popsizes2 = [popsizes[snode.name] for snode in snodes]
    sdists = [snode.dist for snode in snodes]
    
    p = dlcoal.dlcoalc.prob_multicoal_recon_topology(
        c_list(c_int, ptree), len(nodes), c_list(c_int, recon2),
        c_list(c_int, pstree), len(snodes), c_list(c_double, sdists),
        c_list(c_double, popsizes2))
    
    return p
compbio.coal.prob_multicoal_recon_topology = prob_multicoal_recon_topology




def prob_locus_coal_recon_topology(tree, recon, locus_tree, n, daughters):

    ptree, nodes, nodelookup = dlcoal.make_ptree(tree)
    pltree, lnodes, lnodelookup = dlcoal.make_ptree(locus_tree)
    recon2 = dlcoal.make_recon_array(tree, recon, nodes, lnodelookup)

    popsizes = compbio.coal.init_popsizes(locus_tree, n)
    popsizes2 = [popsizes[lnode.name] for lnode in lnodes]

    ltimes = treelib.get_tree_timestamps(locus_tree)
    ltimes2 = [ltimes[lnode] for lnode in lnodes]

    daughters2 = [lnodelookup[lnode] for lnode in daughters]
    
    p = dlcoal.dlcoalc.prob_locus_coal_recon_topology(
        c_list(c_int, ptree), len(nodes), c_list(c_int, recon2),
        c_list(c_int, pltree), 0, len(lnodes),
        c_list(c_double, popsizes2), c_list(c_double, ltimes2),
        c_list(c_int, daughters2), len(daughters))
    
    return p


def prob_locus_coal_recon_topology_samples(
    coal_tree, coal_recon,
    locus_tree, locus_recon, locus_events, locus_popsizes,
    stree, stimes,
    daughters,
    birth, death, nsamples, pretime=None, premean=100.0):

    if pretime is None:
        pretime = -1
    

    ptree, nodes, nodelookup = dlcoal.make_ptree(coal_tree)
    pltree, lnodes, lnodelookup = dlcoal.make_ptree(locus_tree)
    pstree, snodes, snodelookup = dlcoal.make_ptree(stree)
    
    crecon2 = dlcoal.make_recon_array(
        coal_tree, coal_recon, nodes, lnodelookup)
    lrecon2 = dlcoal.make_recon_array(
        locus_tree, locus_recon, lnodes, snodelookup)
    levents2 = dlcoal.make_events_array(lnodes, locus_events)

    locus_popsizes = compbio.coal.init_popsizes(locus_tree, locus_popsizes)
    popsizes2 = [locus_popsizes[lnode.name] for lnode in lnodes]

    stimes2 = [stimes[snode] for snode in snodes]

    daughters2 = [lnodelookup[lnode] for lnode in daughters]
    
    p = dlcoal.dlcoalc.prob_locus_coal_recon_topology_samples(
        c_list(c_int, ptree), len(nodes), c_list(c_int, crecon2),
        c_list(c_int, pltree), len(lnodes),
        c_list(c_int, lrecon2), c_list(c_int, levents2),
        c_list(c_double, popsizes2),
        c_list(c_int, pstree), len(snodes), c_list(c_double, stimes2),
        c_list(c_int, daughters2), len(daughters),
        birth, death, nsamples, pretime, premean)

    return p
