import base64
import xxhash

class mt:
    def __init__(self, seed: int):
        self.mt = [0] * 624
        self.index = 624
        self.mt[0] = seed & 0xFFFFFFFF
        for i in range(1, 624):
            self.mt[i] = (1812433253 * (self.mt[i - 1] ^ (self.mt[i - 1] >> 30)) + i) & 0xFFFFFFFF

    def _twist(self):
        for i in range(624):
            y = (self.mt[i] & 0x80000000) + (self.mt[(i + 1) % 624] & 0x7fffffff)
            self.mt[i] = self.mt[(i + 397) % 624] ^ (y >> 1)
            if y & 1:
                self.mt[i] ^= 0x9908b0df
        self.index = 0

    def next_u32(self):
        if self.index >= 624:
            self._twist()

        y = self.mt[self.index]
        self.index += 1

        y ^= (y >> 11)
        y ^= (y << 7) & 0x9d2c5680
        y ^= (y << 15) & 0xefc60000
        y ^= (y >> 18)

        return y & 0xFFFFFFFF

    def next_u31(self):
        return self.next_u32() >> 1

def calculate_xxhash(data: bytes) -> int:
    return xxhash.xxh32(data, seed=0).intdigest()

def next_bytes(rng: mt, length: int) -> bytearray:
    buf = bytearray(length)
    for i in range((length + 3) // 4):
        val = rng.next_u31()
        offset = i * 4
        for j in range(4):
            idx = offset + j
            if idx < length:
                buf[idx] = (val >> (j * 8)) & 0xFF
    return buf

if __name__ == "__main__":
    filename = input("input fileName: ")
    seed = calculate_xxhash(filename.encode("utf-8"))
    rng = mt(seed)
    buf = next_bytes(rng, 15)
    password = base64.b64encode(buf).decode("utf-8")

    # print("xxhash32 seed:", seed)
    # print("next_buf:", list(buf))
    print("Password:", password)