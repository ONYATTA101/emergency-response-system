import folium
import requests
import geocoder
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

def get_user_location():
    # Get user's current location using IP
    g = geocoder.ip('me')
    return g.latlng




def find_nearby_hospitals(lat, lon, radius=5000):
    # Using Overpass API to find hospitals
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
    );
    out body;
    """
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()
    
    hospitals = []
    for element in data['elements']:
        if 'tags' in element:
            name = element['tags'].get('name', 'Unknown Hospital')
            hospital_lat = element['lat']
            hospital_lon = element['lon']
            distance = geodesic((lat, lon), (hospital_lat, hospital_lon)).kilometers
            hospitals.append({
                'name': name,
                'distance': round(distance, 2),
                'coordinates': (hospital_lat, hospital_lon)
            })
    
    return sorted(hospitals, key=lambda x: x['distance'])

def create_map(user_location, hospitals):
    # Create a map centered on user's location
    m = folium.Map(location=user_location, zoom_start=13)
    
    # Add user marker
    folium.Marker(
        user_location,
        popup='Your Location',
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    







    # Add hospital markers
    for hospital in hospitals:
        folium.Marker(
            hospital['coordinates'],
            popup=f"{hospital['name']} ({hospital['distance']} km)",
            icon=folium.Icon(color='green', icon='plus')
        ).add_to(m)
    
    # Save map
    m.save('emergency_map.html')

def main():
    print("Emergency Response System")
    print("------------------------")
    
    # Get user's location
    user_location = get_user_location()
    if not user_location:
        print("Error: Could not determine your location")
        return
    
    print(f"Your location: {user_location}")
    
    # Find nearby hospitals
    hospitals = find_nearby_hospitals(user_location[0], user_location[1])
    
    if not hospitals:
        print("No hospitals found in your area")
        return
    
    # Display nearest hospitals
    print("\nNearest Hospitals:")
    for i, hospital in enumerate(hospitals[:5], 1):
        print(f"{i}. {hospital['name']} - {hospital['distance']} km")
    
    # Create and save map
    create_map(user_location, hospitals[:5])
    print("\nMap has been created as 'emergency_map.html'")

if __name__ == "__main__":
    main()
    