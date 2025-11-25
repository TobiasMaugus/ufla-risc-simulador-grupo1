# Lê arquivo de instrucoes (texto binário) com diretiva 'address' e decodifica instruções de 32 bits

from typing import Tuple, Dict

#opcode -> instruction
INSTRUCOES = {
    "00000001": "add",
    "00000010": "sub",
    "00000011": "zeros",
    "00000100": "xor",
    "00000101": "or",
    "00000110": "passnota",  # not
    "00000111": "and",
    "00001000": "asl",
    "00001001": "asr",
    "00001010": "lsl",
    "00001011": "lsr",
    "00001100": "passa",     # copy
    "00001110": "lcl_msb",   # load const high
    "00001111": "lcl_lsb",   # load const low
    "00010000": "load",
    "00010001": "store",
    "00010010": "jal",
    "00010011": "jr",
    "00010100": "beq",
    "00010101": "bne",
    "00010110": "j",
    "00010111": "storei",
    "00011000": "loadi",
    "00011001": "mul",
    "00011010": "div",
    "00011011": "mod",
    "00011100": "neg",
    "00011101": "inc",
    "00011110": "dec",
    "11111111": "halt"
}

def parse_program(path: str) -> Dict[int, str]:
    """
    Lê arquivo de instruções (texto) e retorna dicionário memória: endereco (int) -> instrução (32-bit string)
    """
    mem = {}
    pc = 0
    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("address"):
                parts = line.split()
                if len(parts) >= 2:
                    pc = int(parts[1], 2)
                continue
            instr = "".join(line.split())
            if len(instr) != 32:
                raise ValueError(f"Instrucao com tamanho != 32: '{instr}'")
            mem[pc] = instr
            pc += 1
    return mem

def decode_instruction(instr_bits: str) -> dict:
    """
    Recebe 32-bit string e retorna dict com campos:
    opcode (8), ra(8), rb(8), rc(8), end24 (24), const16 (16), mnemonic
    """
    opcode = instr_bits[0:8]
    ra = instr_bits[8:16]
    rb = instr_bits[16:24]
    rc = instr_bits[24:32]
    # campos alternativos
    end24 = instr_bits[8:32] 
    const16 = instr_bits[8:24] 
    mnemonic = INSTRUCOES.get(opcode, "unknown")
    return {
        "bits": instr_bits,
        "opcode": opcode,
        "mnemonic": mnemonic,
        "ra": int(ra, 2),
        "rb": int(rb, 2),
        "rc": int(rc, 2),
        "end24": int(end24, 2),
        "const16": int(const16, 2)
    }

# exemplo de uso:
# mem = parse_program("binarios/programa.txt")
# instr = decode_instruction(mem[0])