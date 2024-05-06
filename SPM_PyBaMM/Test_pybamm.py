# ----------------------------------------------
# run SPM in PyBaMM: 
# https://github.com/pybamm-team/PyBaMM
# ----------------------------------------------

import pybamm
import numpy as np
import matplotlib.pyplot as plt

#import pybamm.mz_develop.output_module as outmod


model = pybamm.lithium_ion.SPM({"SEI": "ec reaction limited"})
param = pybamm.ParameterValues("Mohtat2020")
param.update({"SEI kinetic rate constant [m.s-1]": 1e-14})

timestamps = [0, 5, 
              5.01, 30, 
              30.01, 35, 
              35.01, 60, 
              60.01, 65, 
              65.01, 90, 
              90.01, 95, 
              95.01, 120]
pulse_test = pybamm.Experiment(
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


N = 10
cccv_experiment = pybamm.Experiment(
    [
        (
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/50",
            "Discharge at 1C until 3V",
            "Rest for 1 hour",
        )
    ]
    * N
)
charge_experiment = pybamm.Experiment(
    [
        (
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/50",
        )
    ]
)
rpt_experiment = pybamm.Experiment([("Discharge at C/3 until 3V",)])
def generate_cell_data(cycle_num = 5):
    cccv_sols = []
    charge_sols = []
    rpt_sols = []
    sim = pybamm.Simulation(
    model, experiment=cccv_experiment, parameter_values=param
    )
    sim = pybamm.Simulation(
    model, experiment=cccv_experiment, parameter_values=param
    )
    cccv_sol = sim.solve()
    sim = pybamm.Simulation(
        model, experiment=charge_experiment, parameter_values=param
    )
    charge_sol = sim.solve(starting_solution=cccv_sol)
    sim = pybamm.Simulation(
        model, experiment=rpt_experiment, parameter_values=param
    )
    rpt_sol = sim.solve(starting_solution=charge_sol)
    cccv_sols = []
    charge_sols = []
    rpt_sols = []
    M = 5
    for i in range(M):
        if i != 0:  # skip the first set of ageing cycles because it's already been done
            sim = pybamm.Simulation(
                model, experiment=cccv_experiment, parameter_values=param
            )
            cccv_sol = sim.solve(starting_solution=rpt_sol)
            sim = pybamm.Simulation(
                model, experiment=charge_experiment, parameter_values=param
            )
            charge_sol = sim.solve(starting_solution=cccv_sol)
            sim = pybamm.Simulation(
                model, experiment=rpt_experiment, parameter_values=param
            )
            rpt_sol = sim.solve(starting_solution=charge_sol)
        cccv_sols.append(cccv_sol)
        charge_sols.append(charge_sol)
        rpt_sols.append(rpt_sol)
    return rpt_sol, rpt_sols

rpt_sol, rpt_sol_list = generate_cell_data()

cccv_cycles = []
cccv_capacities = []
rpt_cycles = []
rpt_capacities = []
M = 5
for i in range(M):
    for j in range(N):
        cccv_cycles.append(i * (N + 2) + j + 1)
        start_capacity = (
            rpt_sol.cycles[i * (N + 2) + j]
            .steps[2]["Discharge capacity [A.h]"]
            .entries[0]
        )
        end_capacity = (
            rpt_sol.cycles[i * (N + 2) + j]
            .steps[2]["Discharge capacity [A.h]"]
            .entries[-1]
        )
        cccv_capacities.append(end_capacity - start_capacity)
    rpt_cycles.append((i + 1) * (N + 2))
    start_capacity = rpt_sol.cycles[(i + 1) * (N + 2) - 1][
        "Discharge capacity [A.h]"
    ].entries[0]
    end_capacity = rpt_sol.cycles[(i + 1) * (N + 2) - 1][
        "Discharge capacity [A.h]"
    ].entries[-1]
    rpt_capacities.append(end_capacity - start_capacity)


sol = rpt_sol_list[0]
sim = pybamm.Simulation(
        model, experiment=pulse_test,
        parameter_values=param,
    )
solution_pulse_test = sim.solve(starting_solution=sol)

# Extract start and end time of pulse test
start_time_pulse_test = solution_pulse_test["Time"].entries[0]
end_time_pulse_test = solution_pulse_test["Time"].entries[-1]

# Plot only the time from the start of the pulse test to the end of the pulse test
solution_pulse_test.plot(time=(start_time_pulse_test, end_time_pulse_test))