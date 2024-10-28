# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.binary import BinaryValue
from model_macUnit import *

def read_binary_file_integer(filename,bitwidth):
	data = []
	with open(filename, 'r') as f:
		for line in f:
			value = BinaryValue(line.strip(),n_bits=bitwidth)
			data.append(value)
	return data
	
def read_binary_file_float(filename,bitwidth):
	data = []
	with open(filename, 'r') as f:
		for line in f:
			value = BinaryValue(line.strip(),n_bits=bitwidth)
			data.append(value)
	return data
	
def read_binary_file_float1(filename,bitwidth):
	data = []
	with open(filename, 'r') as f:
		for line in f:
			value = BinaryValue(line.strip()[:31],n_bits=bitwidth-1)
			data.append(value)
	return data
	
@cocotb.test()
async def test_macUnit_integer(dut):
    """Test to check Int macUnit"""
    a_Data = read_binary_file_integer("testcases/int8mac/A_binary.txt",8)
    b_Data = read_binary_file_integer("testcases/int8mac/B_binary.txt",8)
    c_Data = read_binary_file_integer("testcases/int8mac/C_binary.txt",32)
    expected_MacOut_Integer = read_binary_file_integer("testcases/int8mac/MAC_binary.txt",32)
    num_tests_intger = len(a_Data)
    clock = Clock(dut.CLK, 10, units="us")  # Create a 10us period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    passed_tests = 0
    Output_dut_Integer = []
    for i in range (num_tests_intger):
        await RisingEdge(dut.CLK)
        dut.EN_load_A.value = 1
        dut.EN_load_B.value = 1
        dut.EN_load_C.value = 1
        dut.EN_load_s1_or_s2.value = 0
        dut.load_A_a.value = a_Data[i]
        dut.load_B_b.value = b_Data[i]
        dut.load_C_c.value = c_Data[i]
        dut.load_s1_or_s2_sel.value = 1	
        for i in range(1,5):
            await RisingEdge(dut.CLK)
        #dut._log.info(f'output {int(dut.get_MAC.value.signed_integer)}')
        Output_dut_Integer.append(dut.get_MAC.value)
    assert  expected_MacOut_Integer == Output_dut_Integer, f'Output mismatch, Expected = {expected_MacOut_Integer} DUT = {Output_dut_Integer}'
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    dut.EN_load_A.value = 1
    dut.EN_load_B.value = 1
    dut.EN_load_C.value = 1
    dut.EN_load_s1_or_s2.value = 0
    dut.load_A_a.value = -50
    dut.load_B_b.value = 40
    dut.load_C_c.value = 30
    dut.load_s1_or_s2_sel.value = 1	
    for i in range(0,5):
    	await RisingEdge(dut.CLK)
    print(int(dut.load_A_a.value.signed_integer))
    mac_Out_Model = model_macUnit(int(dut.EN_load_A.value),int(dut.EN_load_B.value),int(dut.EN_load_C.value),int(dut.EN_load_s1_or_s2.value),  int(dut.load_A_a.value.signed_integer), int(dut.load_B_b.value.signed_integer),int(dut.load_C_c.value.signed_integer), int(dut.load_s1_or_s2_sel.value));
    
    for i in range(0,5):
    	await RisingEdge(dut.CLK)
    dut._log.info(f'output {int(dut.get_MAC.value)}')
    assert int(mac_Out_Model) == int(dut.get_MAC.value.signed_integer), f'Counter Output Mismatch, Expected = {mac_Out_Model} DUT = {int(dut.get_MAC.value)}'
    for i in range(1,3):
    	await RisingEdge(dut.CLK)

@cocotb.test()
async def test_macUnit_float(dut):
    
    
    a_Data = read_binary_file_float("testcases/bf16mac/A_binary.txt",16)
    b_Data = read_binary_file_float("testcases/bf16mac/B_binary.txt",16)
    c_Data = read_binary_file_float("testcases/bf16mac/C_binary.txt",32)
    expected_MacOut_float = read_binary_file_float1("testcases/bf16mac/MAC_binary.txt",32)
    
    num_tests_float = len(a_Data)
    
    clock = Clock(dut.CLK, 10, units="us")  # Create a 10us period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    passed_tests = 0
    Output_dut_float = []
    for i in range (num_tests_float):
    	await RisingEdge(dut.CLK)

    	dut.EN_load_A.value = 1
    	dut.EN_load_B.value = 1
    	dut.EN_load_C.value = 1
    	dut.EN_load_s1_or_s2.value = 1	
    	dut.load_A_a.value = a_Data[i]
    	dut.load_B_b.value = b_Data[i]
    	dut.load_C_c.value = c_Data[i]
    	dut.load_s1_or_s2_sel.value = 1    	
    	for i in range(1,6):
    		await RisingEdge(dut.CLK)
    	#dut._log.info(f'output {dut.get_MAC.value}')
    	Output_dut_float.append(BinaryValue(str(dut.get_MAC.value)[:31]))
    assert  expected_MacOut_float == Output_dut_float, f'Output mismatch, Expected = {0} DUT = {Output_dut_float}'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

