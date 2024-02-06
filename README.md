# wind_gates_search_states
Repository for creating figures associated with Stupski and van Breugel 2024

# Overview
This repository contains the Jupyter notebooks necessary to recreate the figures associated with "Wind Gates Search States in Free Flight"
The current preprint can be found at: https://www.biorxiv.org/content/10.1101/2023.11.30.569086v2.abstract

Notebooks are written in Python 2 and 3, using standard libraries, e.g. matplotlib, pandas, numpy etc.  There is however one more unique dependency to run the notebooks as they are written.  This dependency, FigureFirst, an Inkscape plugin that links figures made in jupyter notebooks directly into an inkscape .svg.  FigureFirst and its installation instructions can be found here.  https://github.com/FlyRanch/figurefirst

# Contents
This repository is meant to function as a complement to the full data hosted on Dryad here:  DRYAD_LINK

# Generating Figures
To run the figure notebooks you only need data from the following repositories hosted on Dryad: figure_first_templates, trimmed_data, trajectories_for_figures, main_text, supplement.  If placed in a single directory, the internal pathing on the jupyter notebooks should allow recreation of all of the figures.  The jupyter notebooks can be found here, in this repository, and also in the Dryad repository.  

# Raw data and data processing
While the figure notebooks are set up to run with the trimmed and processed data, the raw data is also available on dryada in it's original .braidz file format (for more information visit https://strawlab.org/braid/) and the code necessary to process the raw tracking data into trimmed data sets. Each nights experiment has its own directory  within the "raw" directory.  In each recording bout  there is a file ending in a .braidz extension, this contains raw tracking information.  With it inside the same directory is an associated ROS .bag file which contains information from each of the trigger events throughout the nights recording.  To go from a raw data file to a trimmed .csv first convert the .bag file into a hdf5 file using the "bag2hdf5.py" script in the auxillary_code directory.  Then to trim the raw data to include only relevant trigger events run data_trimming.py <raw_tracking.braidz> <trigger_events.hdf5>.  Each nights trimmed output is then simply concatenated together to generate the trimmed data sets found in the trimmed data folder.  Any further processing is handled within the notebooks used to generate the figures.   

# Repository layout

.
└── wind_gates_search_states/

    ├── auxillary_code/
    │   ├── bag2hdf5.py
    │   └── data_trimming.py
    ├── figure_first_templates/
    │   ├── altitude_control.svg
    │   ├── double_flash_genetic_control.svg
    │   ├── etoh_anemo_for_supp.svg
    │   ├── f1_part1.svg
    │   ├── f1_part2.svg
    │   ├── f2.svg
    │   ├── f3.svg
    │   ├── f4.svg
    │   ├── f5.svg
    │   ├── f6.svg
    │   ├── genetic_control_supplement.svg
    │   ├── s7.svg
    │   ├── s8.svg
    │   └── still_air_with_controls.svg
    ├── main_text/
    │   ├── f1_anemotaxis.ipynb
    │   ├── f1_object_approach.ipynb
    │   ├── f2.ipynb
    │   ├── f3.ipynb
    │   ├── f4.ipynb
    │   ├── f5.ipynb
    │   └── f6_and_s8_s9.ipynb
    ├── raw_data/
    │   ├── Orco_CsChrimson_double_flash
    │   ├── Orco_CsChrimson_Laminar
    │   ├── Orco_CsChrimson_no_atr_control
    │   ├── Orco_CsChrimson_Object_Approach
    │   ├── Orco_CsChrimson_Still_air
    │   ├── Orco_CsChrimson_still_air_optic_flow_control
    │   ├── UAS_CsChrimson_heterozygote_control
    │   ├── vanBreugel_2014_reanalysis
    │   ├── Wild_type_control_double_flash
    │   ├── Wild_type_control_laminar_wind
    │   ├── Wild_type_control_still_air
    │   ├── Wild_type_object_approach_clean_air
    │   └── Wild_type_object_approach_ethanol
    ├── supplement/
    │   ├── S2.ipynb
    │   ├── S3.ipynb
    │   ├── S4.ipynb
    │   ├── S6.ipynb
    │   └── S7.ipynb
    ├── trajectories_for_figures/
    │   ├── double_flash/
    │   │   ├── double_pulse_sample_traj.csv
    │   │   ├── no_pulse_example_trajs.csv
    │   │   └── single_pulse_example.csv
    │   ├── still_air/
    │   │   ├── sacc_for_ang-vel_rep.csv
    │   │   ├── single_pulse.csv
    │   │   ├── traj_1.csv
    │   │   ├── traj_2.csv
    │   │   ├── traj_3.csv
    │   │   ├── traj_4.csv
    │   │   ├── traj_5.csv
    │   │   ├── traj_6.csv
    │   │   ├── traj_7.csv
    │   │   ├── traj_8.csv
    │   │   ├── traj_9.csv
    │   │   ├── traj_10.csv
    │   │   ├── traj_11.csv
    │   │   └── traj_12.csv
    │   ├── object1.csv
    │   ├── object2.csv
    │   ├── object3.csv
    │   ├── orco_laminar1.csv
    │   ├── orco_traj2.csv
    │   ├── orco_traj3.csv
    │   ├── wt_laminar1.csv
    │   ├── wt_traj2.csv
    │   └── wt_traj3.csv
    └── trimmed_data/
        ├── main/
        │   ├── etoh_object.csv
        │   ├── flash_object_approach.csv
        │   ├── no_etoh_object.csv
        │   ├── OrcoCshrimson_laminar_wind_merged.csv
        │   ├── Orco_CsChrimson_still_air_merged.csv
        │   ├── sham_object_approach.csv
        │   ├── wild_type_laminar_merged.csv
        │   └── wildtype_still_air_merged.csv
        ├── mGSD_annotations/
        │   ├── lw0_orco_sacc.csv
        │   ├── lw0_wt_sacc.csv
        │   ├── lw100_orco_sacc.csv
        │   ├── lw100_wt_sacc.csv
        │   ├── modified_GSD_laminar_wind_orco.csv
        │   ├── modified_GSD_laminar_wind_wt.csv
        │   ├── modified_GSD_no_wind_orco.csv
        │   ├── modified_GSD_wt_no_wind.csv
        │   ├── nw0_orco_sacc.csv
        │   ├── nw0_wt_sacc.csv
        │   ├── nw100_orco_sacc.csv
        │   └── nw100_wt_sacc.csv
        ├── supp/
        │   ├── CsChrimson_hets.csv
        │   ├── fly_trajec_data_all_etoh.hdf
        │   ├── fly_traject_data_noodor_all.hdf
        │   ├── no_wind_no_grid_orco.csv
        │   └── OrcoCsChrimson_no_atr.csv
        └── trimmed_double_flash/
            ├── double_flash_mean_time_trace_qc.csv
            ├── no_wind_wt_shams_merged_distilled.csv
            ├── orco_double_pulse_distilled_response.csv
            ├── orco_shams_distilled_merged.csv
            ├── orco_single_distilled.csv
            ├── sham_merged_mean_time_trace.csv
            ├── single_flash_wt_distilled.csv
            ├── single_pulse_mean_time_trace.csv
            └── wt_double_flash_distilled.csv


