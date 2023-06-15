import streamlit as st
from streamlit_folium import folium_static
import folium
import requests
from math import sin, cos, sqrt, atan2, radians
import math
import pandas as pd
import chardet


# Streamlit documentation https://docs.streamlit.io/library/api-reference/widgets
def input():
    st.title('UK Schools checker App')
# get user Post code
    st.sidebar.subheader("User Post Code")
    user_post = st.sidebar.text_input("Please enter your post code: 🔎", "WC1B3DG")
    button_was_clicked = st.sidebar.button("SUBMIT")
    user_crd = Post_Code_to_Coordinates(user_post)
    user_dist = user_post[0:3]
    st.write('Your coordinates are : ', user_crd[0], " & ",  user_crd[1])
    
    # search area
    
    radio_but = st.radio(label = 'Search Area', options = ['Your Borough','Entire District'])
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        
    if (radio_but == 'Your Borough'):
        focus = 3
    elif (radio_but == 'Entire District'):
        focus = 2
    
    return user_post, user_dist ,user_crd, focus
    
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
    folium.Marker([lat, long], popup="Liberty Bell", tooltip=tooltip).add_to(m)
    folium_static(m)

def Travel_GAPI(Lat1,Long1,Lat2,Long2,Transport_mode):
    # Google Distance API Documentation https://developers.google.com/maps/documentation/distance-matrix/overview?hl=en_US#transit_mode
    # https://developers.google.com/maps/documentation/distance-matrix/overview#distance-matrix-responses
    source = Lat1 & Long1
    Dest = Lat2 & Long2
    API_key= open("keyfile.txt", "r").read()
    if tranport_mode == 'car':

        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" & Lat1 & "%2C" & Long1 & "&destinations=" & Lat2 & "%2C" & Long2 & "&mode=driving" & " &key=" & API_key 
    if tranport_mode == 'Public Transport':

        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" & Lat1 & "%2C" & Long1 & "&destinations=" & Lat2 & "%2C" & Long2 & "&mode=transit" & "&key=" & API_key 
    if tranport_mode == 'Walking':

        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" & Lat1 & "%2C" & Long1 & "&destinations=" & Lat2 & "%2C" & Long2 & "walking" & API_key
    if tranport_mode == 'Bike':

        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" & Lat1 & "%2C" & Long1 & "&destinations=" & Lat2 & "%2C" & Long2 & "bicycling" & API_key 

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


#@st.cache
def nearby_schools(po,user_crd,f):


    schools = pd.read_csv('schools_db.csv', engine='python', encoding='ISO-8859-1')
    # Insert a new column in the df located in 1st column with name Distrocs and data to be added   
    schools.insert(0, "District", True)
    # fill new column with the first 3 characters of the postcode
    schools['District'] = schools['Postcode'].astype(str).str[:f]
    # create a new df filtering only on schools in the district matching the first 3 chars of the postcode
    df = schools[schools['District'] == po[0:f]]
    # create a new df focusing on interesting columns 
    selected_schools = df[[ 'EstablishmentName', 'OfstedRating (name)', 'LA (name)', 'SchoolWebsite', 'Postcode', 'Locality', 'NumberOfPupils', 'NumberOfBoys',
     'NumberOfGirls', 'DistrictAdministrative (name)', 'Gender (name)', 'AdministrativeWard (name)', 'PhaseOfEducation (name)', 'ReligiousCharacter (name)',
      'StatutoryLowAge', 'StatutoryHighAge', 'TypeOfEstablishment (name)', 'OfstedLastInsp', 'Street', 'Address3', 'Town', 'County (name)', 'SchoolCapacity',
       'TelephoneNum', 'EstablishmentStatus (name)',  'UKPRN', 'HeadFirstName', 'HeadLastName']]
    # Replace NAN cells 
    selected_schools.fillna('', inplace=True)
    # Convert to strings
    selected_schools.astype(str)
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
        
        folium.Marker([float(selected_schools.iloc[i,23]),float(selected_schools.iloc[i,24])], popup = [selected_schools.iloc[i,0],  selected_schools.iloc[i,1], selected_schools.iloc[i,22] ]).add_to(m)
    folium_static(m)
    
    min_dist =selected_schools['Distance'].min()
    nearest_school = selected_schools.loc[(selected_schools['Distance']==min_dist)]
    st.write("Nearest School Name is",nearest_school.iloc[0,0], " which is far ", min_dist , " meters from your home")
    st.write('Number of schools in your district is :', len(selected_schools))
    st.markdown('Summary:')
    pivot = pd.crosstab(index=[selected_schools['Town'],selected_schools['PhaseOfEducation (name)']], columns=[selected_schools['OfstedRating (name)']],  margins=True)
    st.write(pivot)
    

    # get schools matching filter criteria, to make all parameters in same form replace st with myform
    myform= st.sidebar.form("Form2")
        # filter on distance from home
    dist_home = myform.slider('Distance from home in meters:', min_value=20, max_value=4000, step=50, value=1000, key=1)
    #choose phase of education
    phase= ("Any","Nursery", "Primary", "Secondary", "16 plus","All-through" )
    phase_choice = myform.selectbox('Phase of educaton:', phase)
    #choose ofsted rating
    ofsted= ("Any","Good", "Outstanding","Special Measures")
    ofsted_choice =  myform.selectbox('School OFsted Rating:', ofsted)
    #Choose mean of transport
    transport = ( "Car", "Public Transport", "Walking", "Bike" )
    selected_Transport = myform.selectbox('Enter the mean of transport', transport)
    #Filter = st.sidebar.button("Filter")
    submitted =  myform.form_submit_button(label = "Filter")
    df_selection = selected_schools
    if submitted:
        if ofsted_choice == 'Any' and phase_choice == 'Any':
            df_selection = selected_schools.loc[(selected_schools['Distance'] <= dist_home)]
        elif phase_choice == 'Any':
            df_selection = selected_schools.loc[(selected_schools['Distance'] <= dist_home)  & (selected_schools['OfstedRating (name)'] == ofsted_choice)]
        elif ofsted_choice == 'Any':
            df_selection = selected_schools.loc[(selected_schools['Distance'] <= dist_home) & (selected_schools['PhaseOfEducation (name)'] == phase_choice)]

        else:
            df_selection = selected_schools.loc[(selected_schools['Distance'] <= dist_home) & (selected_schools['PhaseOfEducation (name)'] == phase_choice) & (selected_schools['OfstedRating (name)'] == ofsted_choice)]

        
    
    #Travel_GAPI(user_crd[0] , user_crd[1],newdf[0,23],newdf[0,24],selected_Transport)
    df_selection = df_selection.style.dataframe(hideindex=True)
    st.write("Filtered schools: " , (len(df_selection)))
    st.write(df_selection.astype(str))

    radio_but2 = st.radio(label = 'Search Area', options = ['Remove Filter Map', 'Filter Map'])
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        
    if (radio_but2 == 'Filter Map'):
        m2 = folium.Map(location=[user_crd[0] , user_crd[1]], tiles="OpenStreetMap",zoom_start=16)
        tooltip = "Liberty Bell" 
        folium.Marker([user_crd[0], user_crd[1]], color='black' ,popup="Your Home",icon=folium.Icon(color='green', icon_color='white', icon='tint')).add_to(m2)
        for i in range (0,len(df_selection)):
        
            folium.Marker([float(df_selection.iloc[i,23]),float(df_selection.iloc[i,24])], popup = [df_selection.iloc[i,0],  df_selection.iloc[i,1], df_selection.iloc[i,22] ]).add_to(m2)
        folium_static(m2)
    elif (radio_but2 == 'Remove Filter Map'):
        filter_map = 2
    
    st.write(  " No. of filtered schools : ",len(df_selection) )
    school_names = df_selection['EstablishmentName'].values.tolist()
    filtered_schools =  st.selectbox('Filtered schools :' , school_names)
    st.write(df_selection.loc[df_selection['EstablishmentName'] == filtered_schools].transpose().astype(str))
def main ():
    
    x = input()
    user_dist = x[1]
    user_post = x[0]
    user_crd = x[2]
    focus = x[3]
    nearby_schools(user_post,user_crd,focus)
    


main()
