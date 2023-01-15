# SOCIOPHYSICS II
Welcome to the Pedestrian Movement Analysis and Simulation project!

In this project, we use data from pedestrian movement along a platform to analyze and simulate the flow of people in different zones of the platform. We use three different Markov chains to model the movement of pedestrians, taking into account the number of people in each zone and the effect this has on the probability of going to that zone.

To get started, you will need to install the following dependencies:

1. NumPy: a powerful numerical computing library for Python
2. Pandas: a library for data manipulation and analysis
3. Matplotlib: a library for creating visualizations of data
4. Seaborn: a library for creating more advanced visualizations

Once you have installed the dependencies, you can run the code in the matrix_generator.ipynb file in the matrix_generator folder to perform the analysis and then run the simulator.ipynb in the simulator folder to start the simulation. The code will load the data from the pedestrian_data.csv file and perform the following steps:

1. Explore the data and visualize the distribution of pedestrian movement across the platform.
2. Fit the three different Markov chains to the data and compare the results.
3. Use the best-performing Markov chain to simulate the movement of pedestrians on the platform, taking into account the number of people in each zone.
4. Visualize the results of the simulation and compare them to the actual data.

We hope that this project will provide insight into the movement of pedestrians on a platform and enable better planning and management of pedestrian flow. We welcome feedback and contributions from the community to improve and expand upon this work.
