# banco_de_registradores.py
# Implementa o banco de registradores do processador
# 32 registradores de 32 bits (r0 a r31) para armazenamento temporário de dados

class RegisterFile:
    # Inicializa todos os 32 registradores com valor zero
    def __init__(self):
        # self.regs é uma lista onde cada posição representa um registrador
        self.regs = [0] * 32

    # Lê o valor de um registrador específico
    def read(self, idx: int) -> int:
        # Verifica se o índice está dentro do intervalo válido (0-31)
        if idx < 0 or idx >= 32:
            raise IndexError("Registrador fora do intervalo")
        # Retorna o valor do registrador aplicando máscara de 32 bits (simula overflow)
        return self.regs[idx] & 0xFFFFFFFF

    # Escreve um valor em um registrador específico
    def write(self, idx: int, value: int):
        # Verifica se o índice está dentro do intervalo válido (0-31)
        if idx < 0 or idx >= 32:
            raise IndexError("Registrador fora do intervalo")
        # Armazena o valor no registrador aplicando máscara de 32 bits (simula overflow)
        self.regs[idx] = value & 0xFFFFFFFF

    # Retorna lista de registradores com valores diferentes de zero
    # Útil para o log ou debug - mostra apenas registradores que estão sendo usados
    def dump_nonzero(self):
        # Formato: [(índice, valor), (índice, valor), ...]
        return [(i, v) for i, v in enumerate(self.regs) if v != 0]