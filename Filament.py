

class Filament:
	def __init__(self, Cursor, FilamentID):
		Cursor.execute ("SELECT Filaments.*, Manufacturers.* FROM Filaments \
					JOIN Manufacturers ON Filaments.ManufacturerID = Manufacturers.ManufacturerID \
					WHERE FilamentID="+str(int(FilamentTable.FilamentID)))

		Results = Cursor.fetchall()
		
		self.Filament = {}		

		self.Filament["ID"] = FilamentID
		self.Filament["Name"] = Results["Filaments.Name"]
		self.Filament["Code"] = Results["Filaments.ManufacturerID"]

		Manufacturer =  {}
		self.Filament.Manufacturer["ID"] = Results["Filaments.ManufacturerID"]
		self.Filament.Manufacturer["Name"] = Results["Manufacturers.Name"]


		self.Filament["Diam"] = Results["Filaments.Diameter"]

		self.Filament["Manufacturer"] = Manufacturer

		return self

	def GetDict(self):
		return self.Filament
	

