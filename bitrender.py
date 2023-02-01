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
	elif modtype == "10":
		# If
		return ["if", bitmath.read_math(b), bitseq.readString(b)]
	elif modtype == "11":
		# Tag
		return ["tag", bitseq.readString(b)]
	else: return [""]

def write_modification(l: list) -> str:
	if l[0] == "mod":
		mod = l[1]
		modn = [x[0] for x in MODS].index(mod[0])
		print(f"Saving mod {MODS[modn][0]}")
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
				if not isinstance(mod[c], (list, int)):
					print(f"--- ERROR: Argument {c} of mod {MODS[modn][0]} is not of type list|int")
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
	elif l[0] == "if":
		print("Saving if")
		return "10" + bitmath.write_math(l[1]) + bitseq.writeString(l[2])
	elif l[0] == "tag":
		print("Saving tag")
		return "11" + bitseq.writeString(l[1])
	else: return ""

def exec_modification(l: list, s: pygame.Surface) -> pygame.Surface:
	newS = s.copy()
	if l[0] == "rect": pygame.draw.rect(newS, (l[1], l[2], l[3], l[4]), pygame.Rect(round(bitmath.exec_math(l[5])), round(bitmath.exec_math(l[6])), round(bitmath.exec_math(l[7])), round(bitmath.exec_math(l[8]))), round(bitmath.exec_math(l[9])))
	elif l[0] == "fill": newS.fill((l[1], l[2], l[3], l[4]))
	elif l[0] == "circle": pygame.draw.ellipse(newS, (l[1], l[2], l[3], l[4]), pygame.Rect(bitmath.exec_math(l[5]), bitmath.exec_math(l[6]), bitmath.exec_math(l[7]), bitmath.exec_math(l[8])), bitmath.exec_math(l[9]))
	elif l[0] == "poly": pygame.draw.polygon(newS, (l[1], l[2], l[3], l[4]), [[bitmath.exec_math(x[0]), bitmath.exec_math(x[1])] for x in l[5]], bitmath.exec_math(l[6]))
	elif l[0] == "line": pygame.draw.line(newS, (l[1], l[2], l[3], l[4]), (bitmath.exec_math(l[5]), bitmath.exec_math(l[6])), (bitmath.exec_math(l[7]), bitmath.exec_math(l[8])), bitmath.exec_math(l[9]))
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
			s = exec_modification(m[1], s)
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
		[300, 300],
		[
			["mod", ["fill", 255, 255, 255, 0]],
			["mod", ["rect", 200, 200, 255, 255, 	50,  100, 200, 200, 	0]],
			["mod", ["rect", 50,  0,   10,  255, 	50,  100, 200, 200, 	10]],
			["mod", ["poly", 200, 200, 255, 255, [[50, 100], [150, 0], [250, 100]], 0]],
			["mod", ["poly", 50,  0,   10, 	255, [[50, 100], [150, 0], [250, 100]], 10]],
			# Door
			["if", ["!", ["<", "personStatus", 61]], "Line314"],
				["mod", ["rect", 100, 100, 100, 255,	85, 200, 50, 90,  	0]],
				["mod", ["circle", 0, 0,   0,   255, 	95, 240, 10, 10, 	0]],
				["if", 1, "Line317"],
			["tag", "Line314"],
				["mod", ["rect", 255, 255, 255, 255, 	85, 200, 50, 90, 0]],
				["mod", ["rect", 100, 100, 100, 255, 	125, 200, 10, 90, 0]],
			["tag", "Line317"],
			# Window
			["if", ["!", ["<", "personStatus", 2]], "Line323"],
				["if", ["!", ["=", "personStatus", 1]], "Line319A"],
					["mod", ["rect", 150, 150, 100, 255, 	160, 135, 60, 60, 	0]],
				["tag", "Line319A"],
				["if", ["=", "personStatus", 1], "Line319B"],
					["mod", ["rect",  50,  50,  50, 255, 	160, 135, 60, 60, 	0]],
				["tag", "Line319B"],
				# rest
				["mod", ["rect", 50, 0, 10, 255, 	160, 135,  60,  60, 	10]],
				["mod", ["line", 50, 0, 10, 255, 	190, 135, 190, 195, 	10]],
				["mod", ["line", 50, 0, 10, 255, 	160, 165, 220, 165, 	10]],
				["if", 1, "Line328"],
			["tag", "Line323"],
			["if", ["!", ["||", ["<", "personStatus", 15], ["=", "personStatus", 15]]], "Line325"],
				["mod", ["rect", 50, 0, 10, 255, 	160, 125,  60,  60, 	0]],
				["if", 1, "Line328"],
			["tag", "Line325"],
				["mod", ["rect", 150, 150, 100, 255, 160, 135, 60,  60, 	0]],
				["mod", ["rect", 50, 0, 10, 255, 	160, 135,  60,  60, 	10]],
			["tag", "Line328"]
		]
	]
	bitseq.download(write_stage(r), "house.dat")
	b = read_stage(bitseq.ReadableBuffer(write_stage(r)))
	[
		pygame.image.save(exec_stage(b, {"personStatus": x}), f"images/house{x}.png")
		for x in range(62)
	]