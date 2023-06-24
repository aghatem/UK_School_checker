import streamlit as st
from streamlit_folium import folium_static
import folium
import requests
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
import matplotlib.pyplot as plt
import plotly.express as px
import fastparquet

# Streamlit documentation https://docs.streamlit.io/library/api-reference/widgets


def input():
    st.title('UK Schools checker App')
    st.write('Check nearest schools in UK using home postcodes and provides OFSTED ranking, school type, distance from home & transport duration with Google Geo-map APIs This web app helps UK residents to assess schools in their neighberhood & select the suitable school based on multiple criteria.')
# get user Post code
    st.sidebar.subheader("User Post Code")
    user_post = st.sidebar.text_input("Please enter your post code: 🔎", "WC1B3DG").upper()
    button_was_clicked = st.sidebar.button("SUBMIT")
    user_crd = Post_Code_to_Coordinates(user_post)
    user_dist = user_post[0:3]
    st.write('Your coordinates are : ', user_crd[0], " & ",  user_crd[1])
    
    # search area
    
    radio_but = st.radio(label = '', options = ['Your Borough','Entire District'])
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        
    if (radio_but == 'Your Borough'):
        focus = 3
    elif (radio_but == 'Entire District'):
        focus = 2
    
    return user_post, user_dist ,user_crd, focus
    
# get user coordinates
def Post_Code_to_Coordinates(pcode):
    try:
        coord_API = "http://api.getthedata.com/postcode/"
        c_r = requests.get(coord_API+pcode)
        #print(c_r.json())
        #lat = c_r.json()["data"][0]["latitude"]
        coord = c_r.json()["data"]
        lat = coord['latitude']
        long = coord['longitude']
        crd =lat+"_"+long
        return lat, long
    except TypeError:
        st.error(f"An error occurred")
        return None

@st.cache(suppress_st_warning=True)
def mapit(lat,long):
    # center the map on British Muserum WC1B3DG
    global m
    m = folium.Map(location=[lat , long], tiles="OpenStreetMap",zoom_start=16)
    # add marker to user home
    tooltip = "Liberty Bell" 
    folium.Marker([lat, long], popup="Liberty Bell", tooltip=tooltip).add_to(m)
    folium_static(m)

def Travel_GAPI(Lat1,Long1,Lat2,Long2,tranport_mode):
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

def create_pie_chart(ds_db,schools,rank, rating_n, user_post):
    #read disrtict db and get district name
    district = ds_db.loc[ds_db['po_code'] == user_post[:3], 'District'].values.item()


    with st.container():
        # Prepare district rank and num of outstanding schoolsfor plotting
        District_info = rank.loc[rank['LA (name)'] == district].values.tolist()
        st.write('Your district' , str(district) ,'rank is ', District_info[0][1], 'in UK, as out of the ', District_info[0][3],' schools in ',str(district) ,' there is ', District_info[0][2],'outstanding schools.')


        District_stats = rating_n.loc[rating_n['District'] == district]
        st.write(District_stats)
        values = District_stats[['Outstanding',	'Good','Special Measures','Requires improvement','Serious Weaknesses','Inadequate']].values.flatten()
        labels = ['Outstanding',	'Good','Special Measures','Requires improvement','Serious Weaknesses','Inadequate']


        # Reshape the DataFrame for Plotly Express
        filtered_df = pd.melt(District_stats, id_vars=['District'], value_vars=['Outstanding',	'Good','Special Measures','Requires improvement','Serious Weaknesses','Inadequate'], var_name='Variable', value_name='Value')

        # Plot a pie chart with Plotly Express
        fig = px.pie(filtered_df, names='Variable', values='Value', title=f'Schools rating in: {district}')
        st.plotly_chart(fig)

        # Prepare districts data for bar chart plotting
        grouped_df = schools.groupby(['LA (name)', 'OfstedRating (name)']).size().reset_index(name='Count')
        grouped_df2 = grouped_df.pivot_table(index='LA (name)', columns='OfstedRating (name)', values='Count', fill_value=0)
        grouped_df2 = grouped_df2.rename_axis('LA (name)')
        grouped_df2.insert(0, "District", True)
        grouped_df2['District'] = grouped_df2.index
        order = ['District','Outstanding',	'Good','Special Measures','Requires improvement','Serious Weaknesses','Inadequate']
        grouped_df2 = grouped_df2[order] 
        sorted_df2 = grouped_df2.sort_values(by='Outstanding', ascending=False) 
        new_df = sorted_df2[['District', 'Outstanding']].copy()

    with st.container():
        st.write("Select another disrtict and see the performance of its schools ")
        new_rating= rating_n.sort_values(by='District')
        dist_names = new_rating['District'].values.tolist()
        default_dist = str(district)
        fitltered =  st.selectbox('Select a district:' , dist_names, index=dist_names.index(default_dist))
        selected_dis = schools[(schools['LA (name)']== fitltered)]

        tab1 , tab2 = st.tabs([ "Charts","Data"])

        with tab2:
            st.subheader("Schools statistics data")
            input1_col, disp1_col = st.columns(2) 
            with input1_col:
                #Phase of education  data
                value_counts5 = selected_dis['PhaseOfEducation (name)'].value_counts()
                phase_data = pd.DataFrame({'phase': value_counts5.index, 'count': value_counts5.values})
                st.write(phase_data)
                #gender data
                value_counts3 = selected_dis['Gender (name)'].value_counts()
                gender_data = pd.DataFrame({'gender_type': value_counts3.index, 'count': value_counts3.values})
                st.write(gender_data)

            with disp1_col:
                #Pschool rank
                value_counts = selected_dis['OfstedRating (name)'].value_counts()
                rating_data = pd.DataFrame({'rating': value_counts.index, 'count': value_counts.values})
                st.write(rating_data)

                #type of establishment data
                value_counts4 = selected_dis['TypeOfEstablishment (name)'].value_counts()
                establishment_data = pd.DataFrame({'establishment_type': value_counts4.index, 'count': value_counts4.values})
                st.write(establishment_data)

        with tab1:
            st.header("Schools statistics charts")
            input3_col, disp3_col = st.columns(2) 
            with input3_col:

                # phase chart
                phase_fig = px.pie(phase_data, values='count', names='phase', height=400, width=400, title=f'Schools phases in: {fitltered}')
                phase_fig.update_layout(legend=dict(orientation="h",yanchor="bottom", y=-0.4, x=0.2 ))
                st.plotly_chart(phase_fig)

                # rating chart
                rating_fig = px.pie(rating_data, values='count', names='rating', height=400, width=400, title=f'Schools rating in: {fitltered}')
                rating_fig.update_layout(legend=dict(orientation="h",yanchor="bottom", y=-0.4, x=0.2 ))
                st.plotly_chart(rating_fig)

            

            with disp3_col:

                # gender chart
                gender_fig = px.pie(gender_data, values='count', names='gender_type', height=350, width=350)
                gender_fig.update_layout(legend=dict(orientation="h",yanchor="bottom", y=-0.4, x=0.2 ), title=f'Schools gender in: {fitltered}')
                st.plotly_chart(gender_fig)
                
                # establishment type chart
                est_fig = px.pie(establishment_data, values='count', names='establishment_type' , title=f'Schools establishment type in: {fitltered}')
                est_fig.update_layout(showlegend=False,height=400, width=400)

                
                st.plotly_chart(est_fig)

                        
    with st.container():
        st.write("Below is a bar chart sorted by top UK districts with high number of Outstanded rated schools.")
        top_n  = st.text_input('How many of the top UK districts would you like to see?', 40)
        top_n = int(top_n)
        input_col, disp_col = st.columns(2)
        new_df=new_df.head(top_n)
        with input_col:
            plt.style.use('ggplot')
            new_df.plot(kind='barh',figsize=(5,10),title='Top ranked districts')
            #plt.plot(x, y)
            plt.ylabel('UK districts')
            plt.xlabel('# of Outstanding schools in district')
            st.pyplot(plt)

        with disp_col:

            new_df = new_df.reset_index(drop=True)
            # Create a Styler object from the DataFrame
            styler = new_df.style
            # Apply the 'text-align: center' CSS style to all cells
            styler = styler.set_properties(**{'text-align': 'center'})
            st.write(styler, unsafe_allow_html=True)







def nearby_schools(schools,user_post,user_crd,f,ds_db,rank, rating_n):


    
    # Insert a new column in the df located in 1st column with name District and data to be added   
    schools.insert(0, "District", True)
    # fill new column with the first 3 characters of the postcode
    schools['District'] = schools['Postcode'].astype(str).str[:f]
    
    # create a new df filtering only on schools in the district matching the first 3 chars of the postcode
    df = schools[schools['District'] == user_post[0:f]]
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
    st.write('You can find more details about ' ,nearest_school.iloc[0,0], 'by visiting its website below',selected_schools.loc[selected_schools['EstablishmentName'] == nearest_school.iloc[0,0], 'SchoolWebsite'])
    
    
    


    # Display rating chart
    st.subheader('Schools Statistics  ')
    st.write('These chart display the Ofsted ratings, type, phase of education and gender for the school in the search area you selected')
    create_pie_chart(ds_db,schools,rank, rating_n, user_post)

    
    st.title('Search for Schools:')
    st.write('Use the filter options in the left sidebar to taoilor your school search and check the resulting schools in below table. You can also press below Filter Map to plot the filtered schools inthe map.')
    pivot = pd.crosstab(index=[selected_schools['Town'],selected_schools['PhaseOfEducation (name)']], columns=[selected_schools['OfstedRating (name)']],  margins=True)
    with st.expander("Click to select see the performance of schools in the filtered area: "):
        st.write(pivot)
    
    with st.container():
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

        st.subheader("Filtered schools: " )
        
        st.write('You have filtered on schools which are far',dist_home, ' meters from your postcode, and in the ', phase_choice,'phase of education', ' and have been ranted by OFSTED to be ',ofsted_choice,' and you prefer to arrive school by ',selected_Transport,'.') 
        st.write(  " The number of schools which match your filter criteria is : ", len(df_selection) )

        st.write(df_selection.astype(str))

        st.subheader('Search Map')
        radio_but2 = st.radio(label = '', options = ['Remove Filter Map', 'Filter Map'])
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
    
        
        school_names = df_selection['EstablishmentName'].values.tolist()
        filtered_schools =  st.selectbox('You can find in below table a detailed list of the filtered schools :' , school_names)
        st.write(df_selection.loc[df_selection['EstablishmentName'] == filtered_schools].transpose().astype(str))
    

def main ():
    #load schools database
    schools = pd.read_parquet('schools.parquet')

    #load districts database
    ds_db = pd.read_csv('po_to_district.csv', engine='python', encoding='ISO-8859-1')
    #load districts rating
    rating = pd.read_csv('districts_rating.csv', engine='python', encoding='ISO-8859-1')
    rating_n = rating.fillna(0)
    rating_convert= rating_n.columns[1:]
    rating_n[rating_convert] = rating_n[rating_convert].astype(int)
    # load districts rank
    rank = pd.read_csv('district_rank.csv', engine='python', encoding='ISO-8859-1')

    x = input()
    user_dist = x[1]
    user_post = x[0]
    user_crd = x[2]
    focus = x[3]
    nearby_schools(schools, user_post,user_crd,focus,ds_db,rank, rating_n)



if __name__ == '__main__':
    main()
