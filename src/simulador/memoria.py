# memoria.py
# Memória word-addressed com 65536 posições (0..65535), cada posição guarda 32 bits (int)

MEM_SIZE = 65536

class Memoria:
    def __init__(self):
        self._mem = [0] * MEM_SIZE

    def load_program(self, mem_map):
        """mem_map: dict endereco->instricao_binaria_string(32)"""
        for addr, bits in mem_map.items():
            if addr < 0 or addr >= MEM_SIZE:
                raise IndexError("Endereço de programa fora do alcance")
            self._mem[addr] = int(bits, 2)

    def read(self, addr: int) -> int:
        if addr < 0 or addr >= MEM_SIZE:
            raise IndexError("Leitura fora do intervalo de memoria")
        return self._mem[addr] & 0xFFFFFFFF

    def write(self, addr: int, value: int):
        if addr < 0 or addr >= MEM_SIZE:
            raise IndexError("Escrita fora do intervalo de memoria")
        self._mem[addr] = value & 0xFFFFFFFF

    def dump_modified(self):
        """Retorna pares (addr, value) para posições que não são zero (útil para saída)"""
        return [(i, v) for i, v in enumerate(self._mem) if v != 0]
