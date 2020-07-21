"""CPU functionality."""
import sys

class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0 # Program Counter
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.running = False
        self.LDI = 0b10000010 # set the value of a register to an integer (130)
        self.PRN = 0b01000111 # Print numeric value stored in the given register (71)
        self.HLT = 0b00000001 # Halt the CPU (and exit the emulator) (1)
        self.MUL = 0b10100010 # MUL
        self.PUSH = 0b01000101 # PUSH R0
        self.POP = 0b01000110 # POP R2
        
    def load(self):
        """Load a program into memory."""
        address = 0

        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    value = line.split("#")[0].strip()
                    if value == '':
                        continue
                    v = int(value, 2)
                    self.ram[address] = v
                    address += 1
        except FileNotFoundError:
            print(f"Error {sys.argv[1]}")
            sys.exit(1)

    # def load(self):
    #     """Load a program into memory."""
    #     address = 0
    #     # For now, we've just hardcoded a program:
    #     # program = [
    #     #     # From print8.ls8
    #     #     0b10000010, # 130 LDI
    #     #     0b00000000, # 0
    #     #     0b00001000, # 8
    #     #     0b01000111, # 71 PRN
    #     #     0b00000000, # 0
    #     #     0b00000001, # 1 HLT
    #     # ]

    #     # for instruction in program:
    #     #     self.ram[address] = instruction
    #     #     address += 1
    #     if len(sys.argv) != 2:
    #         print("usage: ls8.py filename")
    #         sys.exit(1)

    #     try:
    #         with open(sys.argv[1]) as f:
    #             for line in f:
    #                 # try:
    #                 line = line.split("#", 1)[0]
    #                 if line == "" or '\n':
    #                     continue
    #                 line = int(line, 2)
    #                 self.ram[address] = line
    #                 address += 1
    #                 # except ValueError:
    #                 #     print(f"Could not find file {sys.argv[1]}")
    #                 #     sys.exit(1)
    #                 print("RAM", self.ram)
    #     except FileNotFoundError:
    #         print(f"Error {sys.argv[1]}")
    #         sys.exit(1)

    # mar stands for memory address register
    # mdr stands for memory data register
    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()

    def run(self):
        """Run the CPU."""
        running = True # set CPU to running
        while running:
            # instruction register = ram[self.pc]
            # Setting ir to be whichever program we are currently running from ram
            ir = self.ram[self.pc]
            # print(ir) # 130
            # print(self.LDI) # 130
            # print('before reg_a')
            reg_a = self.ram_read(self.pc + 1)
            # print('before reg_b')
            reg_b = self.ram_read(self.pc + 2)

            # if instruction register(ir) == load immediate (LDI)

            if ir == self.LDI:
                # create a variable(register_number) from ram at address 1
                register_number = self.ram[self.pc+1] # Set register_number to 0
                # create a variable(value), store address 3
                value = self.ram[self.pc+2] # Set value to 8
                # access our reg, at our register_number index(1) and set it to value
                self.reg[register_number] = value
                # print(self.reg)
                self.pc += 3
                # print(f'REGISTER NUMBER: {register_number} VALUE: {value}')
            elif ir == self.MUL:
                self.alu("MUL", reg_a, reg_b)
                self.pc += 3
            elif ir == self.PUSH:
                self.pc += 2
                continue
            elif ir == self.POP:
                self.pc += 2
                continue 
            elif ir == self.PRN:
                register_number = self.ram[self.pc+1]
                print(self.reg[register_number])
                self.pc +=2
            elif ir == self.HLT:
                running = False
                self.pc +=1
            elif ir == 0:
                continue
            else:
                print(f'Unkown instruction {ir} at address {self.pc}')
                sys.exit(1)