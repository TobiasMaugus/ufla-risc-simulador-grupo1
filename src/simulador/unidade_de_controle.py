# unidade_de_controle.py
# Orquestra IF, ID, EX/MEM, WB em quatro rotinas por instrução
# Usa interpretador_de_instrucoes, memoria, banco_de_registradores, alu

from src.interpretador.interpretador_de_instrucoes import parse_program, decode_instruction, INSTRUCOES
from src.simulador.memoria import Memoria
from src.simulador.banco_de_registradores import RegisterFile
import src.simulador.alu as alu

class CPU:
    def __init__(self, program_path):
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
        # busca iinstrução e incrementa PC
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
        decoded["ra_val"] = self.rf.read(ra)
        decoded["rb_val"] = self.rf.read(rb)
        decoded["rc_val"] = self.rf.read(rc)
        return decoded

    def ex_mem_stage(self):
        d = self.decoded
        if not d:
            return None
        mnem = d["mnemonic"]
        ra_val = d["ra_val"]
        rb_val = d["rb_val"]
        rc_idx = d["rc"]
        result = None
        wb = {"write_reg": None, "write_val": None, "mem_write": None, "mem_addr": None}
        
        if mnem == "halt":
            self.halted = True
        elif mnem == "add":
            res = alu.add_op(ra_val, rb_val)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "sub":
            res = alu.sub_op(ra_val, rb_val)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "zeros":
            res = alu.zeros_op()
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "xor":
            res = alu.xor_op(ra_val, rb_val)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "or":
            res = alu.or_op(ra_val, rb_val)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "passnota":
            res = alu.not_op(ra_val)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "and":
            res = alu.and_op(ra_val, rb_val)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "asl":
            res = alu.asl_op(ra_val, rb_val & 0x1F)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "asr":
            res = alu.asr_op(ra_val, rb_val & 0x1F)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "lsl":
            res = alu.lsl_op(ra_val, rb_val & 0x1F)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "lsr":
            res = alu.lsr_op(ra_val, rb_val & 0x1F)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "passa":
            res = alu.passa_op(ra_val)
            result = res
            wb["write_reg"] = rc_idx
            wb["write_val"] = res.result

        elif mnem == "lcl_msb":
            const16 = d["const16"]
            old = d["rc_val"]
            new = ((const16 << 16) & 0xFFFF0000) | (old & 0x0000FFFF)
            wb["write_reg"] = d["rc"]
            wb["write_val"] = new

        elif mnem == "lcl_lsb":
            const16 = d["const16"]
            old = d["rc_val"]
            new = (const16 & 0xFFFF) | (old & 0xFFFF0000)
            wb["write_reg"] = d["rc"]
            wb["write_val"] = new

        elif mnem == "load":
            # load rc, ra -> rc = memoria[ra]
            addr = ra_val & 0xFFFF
            val = self.mem.read(addr)
            wb["write_reg"] = d["rc"]
            wb["write_val"] = val

        elif mnem == "store":
            # store rc, ra -> memoria[rc] = ra
            addr = d["rc"]
            addr_val = self.rf.read(addr) if False else d["rc_val"]
            addr_val = d["rc_val"]
            self.mem.write(addr_val & 0xFFFF, d["ra_val"])

        elif mnem == "jal":
            # jal end -> r31 = PC; PC = end
            self.rf.write(31, self.PC)
            self.PC = d["end24"]

        elif mnem == "jr":
            # jr rc -> PC = rc
            self.PC = d["rc_val"]

        elif mnem == "beq":
            if d["ra_val"] == d["rb_val"]:
                # PC já foi incrementado no IF
                self.PC = d["end24"]

        elif mnem == "bne":
            if d["ra_val"] != d["rb_val"]:
                self.PC = d["end24"]

        elif mnem == "j":
            self.PC = d["end24"]

        #instrucoes adicinadas
        elif mnem == "storei":
            alu.storei_op(self.mem, d["end24"], d["ra_val"])

        elif mnem == "loadi":
            val = alu.loadi_op(self.mem, d["end24"])
            wb["write_reg"] = d["rc"]
            wb["write_val"] = val
        
        elif mnem == "mul":
            res = alu.mul_op(d["ra_val"], d["rb_val"])
            wb["write_reg"] = d["rc"]
            wb["write_val"] = res.result
            self.flags.update({"neg": res.neg, "zero": res.zero,
                               "carry": res.carry, "overflow": res.overflow})

        elif mnem == "div":
            res = alu.div_op(d["ra_val"], d["rb_val"])
            wb["write_reg"] = d["rc"]
            wb["write_val"] = res.result
            self.flags.update({"neg": res.neg, "zero": res.zero,
                               "carry": res.carry, "overflow": res.overflow})

        elif mnem == "mod":
            res = alu.mod_op(d["ra_val"], d["rb_val"])
            wb["write_reg"] = d["rc"]
            wb["write_val"] = res.result
            self.flags.update({"neg": res.neg, "zero": res.zero,
                               "carry": res.carry, "overflow": res.overflow})

        elif mnem == "neg":
            res = alu.neg_op(d["ra_val"])
            wb["write_reg"] = d["rc"]
            wb["write_val"] = res.result
            self.flags.update({"neg": res.neg, "zero": res.zero,
                               "carry": res.carry, "overflow": res.overflow})

        elif mnem == "inc":
            res = alu.inc_op(d["ra_val"])
            wb["write_reg"] = d["ra"]  # incrementa o mesmo registrador
            wb["write_val"] = res.result
            self.flags.update({"neg": res.neg, "zero": res.zero,
                               "carry": res.carry, "overflow": res.overflow})

        elif mnem == "dec":
            res = alu.dec_op(d["ra_val"])
            wb["write_reg"] = d["ra"]  # decrementa o mesmo registrador
            wb["write_val"] = res.result
            self.flags.update({"neg": res.neg, "zero": res.zero,
                               "carry": res.carry, "overflow": res.overflow})
        else:
            # Caso alguma instrução seja desconhecida, pula
            pass

        # Atualiza as flags de acordo com o resultado da ALU
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
            self.rf.write(wb["write_reg"], wb["write_val"])
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



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python -m src.simulador.unidade_de_controle bin/teste3.bin")
        sys.exit(1)
    cpu = CPU(sys.argv[1])
    cpu.run(verbose=True)
