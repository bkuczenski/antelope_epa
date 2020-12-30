# EPA_PSM_Antelope

EPA Product System Modeling Hackathon - antelope branch.  

## Overview

The Product Systems being modeled in this project are the landing gear assemblies for an advanced fighter jet.  The model is built from a set of excel spreadsheets that describe the authentic bills of materials for these assemblies in a hierarchical fashion.

I use the disclosure framework outlined in [Disclosure of Product System Models in LCA](https://doi.org/10.1111/jiec.12810) to describe the derived product models in a structured, software-independent format including three lists of entities and three submatrices:

<img alt="Graphical depiction of an LCA disclosure" src="jie-disclosure_fig3.png" width=384>

In the current project, there is no foreground emissions data, so *d-iii* and *d-vi* are blank. Moreover, there is no authentic data on the physical characteristics of the parts, so the numeric values in *d-v* are mocked up.  However, the background terminations (i.e. *d-ii*) are hand-curated to be at least somewhat plausible.

My solution uses the Antelope framework to encode these PSMs as life cycle fragment trees, which are nestable acyclic directed graphs. Each "fragment" is an _observed_ link in a product model, and it functions as a parameterizable exchange.  The disclosures are then generated from traversals of the fragments.

## Components and set-up

The software components used in this entry are contained in two public repositories, and neither is on PyPi because I don't yet know how to use `setuptools`.

 * [Antelope foreground](https://github.com/AntelopeLCA/foreground), Tools for building LCA models from observation of model "fragments"
 * [lca_disclosures](https://github.com/AntelopeLCA/lca_disclosures). Derived from J. Joyce's [original software](https://github.com/pjamesjoyce/lca_disclosures) 
 of the same name.

The requirements for these tools are not light:

 - python 3.6+
 - scipy (required by `lca_disclosures` for some matrix computation)
 - pandas (required by `lca_disclosures` for excel output)
 - lxml (for reading ELCD files)
 - plus some other miscellaneous packages.

This worked on my system in a new virtualenv.

### Installation

For the moment, `pip install -r requirements.txt` should work, as long as I get around to properly releasing 
`lca_disclosures` and `antelope_foreground`.


### Configuration and run

The following steps were sufficient on my system:

    $ mkvirtualenv -p /usr/bin/python3.7 hackathon
    (hackathon)$ pip install -r requirements.txt
    (hackathon)$ export EPA_FOREGROUND=/path/to/LCAproductsystemassembly_resources/data
    (hackathon)$ python generate_disclosures.py

# Documentation

Coming soon!