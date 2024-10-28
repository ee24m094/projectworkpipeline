package macUnit;

//package imports

//Custom structure for MAC Result
typedef struct{
	Bit#(32) macOut;
}macOutResult deriving(Bits, Eq);

// Custom structure for Addition
typedef struct{
	Bit#(1) overflow;
	Bit#(32) sum;
} AdderResult_int32 deriving (Bits,Eq);

//Interface declaration for macUnit
interface macUnit_ifc;
	//method loadValues load_Values();
	method Action load_A(Bit#(16) a);
	method Action load_B(Bit#(16) b);
	method Action load_C(Bit#(16) c);
	method Action load_s1_or_s2(Bit#(1) s1_or_s2);
	method ActionValue#(Bit#(32)) get_MAC();
endinterface: macUnit_ifc

//Interface for DeMux
interface DeMux_ifc;
	method ActionValue#(Bit#(8)) get_A_8(Bit#(16) data, Bit#(1) s1_or_s2);
	method ActionValue#(Bit#(16)) get_A_16(Bit#(16) data, Bit#(1) s1_or_s2);  
endinterface: DeMux

//Interface for Mux
interface Mux_ifc;
	method ActionValue#(Bit#(32)) select_output(Bit#(32) mac_int32, Bit#(32) mac_fp32, Bool s1_or_s2); 
endinterface: Mux



//Top Module for MAC Unit
(*synthesize*)
module mkMac_Unit(macUnit_ifc);
	//Internal Registers
	Reg#(Bit#(16)) reg_A <- mkReg(0);
	Reg#(Bit#(16)) reg_B <- mkReg(0);
	Reg#(Bit#(32)) reg_C <- mkReg(0);
	Reg#(Bit#(1)) reg_s1_or_s2 <- mkReg(0);

	//Registers to store results
	Reg#(AdderResult_int32) reg_Out_Addition <- mkReg(AdderResult_int32({overflow=0, sum=0}));	
	//Reg#(macOutResult) reg_Out_int32, reg_Out_fp32 <- mkReg(macOutResult({macOut=0}));
	
	//Instantiate DeMux for A and B
	DeMux_ifc demux_reg_A <- mkDeMux();
	DeMux_ifc demux_reg_B <- mkDeMux();

	//Instantiate Mux
	Mux_ifc mux <- mkMux();

	//Funtion to perform bitwise addition for integers
	function Bit#(32) bitwise_Addition_int32(
	Bit#(32) a, 
	Bit#(32) b,
	Bit#(1) cin;
	);
	//Initialize sum and carry
		Bit#(32) sum=0;
		Bit#(33) carry=zeroExtend(cin);

		//Add bit by bit with carry
		for(Integer i=0; i<32; i=i+1) begin
			sum[i] = (a[i] ^ b[i] ^ carry[i]);
			carry[i+1] = (a[i] & b[i] | (carry[i] & (a[i] ^ b[i])));
		end
		//set overflow flag
		AdderResult_int32 result;
		result.sum =sum;
		result.overflow=carry[32];
		return result;

	endfunction: bitwise_Addition_int32 

	//Function to perform multiplication for int32
	function Bit#(32) bitwise_multiplication_int32(Bit#(8) a, Bit#(8) b);
		
		Bit#(32) product=0;
		Bit#(32) shifted_a = zeroExtend(a);
		
		for(Integer i=0; i<8; i=i+1) begin
			if(b[i]) begin
				product = bitwise_Addition_int32(product, shifted_a,0).sum;
			end
			shifted_a = shifted_a << 1;
		end
		
		return product;
	
	endfunction: bitwise_multiplication_int32

	//function to perform 24 bit multiplication
	function Bit#(32) bitwise_multiplication_24bit(Bit#(24) a, Bit#(24) b);
		Bit#(48) product_32bit=0;

		for(Integer i=0; i<24; i=i+1) begin
			if(b[i]) begin
				product = bitwise_Addition_int32(product, a<<i,0).sum;
			end
		end

		return product_32bit[47:16];
	endfunction: bitwise_multiplication_24bit

	//function to convert bf16 to fp32
	function Bit#(32) bf16_to_fp32(Bit#(16) bf16);
		Bit#(32) fp32 = zeroExtend(bf16[15]) << 31; //sign
		fp32 = fp32 | (zeroExtend(bf16[14:7])) << 23; // exponent
		fp32 = fp32 | (zeroExtend(bf16[6:0])) << 16; //mantissa
		return fp32;
	endfunction

	//Function to perform multiplication for fp32
	function Bit#(32) bitwise_multiplication_fp32(Bit#(32) a_fp32, Bit#(32) b_fp32);
		Bit#(1) sign_A = a_fp32[31];
		Bit#(1) sign_B = b_fp32[31];
		Bit#(23) mantissa_a = {1'b1,a_fp32[22:0]};
		Bit#(23) mantissa_b = {1'b1,b_fp32[22:0]};
		Bit#(8) exponent_A = a_fp32[30:23];
		Bit#(8) exponent_B = b_fp32[30:23];
		//Bit#(32) product=0;

		//multiply mantissas
		Bit#(48) mantissa_product= bitwise_multiplication_24bit(mantissa_a,mantissa_b);

		//check for rounding requirement
		Bit#(1) round_bit = mantissa_product[22];

		Bit#(23) mantissa_rounded;

		if(round_bit) begin
			//Roundup by adding 1 to the significant bits
			mantissa_rounded = bitwise_Addition_int32(mantissa_product[46:24],1,0).sum;
		end else begin
			//no rounding needed, just truncate
			mantissa_rounded = mantissa_product[46:24];
		end

		//Exponent addition using bitwise addition
		Bit#(8) exponent_sum = bitwise_Addition_int32(exponent_A, exponent_B,0)-127;
		
		//handling mantissa overflow after rounding
		if(mantissa_rounded[23]) begin
			//overflow occurred, shift and increment exponent
			mantissa_rounded = mantissa_rounded >> 1;
			exponent_sum = bitwise_Addition_int32(exponent_sum,1,0).sum;
		end

		//Form the final result (sign|exponent|mantissa)
		Bit#(32) result = {sign_A ^ sign_B, exponent_sum, mantissa_rounded[22:0]};
		return result;
	endfunction: bitwise_multiplication_fp32 

	//Control flow for MAC operations
	
	rule rl_mac_int32();
		if(reg_s1_or_s2==0) begin
			Bit#(8) A = demux_reg_A.get_A_8(reg_A, reg_s1_or_s2);
			Bit#(8) B = demux_reg_A.get_A_8(reg_B, reg_s1_or_s2);
			Bit#(32) product = bitwise_multiplication_int32(A,B);
			reg_Out_Addition <= bitwise_Addition_int32(product, reg_C, 1'b0);
			Bit#(32) reg_Out_int32 <= macOutResult(macOut=reg_Out_Addition.sum);
		end 
	endrule: rl_mac_int32

	rule rl_mac_fp32();
		if(reg_s1_or_s2==1) begin
			Bit#(32) a_fp32 <= bf16_to_fp32(reg_A);
			Bit#(32) b_fp32 <= bf16_to_fp32(reg_B); 
			Bit#(32) product = bitwise_multiplication_fp32(a_fp32,b_fp32);
			reg_Out_Addition <= bitwise_Addition_int32(product, reg_C,0);
			Bit#(32) reg_Out_fp32<= macOutResult(macOut = reg_Out_Addition.sum);
		end
	endrule:rl_mac_fp32

	//start MAC Operation
	method Action load_A(Bit#(16) a);
		reg_A <= a;
	endmethod
	method Action load_B(Bit#(16) b);
		reg_B <= b;
	endmethod
	method Action load_C(Bit#(16) c);
		reg_C <= c;
	endmethod
	method Action load_s1_or_s2(Bit#(1) s1_or_s2);
		reg_s1_or_s2 <= s1_or_s2;
	endmethod

	method ActionValue#(Bit#(32)) get_MAC();
		//Bit#(32) mux.select_output();
		return mux.select_output(reg_Out_int32,reg_Out_fp32, reg_s1_or_s2);
	endmethod


	
endmodule: mkMac_Unit



//module for DeMux
(*synthesize*)
module mkDeMux(DeMux);

	//Bit#(16) input_data <- 0;

	method ActionValue#(Bit#(8)) get_A_8(Bit#(16) data, Bit#(1) s1_or_s2);
		return s1_or_s2 ? data[15:8]:data[7:0];
	endmethod

	method ActionValue#(Bit#(16)) get_A_16(Bit#(16) data);
		return s1_or_s2 ? data:zeroExtend(data[7:0]);
	endmethod


endmodule: mkDeMux

//module for Mux
(*synthesize*)
module mkMux(Mux);
	method ActionValue#(Bit#(32)) select_output(Bit#(32) mac_int32, Bit#(32) mac_fp32, Bit#(1) s1_or_s2);
		return s1_or_s2 ? mac_fp32 : mac_int32;
	endmethod:select_output
endmodule:mkMux


endpackage:macUnit
