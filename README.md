# UK_School_checker
Check nearest schools in UK using home's postcodes and provides OFSTED ranking, school type, distance from home &amp; transport duration with Google Geo-map APIs
This web app helps UK residents to assess schools in their neighberhood & select the suitable school based on multiple criteria

The app takes from user the home postcode and plots on a map the home location and all surrounding schoools in the neighborhood

1. The app uses an API to conver the post code to coordinates  (http://api.getthedata.com/postcode/)
Criterias to evaluate a school can be:

2. School distance, the app calculate the radial distance and the exact route
Also the app uses Google Maps API to calculate the route and provide an estimate to reach the school based on the traffic considering different tranpsort modes the user can choose (walking, cycling, driving or public transport)
(https://maps.googleapis.com/maps/api/distancematrix/)

3. There is a big list of criterias to assess different schools likw 'District', 'LA (name)', 'EstablishmentName', 'OfstedRating (name)', 'SchoolCapacity', 'Postcode', 'Locality', 'NumberOfPupils', 'NumberOfBoys', 'NumberOfGirls', 'DistrictAdministrative (name)', 'Gender (name)', 'AdministrativeWard (name)', 'PhaseOfEducation (name)', 'ReligiousCharacter (name)', 'StatutoryLowAge', 'StatutoryHighAge', 'TypeOfEstablishment (name)', 'OfstedLastInsp', 'Street', 'Address3', 'Town', 'County (name)', 'SchoolWebsite', 'TelephoneNum', 'EstablishmentStatus (name)', 'NurseryProvision (name)', 'UKPRN', 'HeadFirstName', HeadLastName'				


The deployed web app is live at https://dp-penguins.herokuapp.com/


The web app was built in Python using the following libraries:
- streamlit
- requests
- streamlit_folium
- folium
- pandas
- chardet

