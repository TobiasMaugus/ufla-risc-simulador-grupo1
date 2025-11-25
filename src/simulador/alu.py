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