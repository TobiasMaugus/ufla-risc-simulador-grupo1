# alu.py
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
    ures = (ua - ub) & 0x1FFFFFFFF  # allow borrow detection
    res = ures & MASK32
    # Borrow -> carry semantics: define carry=1 if borrow occurred? 
    # We'll use carry = 1 if unsigned borrow did NOT occur (common variant),
    # but PDF asks carry flag for subtraction. Here we set carry = 1 if borrow occurred (ua < ub).
    carry = 1 if ua < ub else 0
    sa, sb, sres = to_signed32(ua), to_signed32(ub), to_signed32(res)
    overflow = 1 if ((sa >=0 and sb < 0 and sres < 0) or (sa < 0 and sb >=0 and sres >=0)) else 0
    neg = 1 if (res & 0x80000000) else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, carry, overflow)

def zeros_op():
    res = 0
    return ALUResult(res, 0, 1, 0, 0)

def xor_op(a, b):
    res = (a ^ b) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def or_op(a, b):
    res = (a | b) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def not_op(a):
    res = (~a) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def and_op(a, b):
    res = (a & b) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def asl_op(a, b_shifts):  # arithmetic left == logical left for typical two's complement
    sh = b_shifts & 0x1F
    res = (a << sh) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def asr_op(a, b_shifts):
    sh = b_shifts & 0x1F
    signed = to_signed32(a)
    res = (signed >> sh) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def lsl_op(a, b_shifts):
    sh = b_shifts & 0x1F
    res = (a << sh) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def lsr_op(a, b_shifts):
    sh = b_shifts & 0x1F
    res = (a & MASK32) >> sh
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def passa_op(a):
    res = a & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

# =====================================
# 🧩 Novas operações ALU (uRISC estendido)
# =====================================


def mul_op(a, b):
    res = (a * b) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

def div_op(a, b):
    if b == 0:
        res = 0
    else:
        res = int(a // b) & MASK32
    neg = 1 if res & 0x80000000 else 0
    zero = 1 if res == 0 else 0
    return ALUResult(res, neg, zero, 0, 0)

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

