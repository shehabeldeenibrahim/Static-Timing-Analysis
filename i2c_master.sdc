set PERIOD 0.56
reset_design
create_clock -period $PERIOD -name clk [get_ports clk]
set_clock_uncertainty 0.05 [get_clocks clk]
set_ideal_network [get_ports clk]
set ALL_INS_EX_CLK [remove_from_collection [all_inputs] [get_ports clk]]
set_input_delay [expr $PERIOD*0.4] -max -clock clk $ALL_INS_EX_CLK
set_output_delay [expr $PERIOD*0.4] -max -clock clk [all_outputs]
set_driving_cell -lib_cell DFFARX1_RVT -pin Q $ALL_INS_EX_CLK
set max_cap [expr [load_of saed32rvt_ss0p7vn40c/AND2X1_RVT/A1] * 10]
set_max_capacitance $max_cap $ALL_INS_EX_CLK
set_load [expr 3 * $max_cap] [all_outputs]
set_max_area 0
