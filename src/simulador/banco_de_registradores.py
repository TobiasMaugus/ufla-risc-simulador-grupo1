# banco_de_registradores.py
# 32 registradores de 32 bits: r0..r31

class RegisterFile:
    def __init__(self):
        self.regs = [0] * 32

    def read(self, idx: int) -> int:
        if idx < 0 or idx >= 32:
            raise IndexError("Registrador fora do intervalo")
        return self.regs[idx] & 0xFFFFFFFF

    def write(self, idx: int, value: int):
        if idx < 0 or idx >= 32:
            raise IndexError("Registrador fora do intervalo")
        self.regs[idx] = value & 0xFFFFFFFF

    def dump_nonzero(self):
        return [(i, v) for i, v in enumerate(self.regs) if v != 0]
