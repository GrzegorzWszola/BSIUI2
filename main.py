from pathlib import Path
import sys
from compressor import Compressor, Decompressor
from Profiler import Profiler
import time

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Nie podano ścieżki do pliku")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = input_path.with_name(f"{input_path.stem}_compressed")

    dec_output_path = input_path.with_name(f"{input_path.stem}_decompressed")

    compressor = Compressor()

    profiler = Profiler()
    # with profiler.measure("Kompresja", ""):
    #     compressor.compress(input_path, output_path)

    decompressor = Decompressor()
    # with profiler.measure("Dekompresja", ""):
    #     decompressor.decompress(output_path, dec_output_path)

    t = time.perf_counter()
    compressor.compress(input_path, output_path)
    print(f"Kompresja: {time.perf_counter() - t:.2f} s")

    t = time.perf_counter()
    decompressor.decompress(output_path, dec_output_path)
    print(f"Dekompresja: {time.perf_counter() - t:.2f} s")

    profiler.report()