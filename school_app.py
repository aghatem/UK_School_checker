

import streamlit as st
from streamlit_folium import folium_static
import folium
import requests
from math import sin, cos, sqrt, atan2, radians
import math
import pandas as pd
import chardet

# Streamlit documentation https://docs.streamlit.io/library/api-reference/widgets
def GUI():
	st.title('UK Schools checker App')
# get user Post code
	st.sidebar.subheader("User Post Code")
	user_post = st.sidebar.text_input("Please enter your post code: ", "WC1B3DG")
	button_was_clicked = st.sidebar.button("SUBMIT")
	user_crd = Post_Code_to_Coordinates(user_post)
	user_dist = user_post[0:3]
	st.write('Your coordinates are : ', user_crd[0], " & ",  user_crd[1])
	st.write('Your district is in : ', user_dist )
	#Choose mean of transport
	transport = ( "Car", "Public Transport", "Walking", "Bike")
	selected_Transport = st.sidebar.selectbox('Enter the mean of transport', transport)
	schools = ("sch1","sch2")
	return user_post, user_dist ,user_crd
	
# get user coordinates
def Post_Code_to_Coordinates(pcode):

   
    coord_API = "http://api.getthedata.com/postcode/"
    c_r = requests.get(coord_API+pcode)
    #print(c_r.json())
    #lat = c_r.json()["data"][0]["latitude"]
    coord = c_r.json()["data"]
    lat = coord['latitude']
    long = coord['longitude']
    crd =lat+"_"+long
    return lat, long

def mapit(lat,long):

	# center the map on British Muserum WC1B3DG
	global m
	m = folium.Map(location=[lat , long], tiles="OpenStreetMap",zoom_start=16)
	# add marker to user home
	tooltip = "Liberty Bell" 
	#folium.Marker([lat, long], popup="Liberty Bell", tooltip=tooltip).add_to(m)
	folium.Marker([lat, long], popup="Liberty Bell", tooltip=tooltip).add_to(m)
	folium.Marker([51.373039, -0.204720], popup="Liberty Bell", tooltip=tooltip).add_to(m)
	folium_static(m)

def Travel_GAPI(Lat1,Long1,Lat2,Long2,Transport_mode):
	
	# Google Distance API Documentation https://developers.google.com/maps/documentation/distance-matrix/overview?hl=en_US#transit_mode
	source = Lat1 & Long1
	Dest = Lat2 & Long2
	API_key= open("keyfile.txt", "r").read()
	if tranport_mode == 'car':

		url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key="&API_key&driving
	if tranport_mode == 'Public Transport':

		url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key="&API_key&transit
	if tranport_mode == 'Walking':

		url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key="&API_key&walking
	if tranport_mode == 'Bike':

		url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key="&API_key&bicycling

	payload={}
	headers = {}

	response = requests.request("GET", url, headers=headers, data=payload)

	return (response.text)

def get_distance (lat1,lon1,lat2,lon2):

    R = 6373.0

    lati1 = radians(lat1)
    long1 = radians(lon1)
    lati2 = radians(lat2)
    long2 = radians(lon2)

    dlon = long2 - long1
    dlat = lati2 - lati1

    a = sin(dlat / 2) ** 2 + cos(lati1) * cos(lati2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = round(R * c*1000,2)
    return distance

def nearby_schools(po,user_crd):


	schools = pd.read_csv('schools_db.csv', engine='python', encoding='ISO-8859-1')
	# Insert a new column in the df located in 1st column with name Distrocs and data to be added	
	schools.insert(0, "District", True)
	# fill new column with the first 3 characters of the postcode
	schools['District'] = schools['Postcode'].astype(str).str[:3]
	# create a new df filtering only on schools in the district matching the first 3 chars of the postcode
	df = schools[schools['District'] == po[0:3]]
	# create a new df focusing on interesting columns 
	selected_schools = df[[ 'EstablishmentName', 'OfstedRating (name)', 'LA (name)', 'SchoolCapacity', 'Postcode', 'Locality', 'NumberOfPupils', 'NumberOfBoys',
	 'NumberOfGirls', 'DistrictAdministrative (name)', 'Gender (name)', 'AdministrativeWard (name)', 'PhaseOfEducation (name)', 'ReligiousCharacter (name)',
	  'StatutoryLowAge', 'StatutoryHighAge', 'TypeOfEstablishment (name)', 'OfstedLastInsp', 'Street', 'Address3', 'Town', 'County (name)', 'SchoolWebsite',
	   'TelephoneNum', 'EstablishmentStatus (name)',  'UKPRN', 'HeadFirstName', 'HeadLastName']]
	# Adding coordinates to each school
	selected_schools.insert(23, "lat", True)
	selected_schools.insert(24, "long", True)
	# Adding distance
	selected_schools.insert(25, "Distance", True)
	#st.write(selected_schools.head(20))
	for i in range (0,len(selected_schools)):
		selected_schools.iloc[i,23] = Post_Code_to_Coordinates(selected_schools.iloc[i,4])[0]
		selected_schools.iloc[i,24] = Post_Code_to_Coordinates(selected_schools.iloc[i,4])[1]
		selected_schools.iloc[i,25] = get_distance(float(selected_schools.iloc[i,23]),float(selected_schools.iloc[i,24]),float(user_crd[0]),float(user_crd[1]))
		

	
	global m
	m = folium.Map(location=[user_crd[0] , user_crd[1]], tiles="OpenStreetMap",zoom_start=14)
	tooltip = "" 
	folium.Marker([user_crd[0] , user_crd[1]],color='black' ,popup="Your Home",icon=folium.Icon(color='green', icon_color='white', icon='tint')).add_to(m)
	for i in range (0,len(selected_schools)):
		
		folium.Marker([float(selected_schools.iloc[i,23]),float(selected_schools.iloc[i,24])], popup=selected_schools.iloc[i,0]).add_to(m)
	
	st.write(selected_schools.head(20))
	

	st.write("Nearest School Name is far ", selected_schools['Distance'].min(), " meters from your home")
	st.write('Number of schools in youd district is :', len(selected_schools))
	st.write(selected_schools.value_counts('OfstedRating (name)'))
	#schools = selected_schools['EstablishmentName'].tolist()
	#st.write('Selected School:', option)
	newdf = selected_schools.loc[(selected_schools.EstablishmentName == option)]
	Travel_GAPI(user_crd[0] , user_crd[1],newdf[0,23],newdf[0,24],selected_Transport)

def main ():
	
	x = GUI()
	user_dist = x[1]
	user_post = x[0]
	user_crd = x[2]
	#mapit(user_crd[0], user_crd[1])
	
	nearby_schools(user_post,user_crd)
	

main()
