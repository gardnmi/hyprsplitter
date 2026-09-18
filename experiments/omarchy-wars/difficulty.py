"""Short warmup followed by grouped attacks; full pressure by one minute."""
def settings(seconds):
 t=max(0,min(1,seconds/60))
 return dict(rooms=min(8,2+2*int(max(0,seconds)/12)),
             ships=1 if seconds<12 else 2 if seconds<30 else 3,
             cap=int(8+36*t),speed=.50+.60*t,
             reinforce_low=9-6*t,reinforce_high=12-7*t,
             fire_interval=5-3*t,bullet_speed=145+105*t,
             node_hp=10+int(12*t),can_shoot=seconds>=12,
             respawn_low=5-3*t,respawn_high=10-6*t)
