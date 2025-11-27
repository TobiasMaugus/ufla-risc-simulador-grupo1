# interpretador_de_instrucoes.py
# Lê arquivo de instrucoes (txt) e decodifica instruções de 32 bits

from typing import Tuple, Dict
import os

# Mapa de opcode (aqui usamos nomes coerentes com o PDF)
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
    "00001110": "lcl_msb",   # load const high (bits 23-8)
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
            # assume it's a 32-bit binary instruction in one line
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
    end24 = instr_bits[8:32]   # bits 23..0
    const16 = instr_bits[8:24] # bits 23..8
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

def asm_to_binary(asm_path: str, bin_path: str) -> None:
    """
    Converte arquivo assembly (.asm ou .txt) para binário (.bin).
    Salva em formato texto: address + instruções em binário contínuo (sem espaços)
    """
    REVERSE_INST = {v: k for k, v in INSTRUCOES.items()}
    
    binary_code = {}
    pc = 0
    
    with open(asm_path, "r", encoding='utf-8') as f:
        for line_num, raw in enumerate(f, 1):
            line = raw.strip()
            
            if not line or line.startswith("#"):
                continue
            
            if line.startswith("address"):
                parts = line.split()
                pc = int(parts[1])
                continue
            
            # Remove vírgulas e splits
            line_clean = line.replace(',', ' ')
            parts = line_clean.split()
            mnem = parts[0]
            
            if mnem not in REVERSE_INST:
                raise ValueError(f"Linha {line_num}: Instrução desconhecida '{mnem}'")
            
            opcode = REVERSE_INST[mnem]
            instr_bits = opcode
            
            # Analisa o formato da instrução e identifica os operandos
            if mnem == "halt":
                instr_bits += "00000000" + "00000000" + "00000000"
            
            elif mnem in ["lcl_lsb", "lcl_msb"]:
                # Formato: lcl_lsb r1, 10
                rc = int(parts[1].replace('r', ''))
                const16 = int(parts[2])
                instr_bits += format(const16, '016b') + format(rc, '08b')
            
            elif mnem in ["add", "sub", "xor", "or", "and", "mul", "div", "mod"]:
                # Formato: add r1, r2, r3
                ra = int(parts[1].replace('r', ''))
                rb = int(parts[2].replace('r', ''))
                rc = int(parts[3].replace('r', ''))
                instr_bits += format(ra, '08b') + format(rb, '08b') + format(rc, '08b')
            
            elif mnem in ["inc", "dec"]:
                # Formato: inc r1
                ra = int(parts[1].replace('r', ''))
                instr_bits += format(ra, '08b') + "00000000" + "00000000"
            
            elif mnem in ["passa", "passnota", "neg"]:
                # Formato: passa ra, rc
                ra = int(parts[1].replace('r', ''))
                rc = int(parts[2].replace('r', ''))
                instr_bits += format(ra, '08b') + "00000000" + format(rc, '08b')
            
            else:
                # Para outras instruções, preencher com zeros
                instr_bits += "00000000" + "00000000" + "00000000"
            
            if len(instr_bits) != 32:
                raise ValueError(f"Linha {line_num}: Instrução com tamanho inválido: {len(instr_bits)} bits")
            
            binary_code[pc] = instr_bits
            pc += 1
    
    # Salva em formato de texto
    os.makedirs(os.path.dirname(bin_path), exist_ok=True)
    with open(bin_path, "w", encoding='utf-8') as f:
        f.write(f"address {format(0, '032b')}\n")
        for addr in sorted(binary_code.keys()):
            f.write(binary_code[addr] + "\n")
    
    print(f"✓ Convertido: {asm_path} -> {bin_path}")
    