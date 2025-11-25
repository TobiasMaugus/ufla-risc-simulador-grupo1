# Implementa as operações ALU e cálculo de flags (32-bit)

MASK32 = 0xFFFFFFFF

def to_unsigned32(x):
    return x & MASK32

def to_signed32(x):
    x = x & MASK32
    return x if x < 0x80000000 else x - 0x100000000

class ALUResult:
    def __init__(self, result, neg, zero, carry, overflow):
        self.result = result & MASK32
        self.neg = neg
        self.zero = zero
        self.carry = carry
        self.overflow = overflow

def add_op(a, b):
    ua = a & MASK32
    ub = b & MASK32
    ures = ua + ub
    res = ures & MASK32
    carry = 1 if ures >> 32 else 0
    sa, sb, sres = to_signed32(ua), to_signed32(ub), to_signed32(res)
    overflow = 1 if ((sa >= 0 and sb >= 0 and sres < 0) or (sa < 0 and sb < 0 and sres >= 0)) else 0
    neg = 1 if (res & 0x80000000) else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, carry, overflow)

def sub_op(a, b):
    ua = a & MASK32
    ub = b & MASK32
    ures = (ua - ub) & 0x1FFFFFFFF 
    res = ures & MASK32
    carry = 1 if ua < ub else 0
    sa, sb, sres = to_signed32(ua), to_signed32(ub), to_signed32(res)
    overflow = 1 if ((sa >=0 and sb < 0 and sres < 0) or (sa < 0 and sb >=0 and sres >=0)) else 0
    neg = 1 if (res & 0x80000000) else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, carry, overflow)

# Operação ZEROS: define o resultado como zero
# Instrução: zeros rc -> rc = 0
def zeros_op():
    res = 0
    # Flags: neg=0 (não é negativo), zero=1 (resultado é zero), 
    # carry=0 (sem carry), overflow=0 (sem overflow)
    return ALUResult(res, 0, 1, 0, 0)

# Operação XOR: OU exclusivo bit a bit
# Instrução: xor rc, ra, rb -> rc = ra XOR rb
def xor_op(a, b):
    # Operação XOR com máscara de 32 bits (evita números representados por mais de 32 bits)
    res = (a ^ b) & MASK32  
    # Flag negativo: verifica se o bit mais significativo (bit 31) é 1
    neg = 1 if res & 0x80000000 else 0
    # Flag zero: verifica se o resultado final é zero, todos os bits são 0
    zero = 1 if res == 0 else 0
    # Operações lógicas não geram carry nem overflow
    return ALUResult(res, neg, zero, 0, 0)

# Operação OR: OU lógico bit a bit  
# Instrução: or rc, ra, rb -> rc = ra OR rb
def or_op(a, b):
    # Operação OR com máscara de 32 bits (evita números representados por mais de 32 bits)
    res = (a | b) & MASK32
    # Flag negativo: verifica se o bit mais significativo (bit 31) é 1
    neg = 1 if res & 0x80000000 else 0
    # Flag zero: verifica se o resultado final é zero, todos os bits são 0
    zero = 1 if res == 0 else 0
    # Operações lógicas não geram carry nem overflow
    return ALUResult(res, neg, zero, 0, 0)

    # Operação NOT: negação lógica, inverte todos os bits
    # Instrução: passnota rc, ra -> rc = NOT ra
def not_op(a):
    # Inverte todos os bits (0 vira 1, 1 vira 0)
    res = (~a) & MASK32  # Operação NOT com máscara de 32 bits
    # Flag negativo: verifica se o bit mais significativo (bit 31) é 1
    neg = 1 if res & 0x80000000 else 0
    # Flag zero: verifica se todos os bits são zero após a negação
    zero = 1 if res == 0 else 0
    # Operações lógicas não geram carry nem overflow
    return ALUResult(res, neg, zero, 0, 0)

    # Operação AND: E lógico bit a bit
    # Instrução: and rc, ra, rb -> rc = ra AND rb  
def and_op(a, b):
    # Cada bit do resultado é 1 apenas se ambos bits correspondentes forem 1
    res = (a & b) & MASK32  # Operação AND com máscara de 32 bits
    # Flag negativo: verifica se o bit mais significativo (bit 31) é 1
    neg = 1 if res & 0x80000000 else 0
     # Flag zero: verifica se o resultado final é zero, todos os bits são 0
    zero = 1 if res == 0 else 0
    # Operações lógicas não geram carry nem overflow
    return ALUResult(res, neg, zero, 0, 0)

def passa_op(a):
    res = a & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

# NOVAS OPERAÇÕES ALU (uRISC ESTENDIDO)

def mod_op(a, b):
    if b == 0:
        res = 0
    else:
        res = int(a % b) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def neg_op(a):
    res = (-a) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def inc_op(a):
    res = (a + 1) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def dec_op(a):
    res = (a - 1) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def asl_op(a, b_shifts):  # arithmetic left == logical left for typical two's complement
    sh = b_shifts & 0x1F  # Máscara para garantir shift máximo de 31 bits
    res = (a << sh) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def asr_op(a, b_shifts): # Arithmetic Shift Right (Preserva o sinal)
    sh = b_shifts & 0x1F
    signed = to_signed32(a) # Converte para signed para o Python propagar o bit de sinal
    res = (signed >> sh) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def lsl_op(a, b_shifts): # Logical Shift Left (Idêntico ao ASL nesta implementação)
    sh = b_shifts & 0x1F
    res = (a << sh) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def lsr_op(a, b_shifts): # Logical Shift Right (Preenche com zeros)
    sh = b_shifts & 0x1F
    res = (a & MASK32) >> sh # Garante operação unsigned
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)
