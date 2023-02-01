import typing

class ReadableBuffer:
	def __init__(self, t: str):
		self.t = t
		self.pos = 0
	def read(self, bytes: int = 0) -> str:
		if bytes == 0:
			r: str = self.t[self.pos:]
			self.pos = len(self.t)
		else:
			r: str = self.t[self.pos:self.pos+bytes]
			self.pos += bytes
		return r
	def seek(self, pos: int):
		self.pos = pos

def readString(b: ReadableBuffer) -> str:
	r: bytes = b""
	while b.read(1) == "0":
		r += bytes([int(b.read(8), 2)])
	return r.decode("UTF-8")

def writeString(s: str) -> str:
	r: str = ""
	for char in s:
		r += "0" + bin(ord(char))[2:].rjust(8, "0")
	return r + "1"

def readList(b: ReadableBuffer, items: typing.Callable[[ReadableBuffer], typing.Any]):
	r = []
	while b.read(1) == "0":
		r.append(items(b))
	return r

def writeList(l: "list[str]") -> str:
	r = []
	for i in l:
		r.append("0" + i)
	return ''.join(r) + "1"

def download(s: str, filename: str = "testyfile.dat"):
	# Read bytes
	r: bytes = bytes([int(s[i:i+8], 2) for i in range(0, len(s), 8)])
	# Save
	f = open(filename, "wb")
	f.write(r)
	f.close()

def upload(filename: str) -> str:
	# Load
	f = open(filename, "rb")
	l = f.read()
	f.close()
	# Convert to bits
	r: str = ""
	for char in l:
		r += bin(char)[2:].rjust(8, "0")
	return r

if __name__ == "__main__":
	r = ReadableBuffer(writeList([writeString("Hi there"), writeString("wheee")]))
	print(readList(r, readString))