# Fixed-500 m map with preserved dynamic-user workload

## 1. What changes from one training episode to another?

The service-area geometry does **not** change. Every episode uses the same square
`[-250, 250] m x [-250, 250] m`, i.e. 500 m x 500 m, and exactly four active
M-UAVs. Map-width and relay-count domain randomization are disabled.

The exogenous ground-user realization does change by design. The training runner
uses `environment_seed = training_seed * 100000 + episode`, so each episode gets
its own reproducible user realization while the map and fleet remain fixed.

## 2. QoS tiers are sampled using probabilities, not fixed quotas

Each newly created GU session independently samples one tier:

| Minimum QoS tier | Sampling probability | Expected count among the initial 20 users |
|---|---:|---:|
| 0.7 Mbps | 45% | 9 |
| 2.0 Mbps | 35% | 7 |
| 2.5 Mbps | 20% | 4 |

These are probabilities, **not exact per-episode quotas**. A particular 20-user
initialization may contain, for example, 11 / 6 / 3 users rather than exactly
9 / 7 / 4. New arrivals use the same categorical distribution. Once a session
is created, its selected minimum QoS remains fixed until that session departs.

## 3. User positions and motion

- On session creation, the user's initial `(x,y)` position is sampled uniformly
  over the fixed 500 m square; each coordinate lies in `[-250,250] m`.
- User motion follows the retained `paper_iid_slot` model. At each 0.5 s slot,
  speed and heading are resampled independently, with speed in `[0,6] m/s` and
  heading in `[-pi,pi]`; the user moves and reflects at the square boundary.
- `hotspot_migration` remains disabled. No migrating hotspot is introduced.

## 4. Dynamic user population

- The episode starts with 20 baseline users. They remain active for the entire
  episode (`dynamic_baseline_users_persistent=True`).
- Additional users arrive according to a four-stage, non-homogeneous Poisson
  session-arrival process. Stage boundaries are sampled per episode within the
  configured physical-time windows:
  - normal ends at 36--44 s;
  - ramp ends at 96--104 s;
  - peak ends at 136--144 s;
  - recovery continues to 200 s.
- Arrival rates are `(0.03, 1.35, 0.10, 0.0)` users/s for normal, ramp, peak,
  and recovery, respectively.
- Temporary session duration is `45 s + Gamma(shape=2, scale=12.5 s)`, clipped
  to `[45,120] s`. Expired sessions depart; free user slots can be reused.
- The simulator supports at most 130 simultaneous users.

This produces time-varying active-user counts without changing map size or the
number of M-UAVs. It is part of the intended high-load communication scenario.

## 5. M-UAV clustering and motion are retained

At each slot, active users are clustered using the current user positions. The
cluster centroid is weighted by each user's fixed minimum-QoS demand. A Hungarian
matching step associates the resulting clusters with the four physical M-UAVs.
Each M-UAV then moves toward its matched cluster center under the configured
25 m/s speed and 5 m/s^2 acceleration limits. The M-UAVs do not teleport to the
centers and their number does not change.

## 6. Fixed-map guard

The final H128 preset and training launcher enforce:

- `area_half_width_m = 250.0`;
- map-width choices exactly `(500.0,)`;
- `training_domain_randomization_interval = 0`;
- relay-count choices exactly `(4,)`;
- `training_topology_exposure_interval = 0`;
- `max_relays = initial_active_relays = min_active_relays = 4`.

The training launcher checks all 400 episode configurations before starting a
long run. Unit tests additionally simulate a full 400-slot environment episode
to verify that user arrivals/departures and M-UAV cluster tracking still occur.
