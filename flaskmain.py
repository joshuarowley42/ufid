#!/usr/bin/python

from flask import Flask, render_template, g, request
import MySQLdb
import MySQLdb.cursors
app = Flask(__name__)
import Filament

@app.before_request
def before_request():
	DB = MySQLdb.connect('localhost', "UFID", "UFID", "UFID",cursorclass=MySQLdb.cursors.DictCursor);
	DB.autocommit(True)
	g.DBCursor = DB.cursor()

	Query = "CREATE TEMPORARY TABLE IF NOT EXISTS TmpTable AS (\
			SELECT \
			COUNT(Filaments.FilamentID) AS Count, \
			Filaments.ManufacturerID AS ManufacturerID \
			FROM Filaments \
			GROUP BY Filaments.ManufacturerID \
			);"
	g.DBCursor.execute(Query)

	Query = "SELECT \
			Manufacturers.ManufacturerID as ManufacturerID, \
			Manufacturers.Name AS Name, \
			TmpTable.Count AS Count \
			FROM Manufacturers \
			LEFT JOIN TmpTable ON TmpTable.ManufacturerID=Manufacturers.ManufacturerID;"
	g.DBCursor.execute(Query)
	g.Manufacturers = g.DBCursor.fetchall()
	g.ManufacturerNames = {}
	for Manufacturer in g.Manufacturers:
		g.ManufacturerNames[Manufacturer["ManufacturerID"]]=Manufacturer["Name"]
	print g.ManufacturerNames


@app.route("/")
def IndexPage():
	return render_template("index.html", Manufacturers=g.Manufacturers)


@app.route("/Manufacturer/<ManufacturerID>")
def Manufacturer(ManufacturerID):
	g.DBCursor.execute("SELECT * FROM Manufacturers WHERE ManufacturerID="+str(int(ManufacturerID))+";")
	Manufacturer = g.DBCursor.fetchone()
	g.DBCursor.execute("SELECT * FROM Filaments WHERE ManufacturerID="+str(int(ManufacturerID))+";")

	Query = "CREATE TEMPORARY TABLE IF NOT EXISTS ProfileCounts AS (\
			SELECT \
			FilamentProfiles.FilamentID AS FilamentID, \
			COUNT(FilamentProfiles.FilamentID) AS ProfileCount \
			FROM FilamentProfiles \
			GROUP BY FilamentProfiles.FilamentID \
			);"
	g.DBCursor.execute(Query)
	print Query
	Query = "SELECT \
			Filaments.FilamentID as FilamentID, \
			Filaments.ManufacturerID as FilamentID, \
			Filaments.MPN as MPN, \
			Filaments.Name as Name, \
			Filaments.Diameter as Diameter, \
			Filaments.Tolerance as Tolerance, \
			Filaments.Volume as Volume, \
			Filaments.Color as Color, \
			Filaments.MixCode as MixCode, \
			Filaments.HumanString as HumanString, \
			Filaments.DateAdded as DateAdded, \
			Filaments.DateModified as DateModified, \
			ProfileCounts.ProfileCount AS ProfileCount \
			FROM Filaments \
			JOIN ProfileCounts ON Filaments.FilamentID=ProfileCounts.FilamentID;"
	print Query				
	g.DBCursor.execute(Query)
	Filaments = g.DBCursor.fetchall()
	return render_template("Manufacturer.html", Manufacturer=Manufacturer, Filaments=Filaments)

@app.route("/Manufacturer/Register/")
def ManufacturerRegistration():
	return render_template("ManufacturerRegistration.html", Errors ={"Name": 0, "Email": 0, "Password": 0})


@app.route("/Manufacturer/Register/", methods=["POST"])
def ConfirmManufacturerRegistration():
	Errors ={"Name": 0, "Email": 0, "Password": 0}
	Failure = False
	g.DBCursor.execute("SELECT Email FROM Manufacturers WHERE Email='"+request.form["Email"]+"';")
	if g.DBCursor.fetchone()!=None:
		Errors["Email"] = " already registered"
		Failure = True
	if request.form["Password"]!=request.form["Password2"]:
		Errors["Password"] = "s don't match"
		Failure = True
	if len(request.form["Name"])<3:
		Errors["Name"] = " - too short"
		Failure = True
	if len(request.form["Password"])<6:
		Errors["Password"] = " - too short"
		Failure = True

	if Failure:
		return render_template("ManufacturerRegistration.html", Errors=Errors)

	Query = "INSERT INTO Manufacturers (Name, Email, Password) VALUES(\
		'"+request.form["Name"]+"',\
		'"+request.form["Email"]+"',\
		'"+request.form["Password"]+"');"
	g.DBCursor.execute(Query)
	
	return render_template("ConfirmManufacturerRegistration.html")




@app.route("/Filament/<FilamentID>")
def FilamentPage(FilamentID):
	FilamentID = str(int(FilamentID))
	g.DBCursor.execute("SELECT * FROM Filaments WHERE FilamentID="+FilamentID+";")
	Filament = g.DBCursor.fetchone() 
	g.DBCursor.execute("SELECT * FROM FilamentProfiles WHERE FilamentID="+FilamentID+";")
	Profiles = g.DBCursor.fetchall()	
	return render_template('Filament.html', ManufacturerName=g.ManufacturerNames[Filament["ManufacturerID"]], Filament=Filament, Profiles=Profiles)

@app.route("/Filament/Add/")
def AddFilament():
	return render_template("AddFilament.html", Manufacturers=g.Manufacturers)

@app.route("/Filament/Add/", methods=["POST"])
def ConfirmAddFilament():
	Query = "INSERT INTO Filaments (ManufacturerID, MPN, Name, Diameter, Tolerance, Volume, Color, DateAdded, DateModified) VALUES(\
		'"+request.form["MID"]+"',\
		'"+request.form["MPN"]+"',\
		'"+request.form["Name"]+"',\
		'"+request.form["Diameter"]+"',\
		'"+request.form["Tolerance"]+"',\
		'"+request.form["Volume"]+"',\
		'"+request.form["Color"]+"',\
		NOW(), NOW());"
	g.DBCursor.execute(Query)

	g.DBCursor.execute("SELECT LAST_INSERT_ID() AS Last;")
	FilamentID = g.DBCursor.fetchone()["Last"]

	return render_template("ConfirmAddFilament.html", FilamentID=FilamentID)





@app.route("/OLD/Filament/<ProfileID>")
def OldFilamentPage(ProfileID):
	ProfileID = str(int(ProfileID))
	g.DBCursor.execute("SELECT * FROM filament_profiles WHERE profile_id="+ProfileID+";")
	Filament = g.DBCursor.fetchone()
	return render_template('filament.html', Filament=Filament)



@app.route("/Search/", methods=["POST"])
def Search():

	if request.form["ManufacturerID"]!=0:
		Conditions += "ManufacturerID="+str(int(request.form["ManufacturerID"]))+" AND "
	if request.form["FilamentID"]!=0:
		Conditions += "FilamentID="+str(int(request.form["FilamentID"]))+" AND "
	if request.form["Name"]!="":
		Conditions += "Name LIKE(%"+str(int(request.form["ManufacturerID"]))+"%) AND "

	Conditions = Conditions[:-4]


	g.DB.Cursor("SELECT FilamentID FROM FilamentTable WHERE "+Conditions+";")

	Matches = g.DB.Cursor.fetchall()

	Results = []
	ResultsDicts = []

	for Match in Matches:
		Results.apend(Filament(Match["FilamentID"]))
		ResultsDicts.append(Results[-1].GetDict())
		
	return render_template("SearchResults.html", Filaments=ResultsDict)



if __name__=="__main__":
	app.debug=True
	app.run()



