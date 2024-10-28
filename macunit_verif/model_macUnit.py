# model for macunit

import cocotb
from cocotb_coverage.coverage import *

macUnit_coverage = coverage_section(
    CoverPoint('top.load_A_a', vname='load_A_a', bins = list(range(0,1000))),
    CoverPoint('top.EN_load_A', vname='EN_load_A', bins = list(range(0,2))),
    CoverCross('top.cross_cover', items = ['top.load_A_a', 'top.EN_load_A']),
    CoverPoint('top.load_B_b', vname='load_B_b', bins = list(range(0,1000))),
    CoverPoint('top.EN_load_B', vname='EN_load_B', bins = list(range(0,2))),
    CoverCross('top.cross_cover', items = ['top.load_B_b', 'top.EN_load_B']),
    CoverPoint('top.load_C_c', vname='load_C_c', bins = list(range(0,200000))),
    CoverPoint('top.EN_load_C', vname='EN_load_C', bins = list(range(0,2))),
    CoverCross('top.cross_cover', items = ['top.load_C_c', 'top.EN_load_C']),
    CoverPoint('top.load_s1_or_s2_sel', vname='load_s1_or_s2_sel', bins = list(range(0,1))),
    CoverPoint('top.EN_load_s1_or_s2', vname='EN_load_s1_or_s2', bins = list(range(0,1))),
    CoverCross('top.cross_cover', items = ['top.load_s1_or_s2_sel','top.load_s1_or_s2' ])
)
@macUnit_coverage
def model_macUnit(EN_load_A: int, EN_load_B: int, EN_load_C: int, EN_load_s1_or_s2:int, load_A_a: int, load_B_b: int, load_C_c: int, load_s1_or_s2_sel:int) -> int:
    result = load_A_a * load_B_b + load_C_c
    return result

    
    
    
    
    
    
    
    
    
    
    
    
    
    
