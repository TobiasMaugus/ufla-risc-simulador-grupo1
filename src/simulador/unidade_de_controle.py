# unidade_de_controle.py
# Orquestra IF, ID, EX/MEM, WB em quatro rotinas por instrução
# Usa interpretador_de_instrucoes, memoria, banco_de_registradores, alu

from src.interpretador.interpretador_de_instrucoes import parse_program, asm_to_binary, decode_instruction
from src.simulador.memoria import Memoria
from src.simulador.banco_de_registradores import RegisterFile
import src.simulador.alu as alu
import os

class CPU:
    def __init__(self, program_path):
        # Se for .txt (assembly), converte para .bin
        if program_path.endswith(".txt"):
            bin_path = os.path.join("bin", os.path.basename(program_path).replace(".txt", ".bin"))
            os.makedirs("bin", exist_ok=True)
            asm_to_binary(program_path, bin_path)
            program_path = bin_path
        
        self.mem = Memoria()
        parsed = parse_program(program_path)
        self.mem.load_program(parsed)
        self.rf = RegisterFile()
        self.PC = 0
        self.IR = None  # 32-bit value
        self.flags = {"neg":0, "zero":0, "carry":0, "overflow":0}
        self.halted = False
        # Estágios do pipeline (Simplificado, pois cada instrução passa por 4 rotinas)
        self.decoded = None
        self.exec_result = None
        self.writeback_info = None
        self.cycle = 0

    def if_stage(self):
        #  busca instrução e incrementa PC
        instr_word = self.mem.read(self.PC)
        # Armazena string de 32-bits para decodificação
        instr_bits = format(instr_word & 0xFFFFFFFF, '032b')
        self.IR = instr_bits
        self.PC += 1
        return instr_bits

    def id_stage(self, instr_bits):
        # Decodificando e lendo registradores
        decoded = decode_instruction(instr_bits)
        self.decoded = decoded
        # Ler registrador de operandos(se tiver)
        ra = decoded["ra"]
        rb = decoded["rb"]
        rc = decoded["rc"]
        
        if 0 <= ra < 32:
            decoded["ra_val"] = self.rf.read(ra)
        else:
            decoded["ra_val"] = 0
        
        if 0 <= rb < 32:
            decoded["rb_val"] = self.rf.read(rb)
        else:
            decoded["rb_val"] = 0
            
        if 0 <= rc < 32:
            decoded["rc_val"] = self.rf.read(rc)
        else:
            decoded["rc_val"] = 0
            
        
        return decoded

    def ex_mem_stage(self):
        d = self.decoded
        if not d:
            return None
        mnem = d["mnemonic"]
        ra = d["ra"]
        ra_val = d["ra_val"]
        rb_val = d["rb_val"]
        rc = d["rc"]
        rc_val = d["rc_val"]
        rc_idx = d["rc"]
        result = None
        wb = {"write_reg": None, "write_val": None, "mem_write": None, "mem_addr": None}

        # Trata as instruções
        if mnem == "halt":
            self.halted = True

        elif mnem == "add":
            # add r1, r2, r3 → r1 = r2 + r3
            res = alu.add_op(rb_val, rc_val)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "sub":
            # sub r1, r2, r3 → r1 = r2 - r3
            res = alu.sub_op(rb_val, rc_val)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "zeros":
            # Produz zero no destino rc
            res = alu.zeros_op()
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "xor":
            # xor r1, r2, r3 → r1 = r2 xor r3
            res = alu.xor_op(rb_val, rc_val)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "or":
            # or r1, r2, r3 → r1 = r2 or r3
            res = alu.or_op(rb_val, rc_val)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "passnota":
            # Aplica not em ra e escreve em rc
            res = alu.not_op(ra_val)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "and":
            # and r1, r2, r3 → r1 = r2 and r3
            res = alu.and_op(rb_val, rc_val)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "asl":
            # asl r1, r2, r3 → r1 = r2 << r3
            res = alu.asl_op(rb_val, rc_val & 0x1F)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "asr":
            # asr r1, r2, r3 → r1 = r2 >> r3 (aritmético)
            res = alu.asr_op(rb_val, rc_val & 0x1F)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "lsl":
            # lsl r1, r2, r3 → r1 = r2 << r3 (lógico)
            res = alu.lsl_op(rb_val, rc_val & 0x1F)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "lsr":
            # lsr r1, r2, r3 → r1 = r2 >> r3 (lógico)
            res = alu.lsr_op(rb_val, rc_val & 0x1F)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "passa":
            # Copia ra para rc
            res = alu.passa_op(ra_val)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "lcl_msb":
            # Define os bits superiores do registrador
            const16 = d["const16"]
            old = d["rc_val"]
            new = ((const16 << 16) & 0xFFFF0000) | (old & 0x0000FFFF)
            wb["write_reg"] = d["rc"]
            wb["write_val"] = new

        elif mnem == "lcl_lsb":
            # Define os bits inferiores do registrador
            const16 = d["const16"]
            old = d["rc_val"]
            new = (const16 & 0xFFFF) | (old & 0xFFFF0000)
            wb["write_reg"] = d["rc"]
            wb["write_val"] = new

        elif mnem == "load":
            # Carrega rc ← mem[ra]
            addr = d["ra_val"] & 0xFFFF
            val = self.mem.read(addr)
            wb["write_reg"] = d["rc"]
            wb["write_val"] = val

        elif mnem == "store":
            # Armazena mem[rc] ← ra
            addr = d["rc_val"] & 0xFFFF
            data = d["ra_val"]
            self.mem.write(addr, data)

        elif mnem == "storei":
            # Armazena mem[imediato] ← ra
            address = d["rc"]
            value = d["ra_val"]
            self.mem.write(address & 0xFFFF, value)
            wb = {}  # Storei não escreve registradores

        elif mnem == "loadi":
            # Lê memória no endereço imediato de 24 bits
            addr = d["end24"] & 0xFFFF
            val = self.mem.read(addr)
            wb["write_reg"] = d["rc"]
            wb["write_reg"] = d["ra"]
            wb["write_val"] = val

        elif mnem == "jal":
            # Salta salvando o PC em r31
            self.rf.write(31, self.PC)
            self.PC = d["end24"]

        elif mnem == "jr":
            # Salto indireto: pc = ra
            self.PC = d["ra_val"]

        elif mnem == "beq":
            # Desvia se ra == rb
            offset = self.sign_extend_8_to_32(d["const8"])
            if d["ra_val"] == d["rb_val"]:
                self.PC += offset

        elif mnem == "bne":
            # Desvia se ra != rb
            offset = self.sign_extend_8_to_32(d["const8"])
            if d["ra_val"] != d["rb_val"]:
                self.PC += offset

        elif mnem == "j":
            # Salto direto
            self.PC = d["end24"]

        elif mnem == "mul":
            # mul r1, r2, r3 → r1 = r2 * r3
            res = alu.mul_op(rb_val, rc_val)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "div":
            # div r1, r2, r3 → r1 = r2 / r3
            res = alu.div_op(rb_val, rc_val)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "mod":
            # mod r1, r2, r3 → r1 = r2 % r3
            res = alu.mod_op(rb_val, rc_val)
            result = res
            wb["write_reg"] = ra
            wb["write_val"] = res.result

        elif mnem == "neg":
            # Aplica negação aritmética
            res = alu.neg_op(d["ra_val"])
            result = res
            wb["write_reg"] = d["rc"]
            wb["write_val"] = res.result

        elif mnem == "inc":
            # Incrementa o registrador
            res = alu.inc_op(d["ra_val"])
            result = res
            wb["write_reg"] = d["ra"]
            wb["write_val"] = res.result

        elif mnem == "dec":
            # Decrementa o registrador
            res = alu.dec_op(d["ra_val"])
            result = res
            wb["write_reg"] = d["ra"]
            wb["write_val"] = res.result

        else:
            # Ignora instrução desconhecida
            pass

        # Atualiza flags se houve operação da ALU
        if result:
            self.flags["neg"] = result.neg
            self.flags["zero"] = result.zero
            self.flags["carry"] = result.carry
            self.flags["overflow"] = result.overflow

        self.writeback_info = wb
        return wb


    def wb_stage(self):
        wb = self.writeback_info
        if not wb:
            return
        if wb.get("write_reg") is not None:
            reg_idx = wb["write_reg"]
            # Apenas escreve em índices válidos de registrador (0–31)
            if 0 <= reg_idx < 32:
                self.rf.write(reg_idx, wb["write_val"])
        # Escritas na memória já foram feitas no estágio EX
        # Limpa informações de writeback
        self.writeback_info = None


    

    def run(self, max_cycles=10000, verbose=True):
        """
        Executa o processador em 4 estágios sequenciais (sem pipeline).
        Cada estágio consome 1 ciclo, totalizando 4 ciclos por instrução.
        A instrução HALT também executa seus 4 estágios.
        """
        if verbose:
            print("Iniciando simulação monociclo (4 estágios).")
            print()

        while not self.halted and self.cycle < max_cycles:
            # ================================
            # IF: Busca da instrução
            # ================================
            self.cycle += 1
            instr_bits = self.if_stage()
            if verbose:
                print(f"--- Cycle {self.cycle} ---")
                print(f"IF: PC -> {self.PC} ; IR = {instr_bits}")
            if self.halted:
                break

            # ================================
            # ID: Decodificação
            # ================================
            self.cycle += 1
            decoded = self.id_stage(instr_bits)
            if verbose:
                print(f"--- Cycle {self.cycle} ---")
                print(f"ID: decoded = {decoded['mnemonic']} ra={decoded['ra']} rb={decoded['rb']} rc={decoded['rc']}")
            if self.halted:
                break

            # ================================
            # EX/MEM: Execução e acesso à memória
            # ================================
            self.cycle += 1
            wbinfo = self.ex_mem_stage()
            if verbose:
                print(f"--- Cycle {self.cycle} ---")
                print(f"EX/MEM: flags = {self.flags}")

            # Se a instrução for HALT, marca mas continua até WB
            is_halt = self.decoded["mnemonic"] == "halt" if self.decoded else False

            # ================================
            # WB: Escrita de resultados
            # ================================
            self.cycle += 1
            self.writeback_info = wbinfo
            self.wb_stage()
            if verbose:
                print(f"--- Cycle {self.cycle} ---")
                print("WB: Registers non-zero:", self.rf.dump_nonzero())
                print("Mem (non-zero small sample):", self.mem.dump_modified()[:10])
                print()

            # Após WB do HALT, encerra simulação
            if is_halt or self.halted:
                self.halted = True
                if verbose:
                    print("HALT encountered. Stopping.")
                break
    def sign_extend_8_to_32(self, val_8_bit):
        """Estende o sinal de um valor de 8 bits para 32 bits."""
        if (val_8_bit & 0x80) != 0:  # Verifica o bit de sinal (bit 7)
            return val_8_bit | 0xFFFFFF00 # Estende o sinal
        return val_8_bit



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python -m src.simulador.unidade_de_controle bin/teste3.bin")
        sys.exit(1)
    cpu = CPU(sys.argv[1])
    cpu.run(verbose=True)
