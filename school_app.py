
import streamlit as st
def GUI():
	st.title('UK Schools checker App')
# get user Post code
	st.sidebar.subheader("User Post Code")
	user_post = st.sidebar.text_input("Please enter your post code: ", "WC1B3DG")
	button_was_clicked = st.sidebar.button("SUBMIT")
	user_crd = Post_Code_to_Coordinates(user_post)
	user_dist = user_post[0:3]
	st.write('Your coordinates are : ', user_crd[0], " & ",  user_crd[1])
	st.write('Your District is  : ', user_dist )
	#Choose mean of transport
	transport = ( "Car", "Public Transport", "Walking", "Bike")
	selected_Transport = st.sidebar.selectbox('Enter the mean of transport', transport)
	return(user_post,user_dist,user_crd)
	
# get user coordinates
def Post_Code_to_Coordinates(pcode):

    import requests
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
	import streamlit as st
	from streamlit_folium import folium_static
	import folium
	# center the map on British Muserum WC1B3DG
	global m
	m = folium.Map(location=[lat , long], tiles="OpenStreetMap",zoom_start=16)
	# add marker to user home
	tooltip = "Liberty Bell" 
	#folium.Marker([lat, long], popup="Liberty Bell", tooltip=tooltip).add_to(m)
	folium.Marker([lat, long], popup="Liberty Bell", tooltip=tooltip).add_to(m)
	folium.Marker([51.373039, -0.204720], popup="Liberty Bell", tooltip=tooltip).add_to(m)
	folium_static(m)


def get_distance (lat1,lon1,lat2,lon2):
    from math import sin, cos, sqrt, atan2, radians
    import math
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
	from streamlit_folium import folium_static
	import folium
	import pandas as pd
	import chardet

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
	   'TelephoneNum', 'EstablishmentStatus (name)', 'UKPRN', 'HeadFirstName', 'HeadLastName']]
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
		#folium.Marker(location=[float(selected_schools.iloc[i,23]),float(selected_schools.iloc[i,24])],popup=selected_schools.iloc[i,0]).add_to(m)
	
	
	
	import streamlit as st
	from streamlit_folium import folium_static
	import folium
	
	global m
	m = folium.Map(location=[user_crd[0] , user_crd[1]], tiles="OpenStreetMap",zoom_start=14)
	tooltip = "" 
	folium.Marker([user_crd[0] , user_crd[1]],color='black' ,popup="Your Home",icon=folium.Icon(color='green', icon_color='white', icon='tint')).add_to(m)
	for i in range (0,len(selected_schools)):
		folium.Marker([float(selected_schools.iloc[i,23]),float(selected_schools.iloc[i,24])], popup=selected_schools.iloc[i,0]).add_to(m)
	


	folium_static(m)

	st.write(selected_schools.head(20))
	
	#st.write(selected_schools['Distance'].idxmin())
	#st.write(selected_schools.loc[selected_schools['Distance'].idxmin()])
	st.write("Nearest School Name is far ", selected_schools['Distance'].min(), " meters from your home")
	#show schools statistics in this district
	st.write('Number of schools in youd district is :', len(selected_schools))
	st.write(selected_schools.value_counts('OfstedRating (name)'))

def main ():
	from streamlit_folium import folium_static
	
	x = GUI()
	user_dist = x[1]
	user_post = x[0]
	user_crd = x[2]
	#mapit(user_crd[0], user_crd[1])

	nearby_schools(user_post,user_crd)
	

main()
