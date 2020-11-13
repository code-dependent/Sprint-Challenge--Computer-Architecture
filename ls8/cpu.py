"""CPU functionality."""

import sys
# def e(fl):
#     fl = bin((fl | 0b00000001))
# def l(fl):
#     fl = bin((fl | 0b00000100))
# def g(fl):
#     fl = bin((fl | 0b00000010))
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.reg = [0] * 8
        self.pc = self.reg[0]
        self.SP = 0xf4
        self.fl = bin(7)
        self.inst_set_pc = False
        self.instruction = {
            0b10000010:'LDI',
            0b01000111:'PRN',
            0b00000001:'HLT',
            0b10100010:'MUL',
            0b01000101:'PUSH',
            0b01000110:'POP',
            0b01010000:'CALL',
            0b00010001:'RET',
            0b10100000:'ADD',
            0b10100111:'CMP',
            0b01010101:'JEQ',
            0b01010110:'JNE',
            0b01010111:'JGT',
            0b01010100: 'JMP'
            }
        # self.flags = {
        #     'E': e(self.fl),
        #     'L': l(self.fl),
        #     'G': g(self.fl)
        # }

    def load(self, txt):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        try:
            with open(txt) as f:
                for line in f:
                    line = line.strip()
                    if line == '' or line[0] == '#':
                        continue
                    try:
                        line_val = line.split("#")[0]
                        value = int(line_val, 2)
                        # print()
                    except ValueError:
                        print(f'Invalid Number: {line_val}')
                        sys.exit(1)
                    # print(value)
                    self.ram[address] = value
                    address+=1
        except FileNotFoundError:
            print(f'File :{txt} Cannot be Found. Please Enter a Valid Program to Run.')
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 1
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 4
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 2
        elif op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")
    def ram_read(self,address):
        return self.ram[address]
    def ram_write(self,val, address):
        self.ram[address] = val

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    def push_val(self,operation):
        self.SP-=1
        self.ram[self.SP] = self.reg[operation]

    def pop_val(self,operation):
        self.reg[operation] = self.ram[self.SP]
        self.SP+=1

    def ret_pop(self):
        rtn = self.ram[self.SP]
        self.SP+=1
        return rtn

    def call_push(self,val):
        self.SP-=1
        self.ram[self.SP] = val

    def compare_reg(self,reg_a, reg_b):
        if reg_a == reg_b:
            return 'E'
        if reg_a < reg_b:
            return 'L'
        if reg_a > reg_b:
            return 'G'




    def run(self):
        """Run the CPU."""
        running = True
        while running:
            self.trace()
            # print(self.pc)
            IR = self.ram[self.pc]

            instruction_size = ((IR & 0b11000000) >> 6) +1
            ir_moves_pc = True if ((IR & 0b00010000) >> 4) == 1 else False

            op_a = self.ram_read(self.pc+1)
            op_b = self.ram_read(self.pc+2)
            # print(bin(84))
            if self.instruction[IR] == 'LDI':
                self.reg[op_a] = op_b

            elif self.instruction[IR] == 'PRN':
                print(self.reg[op_a])

            elif self.instruction[IR] == 'MUL':
                self.alu('MUL', op_a, op_b)

            elif self.instruction[IR] == 'PUSH':
                self.push_val(op_a)

            elif self.instruction[IR] == 'POP':
                self.pop_val(op_a)

            elif self.instruction[IR] == 'CALL':
                self.call_push(self.pc + 1)
                self.pc = self.reg[op_a]

            elif self.instruction[IR] == 'RET':
                self.pc = self.ret_pop()

            elif self.instruction[IR] == 'ADD':
                # print(self.pc)
                self.alu('ADD',op_a, op_b)

            elif self.instruction[IR] == 'CMP':
                self.alu('CMP', op_a, op_b)
                # print('hit')

            elif self.instruction[IR] == 'JEQ':
                if self.fl == 1:
                    # print("hit JEQ")
                    self.pc = self.reg[op_a]
                else:
                    self.pc+=2
            elif self.instruction[IR] == 'JNE':
                # print("hit JNE")
                if self.fl > 1:
                    self.pc = self.reg[op_a]
                else:
                    self.pc+=2
            elif self.instruction[IR] == 'JGT':
                if self.fl == 2:
                    self.pc = self.reg[op_a]
            elif self.instruction[IR] == 'JMP':
                self.pc = self.reg[op_a]

            elif self.instruction[IR] == 'HLT':
                # print()

                sys.exit(0)

            if not ir_moves_pc:
                self.pc+= instruction_size
            # else:
            #     self.pc = IR

