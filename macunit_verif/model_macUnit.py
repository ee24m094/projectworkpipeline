# model for increment alone

import cocotb
from cocotb_coverage.coverage import *

counter_coverage = coverage_section(
    CoverPoint('top.load_A_a', vname='load_A_a', bins = list(range(0x0000,0x1000))),
    CoverPoint('top.load_B_b', vname='load_B_b', bins = list(range(0x0000,0x1000))),
    CoverPoint('top.load_C_c', vname='load_C_c', bins = list(range(0x00000000,0x10000000))),
    CoverPoint('top.load_s1_or_s2_sel', vname='load_s1_or_s2_sel', bins = list(range(0,2))),
    CoverPoint('top.EN_load_A', vname='EN_load_A', bins = list(range(0,2))),
    CoverPoint('top.EN_load_B', vname='EN_load_B', bins = list(range(0,2))),
    CoverPoint('top.EN_load_C', vname='EN_load_C', bins = list(range(0,2))),
    CoverPoint('top.EN_load_s1_or_s2', vname='EN_load_s1_or_s2', bins = list(range(0,2))),
    CoverCross('top.cross_cover', items = ['top.load_A_a', 'top.load_B_b', 'top.load_C_c', 'top.load_s1_or_s2_sel', 'top.EN_load_A' , 'top.EN_load_B', 'top.EN_load_C','top.load_s1_or_s2' ])
)
@counter_coverage
def model_macUnit(EN_load_A: int, EN_load_B: int, EN_load_C: int, EN_load_s1_or_s2:int, load_A_a: int, load_B_b: int, load_C_c: int, load_s1_or_s2_sel:int) -> int:
    if EN_load_A and EN_load_B and EN_load_C and EN_load_s1_or_s2:
        if load_s1_or_s2 == 1:
            return load_A_a * load_B_b + load_C_c
        else:
        	return float(load_A_a)*float(load_B_b) + float(load_C_c)
    return 0
