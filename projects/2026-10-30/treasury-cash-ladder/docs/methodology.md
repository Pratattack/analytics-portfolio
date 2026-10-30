# Formulation

Decision variables x4, x8 and x13 are nonnegative initial dollar allocations including the proportional upfront fee; c is idle cash. Their sum equals capital C. With bank-discount quotation d, quoted price per dollar of face is 1 − dT/360 for assumed T = 28, 56, 91 days. Factor fT = 1 / [(1 − dT/360)(1 + fee_bps/10000)].

For payment day k, c + sum of maturity receipts available by k − cumulative outflows by k >= reserve. All holdings mature by day 91; terminal cash is c + sum(fT*xT) − all outflows. Maximize this objective. Payments precede no later-day maturities. Same-day maturities precede payments.

Python uses scipy.optimize.linprog with HiGHS. The independent JavaScript implementation enumerates intersections of three binding inequalities with the capital equality, solves the resulting 4x4 systems and retains the best feasible vertex. The bounded feasible polytope guarantees a vertex optimum for a linear objective. Tied allocations can differ, so parity tests compare feasibility and objective rather than requiring an identical tied portfolio. Zero-yield cash, infeasible early payments and expensive-fee boundaries are checked.

Historical monthly quote sensitivities rerun the same hypothetical plan at each month’s last retrieved observation. They are not rolling realized returns or an executable backtest. No forecasts of future reinvestment rates are needed or implied.
