#!/usr/bin/python

from flask import Flask, render_template, g, request
import MySQLdb
import MySQLdb.cursors
app = Flask(__name__)
import Filament
import logging
from unidecode import unidecode
from ufid import UFID
logging.basicConfig(filename='log.txt', level=logging.DEBUG)

@app.before_request
def before_request():
	DB = MySQLdb.connect('localhost', "UFID", "UFID", "UFID",cursorclass=MySQLdb.cursors.DictCursor);
	DB.autocommit(True)
	g.DBCursor = DB.cursor()
	g.DBEscaper = DB.escape_string

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
			LEFT JOIN TmpTable ON TmpTable.ManufacturerID=Manufacturers.ManufacturerID\
			ORDER BY Manufacturers.Name ASC;"
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
			LEFT JOIN ProfileCounts ON Filaments.FilamentID=ProfileCounts.FilamentID\
			WHERE Filaments.ManufacturerID = "+str(int(ManufacturerID))+";"
	print Query				
	g.DBCursor.execute(Query)
	Filaments = g.DBCursor.fetchall()
	return render_template("Manufacturer.html", Manufacturer=Manufacturer, Filaments=Filaments)

@app.route("/Manufacturer/Add/<Name>")
def ManufacturerAdd(Name):
	g.DBCursor.execute("INSERT INTO Manufacturers (Name) VALUES('"+g.DBEscaper(Name)+"');")
	return render_template("index.html", Manufacturers=g.Manufacturers)

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
		'"+g.DBEscaper(unidecode(request.form["Name"]))+"',\
		'"+g.DBEscaper(request.form["Email"])+"',\
		'"+g.DBEscaper(request.form["Password"])+"');"
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
	return render_template("AddFilament.html", Manufacturers=g.Manufacturers, ManufacturerID=0)

@app.route("/Filament/Add/<ManufacturerID>")
def AddFilamentForManufacturer(ManufacturerID):
	return render_template("AddFilament.html", Manufacturers=g.Manufacturers, ManufacturerID=int(ManufacturerID))

@app.route("/Filament/Add/<ManufacturerID>", methods=["POST"])
def ConfirmAddFilament(ManufacturerID):
	Query = "INSERT INTO Filaments (ManufacturerID, MPN, Name, Diameter, Tolerance, Volume, Color, DateAdded, DateModified) VALUES(\
		'"+str(int(request.form["MID"]))+"',\
		'"+g.DBEscaper(request.form["MPN"][:128])+"',\
		'"+g.DBEscaper(unidecode(request.form["Name"][:128]))+"',\
		'"+str(float(request.form["Diameter"]))+"',\
		'"+str(float(request.form["Tolerance"]))+"',\
		'"+str(float(request.form["Volume"]))+"',\
		'"+g.DBEscaper(request.form["Color"])+"',\
		NOW(), NOW());"
	g.DBCursor.execute(Query)

	g.DBCursor.execute("SELECT LAST_INSERT_ID() AS Last;")
	FilamentID = g.DBCursor.fetchone()["Last"]
	return FilamentPage(FilamentID)

@app.route("/Filament/Profile/<ProfileID>")
def ViewProfile(ProfileID):
	g.DBCursor.execute("SELECT FilamentProfiles.*, \
				Filaments.*\
				FROM FilamentProfiles\
				JOIN Filaments ON FilamentProfiles.FilamentID = Filaments.FilamentID\
				WHERE ProfileID="+str(int(ProfileID))+";")
	Profile = g.DBCursor.fetchone()
	print Profile
	UFIDObject = UFID(Diameter = Profile["Diameter"],
		Tolerance = Profile["Tolerance"],
		Tg = Profile["Tg"],
		TPrint = Profile["TPrint"],
		TMin = Profile["TMin"],
		TMax = Profile["TMax"],
		TChamber = Profile["TChamber"],
		TBed = Profile["TBed"],
		Color = Profile["Color"])
	return "<a href='"+UFIDObject.GetUFIDUrl()+"'>"+UFIDObject.GetUFIDUrl()+"</a>"


@app.route("/Filament/Profile/Add/<FilamentID>")
def AddProfile(FilamentID):
	FilamentID = str(int(FilamentID))
	g.DBCursor.execute("SELECT * FROM Filaments WHERE FilamentID="+FilamentID+";")
	Filament = g.DBCursor.fetchone() 
	g.DBCursor.execute("SELECT * FROM FilamentProfiles WHERE FilamentID="+FilamentID+";")
	Profiles = g.DBCursor.fetchall()	
	return render_template('AddProfile.html', ManufacturerName=g.ManufacturerNames[Filament["ManufacturerID"]], Filament=Filament, Profiles=Profiles)

@app.route("/Filament/Profile/Add/<FilamentID>", methods=["POST"])
def AddProfileDo(FilamentID):
	FilamentID = str(int(FilamentID))
	Query = "INSERT INTO FilamentProfiles (FilamentID, ProfileDescription, TPrint, TMax, TMin, Tg, TBed, TChamber, Contributor, DateAdded, DateModified) VALUES(\
		'"+FilamentID+"',\
		'"+g.DBEscaper(request.form["Description"])+"',\
		'"+str(float(request.form["TPrint"]))+"',\
		'"+str(float(request.form["TMax"]))+"',\
		'"+str(float(request.form["TMin"]))+"',\
		'"+str(float(request.form["Tg"]))+"',\
		'"+str(float(request.form["TBed"]))+"',\
		'"+str(float(request.form["TChamber"]))+"',\
		'Username',\
		NOW(), NOW());"
	g.DBCursor.execute(Query)
	return FilamentPage(FilamentID)


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



