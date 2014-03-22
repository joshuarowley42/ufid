import logging

class UFID:
	def __init__(self, Version = 1,
		Flags = 0,
		Diameter = 0,
		Tolerance = 0,
		Tg = 0,
		TPrint = 100,
		TMin = 50,
		TMax = 0,
		TChamber = 0,
		TBed = 0,
		Color = "000000",
		Alpha = 0,
		MaterialProp = 0,
		MixtureID = 0,
		Volume = 0,
		GTIN = 0):

		self.UFIDUrlRoot = "http://ufids.org/#"

		self.DataStructure = []

		self.DataStructure.append(["Version", 	8, 	lambda x: int(x)])
		self.DataStructure.append(["Flags", 	8, 	lambda x: int(x)])
		self.DataStructure.append(["Diameter", 	9, 	lambda x: int((x-x%0.01)*100)])
		self.DataStructure.append(["Tolerance",	7, 	lambda x: int((x-x%0.01)*100)])
		self.DataStructure.append(["Tg", 	8, 	lambda x: int(x-x%1)])
		self.DataStructure.append(["TPrint", 	8, 	lambda x: int(x-x%1-100)])
		self.DataStructure.append(["TMin", 	8, 	lambda x: int(x-x%1-50)])
		self.DataStructure.append(["TMax", 	8, 	lambda x: int((x/2)-(x/2)%1)])
		self.DataStructure.append(["TChamber", 	8, 	lambda x: int(x-x%1)])
		self.DataStructure.append(["TBed", 	8, 	lambda x: int(x-x%1)])
		self.DataStructure.append(["Color", 	24, 	lambda x: int(x,16)])
		self.DataStructure.append(["Alpha", 	3, 	lambda x: int((x*8/100)-(x*8/100)%1)])
		self.DataStructure.append(["MaterialProp", 5, 	lambda x: int(x)])
		self.DataStructure.append(["MixtureID",	8, 	lambda x: int(x)])
		self.DataStructure.append(["Volume", 	16, 	lambda x: int((x*10)-(x*10)%1)])
		self.DataStructure.append(["GTIN", 	40, 	lambda x: int(x)])

		self.Binary = ""
		
		for Element in self.DataStructure:
			Val		= eval(Element[0])
			BitLength 	= Element[1]
			MappedVal	= Element[2](Val)
			Binary 		= self.IntToBin(MappedVal, BitLength)
			self.Binary 	+= Binary

			logging.debug(" Element: "+str(Element))
			logging.debug(" \tInput Value  : "+str(Val))
			logging.debug(" \tMapped Value : "+str(MappedVal))
			logging.debug(" \tBinary Value : "+str(Binary))

		logging.debug(" Binary Output: " + self.Binary)

		self.Hex = hex(eval("0b"+self.Binary))
		self.Hex = "0"+self.Hex[2:-1] # Truncate 0x...L and add a leading 0. FIXME The extra zero has been added without understanding why it is not generated..

		logging.debug(" Hex Output:    " + self.Hex)


	def IntToBin(self, Int, Length=8):
		Bin = str(bin(Int))[2:]
		if len(Bin)>Length:
			logging.warning("[fixme::] Value out of range - defaulting to 0")
			return "0"*Length
		Bin = "0"*(Length-len(Bin))+Bin 	# Pad with 0's
		return Bin


	def GetUFIDUrl(self):
		return self.UFIDUrlRoot + self.Hex



		
