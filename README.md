# wind_gates_search_states
Repository for creating figures associated with Stupski and van Breugel 2024

# Overview
This repository contains the Jupyter notebooks necessary to recreate the figures associated with "Wind Gates Search States in Free Flight"
The current preprint can be found at: https://www.biorxiv.org/content/10.1101/2023.11.30.569086v2.abstract

Notebooks are written in Python 2 and 3, using standard libraries, e.g. matplotlib, pandas, numpt etc.  There is however one more unique dependency to run the notebooks as they are written.  This dependency, FigureFirst, an Inkscape plugin that links figures made in jupyter notebooks directly into an inkscape .svg.  FigureFirst and its installation instructions can be found here.  https://github.com/FlyRanch/figurefirst

# Contents
This repository is meant to function as a complement to the full data hosted on Dryad here:  DRYAD_LINK

To run the notebooks you only need data from the following repositories hosted on Dryad: figure_first_templates, trimmed_data, trajectories_for_figures, main_text, supplement.  If placed in a single directory internal pathing on the jupyter notebooks should allow recreation of all of the figures.  The jupyter notebooks can be found here, in this repository and also in the Dryad repository.  

Also found on Dryad are two other directpries for the curious reader:  auxillary_code and raw_data.  The former contains the code necessary to trim down the raw braid recordings and Ros bag files into the trimmed data sets.  It also contains code for converting .bag files into hdf5 files for easier use.  The latter is the raw .braidz data and .bag files from every data set that contributes to this paper before it has been trimmed or quality controlled in any way. 

# 
