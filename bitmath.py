import bitseq
import math

OPERATORS: "list[tuple[str, int]]" = [
	("+", 2),
	("-", 2),
	("*", 2),
	("/", 2),
	("sqrt", 1),
	("if", 3),
	("^", 2),
	("%", 2),
	("<", 2),
	("=", 2),
	(">", 2),
	("random", 0),
	("&&", 2),
	("||", 2),
	("!", 1),
	("round", 1)
]

def read_math(b: bitseq.ReadableBuffer) -> list or int or str:
	if b.read(1) == "0":
		operator: tuple = OPERATORS[int(b.read(4), 2)]
		return [operator[0], *[read_math(b) for i in range(operator[1])]]
	else:
		if b.read(1) == "0":
			return int(b.read(12), 2) # type: ignore
		else:
			return bitseq.readString(b) # type: ignore

def write_math(l: list or int or str) -> str:
	if isinstance(l, int):
		if l > 4095: print(f"--- ERROR: {l} is too big to fit in 12 bits")
		return "10" + bin(l)[2:].rjust(12, "0")
	if isinstance(l, str):
		return "11" + bitseq.writeString(l)
	r: str = "0"
	operator = [x[0] for x in OPERATORS].index(l[0])
	r += bin(operator)[2:].rjust(4, "0")
	for i in l[1:]:
		r += write_math(i)
	return r

def exec_math(l: list or int, variables: "dict[str, int]" = {}) -> int:
	if isinstance(l, list):
		import random
		x = lambda n: exec_math(l[n], variables)
		if l[0] == "+": return x(1) + x(2)
		elif l[0] == "-": return x(1) - x(2)
		elif l[0] == "*": return x(1) * x(2)
		elif l[0] == "/": return x(1) / x(2) # type: ignore
		elif l[0] == "sqrt": return math.sqrt(x(1)) # type: ignore
		elif l[0] == "if": return x(2) if x(1) else x(3)
		elif l[0] == "^": return math.pow(x(1), x(2)) # type: ignore
		elif l[0] == "%": return x(1) % x(2)
		elif l[0] == "<": return 1 if x(1) < x(2) else 0
		elif l[0] == "=": return 1 if x(1) == x(2) else 0
		elif l[0] == ">": return 1 if x(1) > x(2) else 0
		elif l[0] == "random": return random.random() # type: ignore
		elif l[0] == "&&": return (x(1) != 0) and (x(2) != 0)
		elif l[0] == "||": return (x(1) != 0) or (x(2) != 0)
		elif l[0] == "!": return not (x(1) != 0)
		elif l[0] == "round": return round(x(1))
		else: return 0
	elif isinstance(l, str):
		if l not in variables:
			print(f"--- ERROR: Variable {l} doesn't exist! Using 0 as default value.")
			return 0
		else:
			return variables[l]
	else:
		return l

if __name__ == "__main__":
	r = bitseq.ReadableBuffer(write_math(["round", ["-", ["^", 2, 16], 1]]))
	print(exec_math(read_math(r)))