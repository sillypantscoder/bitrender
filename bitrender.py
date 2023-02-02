import bitseq
import bitmath
import pygame

MODS: "list[tuple[str, str]]" = [
	("rect", "bbbbiiiii"),
	("fill", "bbbb"),
	("circle", "bbbbiiiii"),
	("poly", "bbbbpi"),
	("line", "bbbbiiiii")
]

def read_modification(b: bitseq.ReadableBuffer) -> list:
	modtype = b.read(2)
	if modtype == "00":
		op: tuple = MODS[int(b.read(4), 2)]
		r: list = []
		r.append(op[0])
		#print("Loading mod " + op[0])
		for c in op[1]:
			if c == "b":
				r.append(int(b.read(8), 2))
			elif c == "i":
				r.append(bitmath.read_math(b))
			elif c == "p":
				coords = []
				while b.read(1) == "0":
					coords.append([bitmath.read_math(b), bitmath.read_math(b)])
				r.append(coords)
		return ["mod", r]
	elif modtype == "01":
		# Set var
		#print("Loading set")
		return ["set", bitseq.readString(b), bitmath.read_math(b)]
	elif modtype == "10":
		# If
		#print("Loading if")
		return ["if", bitmath.read_math(b), bitseq.readString(b)]
	elif modtype == "11":
		# Tag
		#print("Loading tag")
		return ["tag", bitseq.readString(b)]
	else: return [""]

def write_modification(l: list) -> str:
	if l[0] == "mod":
		mod = l[1]
		modn = [x[0] for x in MODS].index(mod[0])
		#print(f"Saving mod {MODS[modn][0]}")
		r = bin(modn)[2:].rjust(4, "0")
		if len(MODS[modn][1]) != len(mod) - 1:
			print(f"--- ERROR: Mod {MODS[modn][0]} requires {len(MODS[modn][1])} arguments but got {len(mod) - 1}")
		for c in range(len(mod))[1:]:
			t = MODS[modn][1][c-1]
			if t == "b":
				if not isinstance(mod[c], int):
					print(f"--- ERROR: Argument {c} of mod {MODS[modn][0]} on is not of type int")
				r += bin(mod[c])[2:].rjust(8, "0")
			elif t == "i":
				if not isinstance(mod[c], (list, int, str)):
					print(f"--- ERROR: Argument {c} of mod {MODS[modn][0]} is not of type list|int|str")
				r += bitmath.write_math(mod[c])
			elif t == "p":
				if not isinstance(mod[c], list):
					print(f"--- ERROR: Argument {c} of mod {MODS[modn][0]} is not of type list")
				for i in mod[c]:
					r += "0"
					r += bitmath.write_math(i[0])
					r += bitmath.write_math(i[1])
				r += "1"
		return "00" + r
	elif l[0] == "set":
		#print("Saving set")
		return "01" + bitseq.writeString(l[1]) + bitmath.write_math(l[2])
	elif l[0] == "if":
		#print("Saving if")
		return "10" + bitmath.write_math(l[1]) + bitseq.writeString(l[2])
	elif l[0] == "tag":
		#print("Saving tag")
		return "11" + bitseq.writeString(l[1])
	else: return ""

def exec_modification(l: list, s: pygame.Surface, variables: "dict[str, int]" = {}) -> pygame.Surface:
	newS = s.copy()
	em = lambda n: bitmath.exec_math(n, variables)
	if l[0] == "rect": pygame.draw.rect(newS, (l[1], l[2], l[3], l[4]), pygame.Rect(round(em(l[5])), round(em(l[6])), round(em(l[7])), round(em(l[8]))), round(em(l[9])))
	elif l[0] == "fill": newS.fill((l[1], l[2], l[3], l[4]))
	elif l[0] == "circle": pygame.draw.ellipse(newS, (l[1], l[2], l[3], l[4]), pygame.Rect(em(l[5]), em(l[6]), em(l[7]), em(l[8])), em(l[9]))
	elif l[0] == "poly": pygame.draw.polygon(newS, (l[1], l[2], l[3], l[4]), [[em(x[0]), em(x[1])] for x in l[5]], em(l[6]))
	elif l[0] == "line": pygame.draw.line(newS, (l[1], l[2], l[3], l[4]), (em(l[5]), em(l[6])), (em(l[7]), em(l[8])), em(l[9]))
	return newS # type: ignore

def read_stage(b: bitseq.ReadableBuffer) -> list:
	size = [
		bitmath.read_math(b),
		bitmath.read_math(b)
	]
	mods = bitseq.readList(b, read_modification)
	return [size, mods]

def write_stage(l: list) -> str:
	size = bitmath.write_math(l[0][0]) + bitmath.write_math(l[0][1])
	mods = bitseq.writeList([write_modification(x) for x in l[1]])
	return size + mods

def exec_stage(l: list, variables: "dict[str, int]") -> pygame.Surface:
	s = pygame.Surface((bitmath.exec_math(l[0][0]), bitmath.exec_math(l[0][1])), pygame.SRCALPHA)
	modlist = l[1]
	i = 0
	while i < len(modlist):
		m = modlist[i]
		if m[0] == "mod":
			s = exec_modification(m[1], s, variables)
		elif m[0] == "set":
			variables[m[1]] = bitmath.exec_math(m[2], variables)
		elif m[0] == "if":
			if bitmath.exec_math(m[1], variables) != 0:
				i = [x[1] for x in modlist].index(m[2])
		elif m[0] == "tag":
			pass
		i += 1
	return s

if __name__ == "__main__":
	"""import pygame
	screen = pygame.display.set_mode((100, 100))
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
		screen.fill((0, 0, 0))
		screen.blit(exec_stage(read_stage(bitseq.ReadableBuffer(bitseq.upload("example.dat"))), {"some_number": 4}), (0, 0))
		pygame.display.flip()"""
	r = [
		[200, 200],
		[
			["mod", ["fill", 255, 255, 255, 0]],
			["set", "treeX", 50],
			["set", "treeMod", ["+", 1, ["/", ["*", "x", "x"], ["*", ["*", 1000, 1000], 10]]]],
			["set", "treeWidth", ["+", ["round", ["*", 30, "treeMod"]], ["*", ["random"], ["round", ["*", 65, "treeMod"]]]]],
			["set", "treeHeight", ["+", ["round", ["*", 50, "treeMod"]], ["*", ["random"], ["round", ["*", 100, "treeMod"]]]]],
			["set", "treeHeight", ["+", "treeHeight", ["/", "treeWidth", 2]]],
			# Base
			["mod", ["rect", 100, 50,  0, 255, 	"treeX", ["-", 200, "treeHeight"], "treeWidth", "treeHeight", 	 0]],
			["mod", ["rect",  50,  0, 10, 255,	"treeX", ["-", 200, "treeHeight"], "treeWidth", "treeHeight", 	10]],
			# Leaves
			["mod", ["circle", 0, 150, 0, 255, 	["-", ["+", "treeX", ["/", "treeWidth", 2]], 50], ["-", ["-", 200, "treeHeight"], 50], 100, 100, 	0]]
		]
	]
	#bitseq.download(write_stage(r), "tree.dat")
	b = read_stage(bitseq.ReadableBuffer(write_stage(r)))
	[
		pygame.image.save(exec_stage(b, {"x": x}), f"images2/tree{x}.png")
		for x in range(0, 1000, 100)
	]