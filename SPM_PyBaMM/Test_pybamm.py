# ----------------------------------------------
# run SPM in PyBaMM: 
# https://github.com/pybamm-team/PyBaMM
# ----------------------------------------------

import pybamm
import numpy as np
import matplotlib.pyplot as plt

#import pybamm.mz_develop.output_module as outmod

#%%

model = pybamm.lithium_ion.SPM()
param = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)

timestamps = [0, 5, 
              5.01, 30, 
              30.01, 35, 
              35.01, 60, 
              60.01, 65, 
              65.01, 90, 
              90.01, 95, 
              95.01, 120]
experiment = pybamm.Experiment(
    [
     (
      "Charge at 0.5 A for 5.0 seconds", 
      "Rest for 25.0 seconds",
      "Discharge at 0.5 A for 5.0 seconds",
      "Rest for 25.0 seconds",
      "Charge at 1.0 A for 5.0 seconds", 
      "Rest for 25.0 seconds",
      "Discharge at 1.0 A for 5.0 seconds",
      "Rest for 25.0 seconds",
      )
    ] * 1,
    period="0.001 second",
)

#model = pybamm.lithium_ion.DFN()
sim = pybamm.Simulation(
    model, experiment=experiment,
    parameter_values=param,
)

sim.solve()
sim.plot()
solution = sim.solution
#print(model.variable_names())
t = solution["Time [s]"].entries
V = solution['Terminal voltage [V]'].entries

indices = [int(x*1000) for x in timestamps]
voltages_at_timestamps = [V[i] for i in indices]
print(voltages_at_timestamps)