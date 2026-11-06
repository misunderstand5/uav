import sys
sys.path.insert(0, '.')
from uavqos import paper_final_presets as PF

for name in ['paper_joint_sac_current_pm_config', 'paper_fair_joint_sac_config',
             'paper_cda_sac_adapted_fixed500_config']:
    try:
        cfg = getattr(PF, name)(seed=7)
        PF.validate_fixed500_dynamic_workload_contract(cfg)
        print(name, 'OK hidden', cfg.sac.hidden_dim, 'motion', cfg.sac.motion_hidden_dim,
              'map', cfg.env.area_half_width_m)
    except Exception as e:
        print(name, 'FAIL', type(e).__name__, e)
