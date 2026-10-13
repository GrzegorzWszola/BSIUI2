import math
from pathlib import Path

def decimal_to_binary(N, n):
    bits = []
    for _ in range(N):
        bits.append(str(n % 2))
        n //= 2
        
    return "".join(reversed(bits))

class Compressor:
    def process_file(self, input_file):
        unique = set()
        k = 0
        with open(input_file, "rb") as f:
            # wczytanie po 64kb zeby nie zajmowac ramu
            while chunk := f.read(65536):
                # set nie dodaje duplikatów
                unique.update(chunk)
                k += len(chunk)

        self.dictionary = sorted(unique)
        self.k = k
        self.X = len(self.dictionary)
        self.N = math.ceil(math.log2(self.X))
        self.R = (8-(3+ k*self.N)% 8) % 8
        self.create_keys()

    def create_keys(self):
        values = []
        for i in range(0, self.X):
            values.append(decimal_to_binary(self.N, i))
        self.code_map = dict(zip(self.dictionary, values))

    def write_compressed(self, out, input_file):
        bits = format(self.R, "03b")

        with open(input_file, "rb") as f:
            while chunk := f.read(65536):
                bits += "".join(self.code_map[b] for b in chunk)

                full = len(bits) // 8 * 8      # ile bitów to pełne bajty
                if full:
                    out.write(int(bits[:full], 2).to_bytes(full // 8, "big"))
                bits = bits[full:]             # zostaje < 8 bitów

        # ostatni bajt: dopełnienie R bitami (tu zerami)
        if bits:
            bits += "0" * (8 - len(bits))
            out.write(bytes([int(bits, 2)]))

    def compress(self, input_file, output_dir):
        self.process_file(input_file)
        print(f"X: {self.X}")
        print(f"N: {self.N}")
        print(f"R: {self.R}")
        print(f"Dlugosc tekstu: {self.k}")
        with open(output_dir, "wb") as out:
            out.write(bytes([self.X % 256]))
            out.write(bytes(self.dictionary))
            self.write_compressed(out, input_file)

        print(f"Dlugosc po kompresji: {output_dir.stat().st_size}")



class Decompressor:
    def process_file(self, f):
            self.X = f.read(1)[0]
            if self.X == 0:         
                self.X = 256
            self.dictionary = list(f.read(self.X))
            self.N = math.ceil(math.log2(self.X))

            self.code_map = [decimal_to_binary(self.N, i) for i in range(0, self.X)]

    def _decode(self, bits, buf):
        """Dekoduje pełne kody po N bitów, zwraca niewykorzystaną resztę."""
        full = len(bits) // self.N * self.N
        for i in range(0, full, self.N):
            buf.append(self.dictionary[int(bits[i:i + self.N], 2)])
        return bits[full:]

    def decompress(self, input_file, output_path):
        with open(input_file, "rb") as f, open(output_path, "wb") as out:
            self.process_file(f)

            # pierwszy bajt danych: 3 bity R + 5 bitów danych
            first = format(f.read(1)[0], "08b")
            R = int(first[:3], 2)
            bits = first[3:]

            buf = bytearray()
            prev = None

            while chunk := f.read(65536):
                for b in chunk:
                    if prev is not None:
                        bits += format(prev, "08b")
                        bits = self._decode(bits, buf)
                    prev = b
                out.write(buf)
                buf.clear()

            # obsługa ostatniego bajtu odcinamy R bitów wypełniacza
            if prev is not None:
                bits += format(prev, "08b")[:8 - R]
            else:
                # jedyny bajt danych to ten pierwszy
                bits = bits[:len(bits) - R]

            self._decode(bits, buf)
            out.write(buf)

