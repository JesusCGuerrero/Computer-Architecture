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
        self.LDI = 0b10000010 # Set the value of a register to an integer
        self.PRN = 0b01000111 # Print numeric value stored in the given register
        self.HLT = 0b00000001 # Halt the CPU (and exit the emulator) (1)
        self.MUL = 0b10100010 # MUL
        self.PUSH = 0b01000101 # PUSH
        self.POP = 0b01000110 # POP
        self.SUB = False
        self.DIV = False
        self.ADD = 0b10100000 # ADD
        self.CALL = 0b01010000 # CALL
        self.RET = 0b00010001 # RET
        self.CMP = 0b10100111 # CMP
        self.JMP = 0b01010100 # JMP
        self.JNE = 0b01010110 # JNE
        self.JEQ = 0b01010101 # JEQ
        self.reg[7] = 0xF4
        self.flag = 0b00000000
        
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
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
            else:
                self.flag = 0b00000000
        elif op == "SHL":
            self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] << self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] -= 0b11111111
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
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
            ir = self.ram[self.pc]
            reg_a = self.ram_read(self.pc + 1)
            reg_b = self.ram_read(self.pc + 2)

            if ir == self.LDI:
                # create a variable(register_number) from ram at address 1
                register_number = self.ram[self.pc+1] # Set register_number to 0
                # create a variable(value), store address 3
                value = self.ram[self.pc+2] # Set value to 8
                # access our reg, at our register_number index(1) and set it to value
                self.reg[register_number] = value
                # Increment program counter enough to start the next program
                self.pc += 3

            elif ir == self.MUL:
                self.alu("MUL", reg_a, reg_b)
                # Increment program counter enough to start the next program
                self.pc += 3

            elif ir == self.ADD:
                self.alu("ADD", reg_a, reg_b)
                self.pc += 3

            elif ir == self.SUB:
                self.alu("SUB", reg_a, reg_b)
                # Increment program counter enough to start the next program
                self.pc += 3

            elif ir == self.DIV:
                self.alu("DIV", reg_a, reg_b)
                # Increment program counter enough to start the next program
                self.pc += 3

            elif ir == self.PUSH:
                # Decrement stack pointer
                self.reg[7] -= 1
                # Prevent overflow
                self.reg[7] &= 0xff
                # Set sp position value in ram to be registry value at position
                self.ram[self.reg[7]] = self.reg[self.ram[self.pc+1]]
                # Next program
                self.pc += 2

            elif ir == self.POP:
                # Set registry value at position to be sp position value
                self.reg[self.ram[self.pc+1]] = self.ram[self.reg[7]]
                # Increment stack pointer
                self.reg[7] += 1
                # Prevent overflow
                self.reg[7] &= 0xff
                # Next program
                self.pc += 2

            elif ir == self.PRN:
                register_number = self.ram[self.pc+1]
                print(self.reg[register_number])
                # Increment program counter enough to start the next program
                self.pc +=2

            elif ir == self.CALL:
                returnAddress = self.pc + 2
                self.reg[7] -= 1
                self.ram[self.reg[7]] = returnAddress
                self.pc = self.reg[self.ram[self.pc+1]]

            elif ir == self.RET:
                returnAddress = self.ram[self.reg[7]]
                self.reg[self.ram[self.pc+1]] = self.ram[self.reg[7]]
                # Increment stack pointer
                self.reg[7] += 1
                self.pc = returnAddress

            elif ir == self.CMP:
                self.alu("CMP", reg_a, reg_b)
                self.pc += 3
        
            elif ir == self.JMP:
                self.pc = self.reg[self.ram[self.pc + 1]]

            elif ir == self.JEQ:
                if self.flag == 0b00000001:
                    self.pc = self.reg[self.ram[self.pc + 1]]
                else:
                    self.pc += 2

            elif ir == self.JNE:
                if self.flag != 0b00000001:
                    self.pc = self.reg[self.ram[self.pc + 1]]
                else:
                    self.pc += 2

            elif ir == self.HLT:
                running = False
                # Increment program counter enough to start the next program
                self.pc +=1

            elif ir == 0:
                # Skip any program with a byte identifier of 0
                continue

            else:
                print(f'Unkown instruction {ir} at address {self.pc}')
                # Exit the program
                sys.exit(1)