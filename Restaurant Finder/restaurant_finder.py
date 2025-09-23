import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient, GEOSPHERE
from pymongo.errors import OperationFailure


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "geo"  
COLLECTION_NAME = "restaurant" 

# Function to connect to MongoDB and fetch data
def get_data_from_mongo(center_coords, radius_km):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Ensure a 2dsphere index exists on the 'location' field
        # The create_index method is idempotent, so it won't create a new one if it already exists.
        try:
            # Explicitly create the 2dsphere index on the 'location' field of the 'restaurants' collection
            db.restaurant.create_index([("location", GEOSPHERE)])
            #st.success("2dsphere index on 'location' field is ready.")
        except OperationFailure as e:
            st.warning(f"Could not create 2dsphere index: {e}")

        # The radius in the $centerSphere query is in radians.
        # To convert kilometers to radians, divide by the Earth's radius in kilometers (approx. 6378.1 km).
        #  3963.2 for miles 
        # .
        earth_radius_miles = 3963.2
        radius_radians = radius_km / earth_radius_miles

        query = {
            "location": {
                "$geoWithin": {
                    "$centerSphere": [center_coords, radius_radians]
                }
            }
        }

        data = list(collection.find(query))
        client.close()
        return data

    except Exception as e:
        st.error(f"Error connecting to MongoDB or fetching data: {e}")
        return None

# Streamlit UI
st.title("Restaurant Finder")
st.write("Find restaurants nearby.")

# User inputs
st.header("Search Parameters")
lon = st.number_input("Longitude", value=-73.93414657, format="%.8f")
lat = st.number_input("Latitude", value=40.82302903, format="%.8f")
radius = st.number_input("Radius (in miles)", value=5.0)

# Fetch and display data
if st.button("Search"):
    with st.spinner('Searching for restaurants...'):
        data = get_data_from_mongo([lon, lat], radius)
        
        if data and len(data) > 0:
            # Convert data to a pandas DataFrame
            df = pd.DataFrame(data)

            # Extract location coordinates from the 'location' field
            df['lat'] = df['location'].apply(lambda x: x['coordinates'][1])
            df['lon'] = df['location'].apply(lambda x: x['coordinates'][0])

            # Display the map
            st.header(f"Found {len(df)} restaurants within {radius} miles.")
            st.map(df[['lat', 'lon']].rename(columns={'lat': 'latitude', 'lon': 'longitude'}))

        else:
            st.warning(f"No restaurants found within {radius} miles of the specified coordinates.")
