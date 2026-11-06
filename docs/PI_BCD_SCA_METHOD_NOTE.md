# Causal PI-BCD-SCA adaptation: implementation and validation status

## Scope

The code implements a project-specific, causal one-slot adaptation inspired by the penalty-iteration / block-coordinate-descent / successive-convex-approximation framework. It is **not** an exact reproduction of the cited uplink optimization paper.

## Information contract

The solver reads only the current environment state: current C-UAV state, current M-UAV positions/velocities and cluster centers, current GU positions and QoS demands, current association, current outage ages, and current radio configuration. It does not read future user positions, future arrivals, or future channel states.

## Per-slot objective

For current active users, the exact current-slot P1 utility is evaluated using the same environment radio functions and the same ROCS-0 scheduler:

\[
U_n = C_n - \lambda_r \bar O_{n+1},
\]

where \(C_n\) is the actual minimum-QoS completion ratio returned by the scheduler and \(\bar O_{n+1}\) is the mean post-slot consecutive under-service age. The C-UAV action is previewed through the same physical motion projector; the M-UAV transition is previewed through the same acceleration-limited cluster tracking.

## Blocks and local convex subproblems

The action is split into Motion \(a_M\in\mathbb R^3\) and Power scores \(a_P\in\mathbb R^4\). For each block, central finite differences estimate a local gradient and diagonal curvature of the exact P1 preview. The solver constructs a concave diagonal-quadratic surrogate

\[
\widehat U(\Delta a)=U(a)+g^T\Delta a-\tfrac12\Delta a^T D\Delta a,
\qquad D\succ0,
\]

and solves its box/trust-region QP by the closed-form coordinate solution. A proximal coefficient \(\rho\) regularizes the step. Motion and Power blocks are updated alternately; a candidate is accepted only if the exact P1 preview improves. The environment remains responsible for the same hard physical feasibility projection.

## Required pilot outputs

- Mean, P95 and maximum solver time per 0.5-s slot.
- Solver-success rate (finite, in-bounds action).
- Physical no-projection rate.
- Number of objective evaluations per slot.
- P1 improvement, QSR and Goodput during the pilot.

A P95 solver time above 0.5 s means the method does not meet the per-slot real-time budget on that machine. Do not claim real-time feasibility in that case; report it as an offline/slow optimization baseline or revise the solver.

## Caveat

The local diagonal SCA surrogate is a deliberately low-cost approximation of the exact one-slot P1 preview. It is not a global optimality certificate. The pilot must be reviewed for numerical stability, feasible action ratio and runtime before a 30/100-seed performance comparison. The paper should describe this as a causal adaptation, not a verbatim algorithm reproduction.
