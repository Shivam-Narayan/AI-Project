import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from map import shortest_route, calculate_distances,format_routes
import time
import os

# Example custom rounding function
def custom_round(value):
    return round(value)

# Load your dataset
def load_data():
    # Construct the path to the CSV file
    csv_path = os.path.join('..','templates', 'final.csv')
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path, encoding='ISO-8859-1')
    
    # Convert 'Month' column to datetime
    df['Month'] = pd.to_datetime(df['Month'])
    return df

# Example of using the load_data function
if __name__ == "__main__":
    df = load_data()
    print(df.head())  # Display the first few rows of the DataFrame

def custom_round(value):
    # Custom rounding logic, e.g., round to the nearest whole number
    return round(value)

# Load and preprocess data
df = load_data()

# Convert Latitude and Longitude columns to numeric, coercing errors
df['Latitude_D'] = pd.to_numeric(df['Latitude_D'], errors='coerce')
df['Longitude_D'] = pd.to_numeric(df['Longitude_D'], errors='coerce')
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

# Drop rows where Latitude or Longitude is NaN
df = df.dropna(subset=['Latitude_D', 'Longitude_D', 'Latitude', 'Longitude'])

st.title('Supply Network Optimizer')

# st.sidebar.radio(label='Simulation Type', options=['Time','Fuel'])

# Select Country
country = st.selectbox('Choose Country', ['Select a country'] + list(df['country'].unique()), index=0)

if 'show_simulate' not in st.session_state:
    st.session_state.show_simulate = False  # To track if Simulate button should be shown
if 'simulate_clicked' not in st.session_state:
    st.session_state.simulate_clicked = False

if country != 'Select a country':
    # Filter data based on selected country
    df_state = df[df['country'] == country]

    # Select State
    state = st.selectbox('Choose State', ['Select a state'] + list(df_state['state'].unique()), index=0)

    if state != 'Select a state':
        # Filter data based on selected state
        df_city = df_state[df_state['state'] == state]

        # Select City
        city = st.selectbox('Choose City', ['Select a city'] + list(df_city['city'].unique()), index=0)

        if city != 'Select a city':
            # Filter data based on selected city
            df_distributor = df_city[df_city['city'] == city]

            # Select Category
            category = st.selectbox('Choose Category', ['Select a category'] + list(df_distributor['Category'].unique()), index=0)

            if category != 'Select a category':
                # Filter data based on selected category
                df_category = df_distributor[df_distributor['Category'] == category]

                # Month selection by names
                month_names = {
                    'Jan': '01',
                    'Feb': '02',
                    'Mar': '03',
                    'Apr': '04',
                    'May': '05',
                    'Jun': '06',
                    'Jul': '07',
                    'Aug': '08',
                    'Sep': '09',
                    'Oct': '10',
                    'Nov': '11',
                    'Dec': '12'
                }
               
  

             

                    
            # Allow user to select one month by name
                selected_month_name = st.selectbox(
                    'Choose Month',
                    list(month_names.keys())
            )
            

                if selected_month_name:
                    # Convert month name to month number
                    selected_month_number = int(month_names[selected_month_name])  
                    
                    # Include the selected month from 2023
                    selected_month_2023 = f"2023-{str(selected_month_number).zfill(2)}"  # Selected month in 2023
                    
                    # Include the corresponding previous three months from 2024
                    previous_months_2024 = [f"2024-{str(month).zfill(2)}" for month in range(max(1, selected_month_number - 3), selected_month_number)]

                    # Combine 2023 selected month and previous three months of 2024
                    selected_months = [selected_month_2023] + previous_months_2024

                    # Convert the selected month to a datetime object (using the first day of the month)
                    selected_month = pd.to_datetime(f"2024-{str(selected_month_number).zfill(2)}-01", format='%Y-%m-%d')

                

                    # Calculate the previous month (3 months before the selected)
                    previous_month = selected_month - pd.DateOffset(months=3)

                

                    previous_month_str = previous_month.strftime('%Y-%m')

                    # Include both selected and previous month
                    selected_months.append(previous_month_str)

                    # Filter data based on the selected and previous months
                    df_selected_months = df_category[df_category['Month'].dt.strftime('%Y-%m').isin(selected_months)]

                    # Calculate Historical Average Quantity for each distributor for selected and previous months
                    distributor_avg_quantity = df_selected_months.groupby('Distributor')['Quantity'].sum().reset_index()
                    length_months = len(selected_months)-1
                
                    distributor_avg_quantity['Predicted_Sales'] = distributor_avg_quantity['Quantity'] / length_months

                    # Round the Historical Average Quantity
                    distributor_avg_quantity['Predicted_Sales'] = distributor_avg_quantity['Predicted_Sales'].apply(custom_round)

                    # Calculate Total Quantity for each distributor across all months
                    distributor_total_quantity = df.groupby('Distributor')['Quantity'].sum().reset_index()
                    distributor_total_quantity.columns = ['Distributor', 'Total_Quantity']

                    # Merge average and total quantities
                    distributor_summary = pd.merge(distributor_avg_quantity, distributor_total_quantity, on='Distributor')

                    # st.subheader(f'Total Sales by Distributors for Selected and Previous Month')
                    plt.figure(figsize=(13, 6))

                    # Calculate Total Sales for each distributor for selected and previous months
                    selected_months_sales = df_selected_months.groupby('Distributor')['Quantity'].sum().reset_index()
                    selected_months_sales.columns = ['Distributor', 'Selected_Months_Sales']

                    # Merge the selected months sales into the summary DataFrame
                    distributor_summary = pd.merge(distributor_summary, selected_months_sales, on='Distributor', how='left')
                    distributor_summary['Selected_Months_Sales'] = distributor_summary['Selected_Months_Sales'].fillna(0).round()

                    # Plot the total sales by distributors for the selected and previous months as a bar chart
                    bars = plt.bar(distributor_summary['Distributor'], distributor_summary['Selected_Months_Sales'], color='skyblue')

                    # Plot the total sales by distributors for the selected and previous months as a bar chart
                    bars = plt.bar(distributor_summary['Distributor'], distributor_summary['Selected_Months_Sales'], color='skyblue')

                       
                       
                    # if st.button('Total Sales in Graph'):
                    # # Code for the next process goes here
                    #     # st.write('Next process has started!')   

                         
                    #     st.subheader(f'Total Sales by Distributors for Selected and Previous Month')
                        

                    #     # Annotate each bar with its value inside the bar
                    #     for bar in bars:
                    #         yval = bar.get_height()
                    #         plt.text(
                    #             bar.get_x() + bar.get_width() / 2,  # X position (center of the bar)
                    #             yval / 2,  # Y position (middle of the bar)
                    #             f'{yval:.0f}',  # Value to display with no decimal places
                    #             ha='center',  # Horizontal alignment (centered)
                    #             va='center',  # Vertical alignment (centered)
                    #             fontsize=12,  # Font size of the label
                    #             color='black',  # Color of the label for better contrast
                    #             rotation=90  # Rotation angle of the text (90 degrees for vertical)
                    #         )

                    #     plt.title(f'Total Sales by Distributors for {selected_month_name} and Previous Month')
                    #     plt.xlabel('Distributor')
                    #     plt.ylabel('Total Sales (Selected and Previous Months)')
                    #     plt.xticks(rotation=45, ha='right')  # Rotate distributor names for better readability
                    #     plt.grid(True, axis='y')

                    #     st.pyplot(plt)

                

                    
                    if st.button('Predicted Sales'):
                        st.session_state.show_simulate = True
                            
                        st.sidebar.selectbox(label='Simulation Type', options=['Shortest Distance','Fuel','Time'])   
                           
                        # Predict the distribution quantity based on the selected and previous months
                        distributor_summary['Selected_Months_Sales'] = distributor_summary['Selected_Months_Sales'].apply(custom_round)

                        # Display distribution results
                        if not distributor_summary['Selected_Months_Sales'].sum() == 0:
                            st.subheader("Predicted Sales Distribution")
                            total_predicted_quantity = distributor_summary['Selected_Months_Sales'].sum()
                            for _, row in distributor_summary.iterrows():
                                st.write(f"{row['Distributor']} should receive: {row['Predicted_Sales']:.0f} units "
                                        f"({(row['Selected_Months_Sales'] / total_predicted_quantity) * 100:.1f}% of total distribution)")
                        else:
                            st.warning("Total selected months sales quantity is zero for the selected months.")

                        # Exclude 'Quantity' column for display
                        distributor_summary_display = distributor_summary.drop(columns=['Quantity', 'Total_Quantity', 'Selected_Months_Sales'])
                        st.write("Predicted Summary:")
                        st.write(distributor_summary_display)

                    if st.session_state.show_simulate:
                        if st.button('Simulate'):
                            st.session_state.simulate_clicked = True


                    if st.session_state.simulate_clicked:
                        progressBar = st.progress(0)
                        progressBar.progress(10)
                        time.sleep(0.8)
                        progressBar.progress(50)
                        time.sleep(0.2)
                        progressBar.progress(100)
                        


                        # # Create a single map centered on the selected city
                        city_lat = df_category['Latitude'].mean()  # Center map on the mean latitude
                        city_lon = df_category['Longitude'].mean() # Center map on the mean longitude
                        folium_map = folium.Map(location=[city_lat, city_lon], zoom_start=12)  # Zoom in to the ci

                        
                        # Create two columns for side-by-side display
                        col1, col2 = st.columns(2)

                    # Loop through each Manufacturing Plant and add its distributors to the map
                        for i, selected_plant in enumerate(df['Manufacturing_Plant'].unique()):
                            # Filter data for the selected plant
                            df_plant = df[df['Manufacturing_Plant'] == selected_plant]
                           
                            
                            if not df_plant.empty:
                                # Get the latitude and longitude of the selected plant
                                plant_lat = df_plant.iloc[0]['Latitude']
                                plant_lon = df_plant.iloc[0]['Longitude']

                                # Calculate distances between the selected plant and all distributors
                                plant_location = (plant_lat, plant_lon)
                                df_category['Distance'] = df_category.apply(
                                    lambda row: geodesic(plant_location, (row['Latitude_D'], row['Longitude_D'])).km, axis=1)

                                # Filter distributors within 8 km
                                df_nearby = df_category[df_category['Distance'] < 8.5]

                                 # Display the distance information in the corresponding column
                                distance_info = df_nearby[['Distributor', 'Distance']].drop_duplicates().sort_values(by='Distance')

                                # Format the Distance column to one decimal place
                                distance_info['Distance'] = distance_info['Distance'].map(lambda x: f"{x:.2f} km")

                                if not df_nearby.empty:
                                    # Add locations for the selected city with updated popup content
                                    for _, row in df_nearby.iterrows():
                                        distributor = row['Distributor']

                                        predicted_sales = 0
                                        if 'Predicted_Sales' in distributor_summary.columns:
                                            sales_qty = distributor_summary[distributor_summary['Distributor'] == distributor]['Predicted_Sales']
                                            if not sales_qty.empty:
                                                predicted_sales = sales_qty.values[0]
                                


                                        dealers = df['Distributor'].unique()
                                        # for deal in dealers:
                                            
                                        df_dealer = df[df['Distributor'] == distributor][['Latitude_D', 'Longitude_D']].drop_duplicates()
                                        lat = list(df_dealer['Latitude_D'])
                                        long = df_dealer['Longitude_D'].values.tolist()

                                        popup_content = f"<strong>Distributor:</strong> {distributor}<br>"
                                        popup_content += f"<strong>Predicted Sales:</strong> {predicted_sales:.0f} units<br>"
                                        popup_content += f"<strong>Distance from {selected_plant}:</strong> {row['Distance']:.2f} km<br>"

                                        

                                        folium.Marker(
                                            location=[lat[0], long[0]],
                                            popup=folium.Popup(popup_content, max_width=300),
                                            icon=folium.Icon(icon='info-sign', prefix='glyphicon', color='blue')
                                        ).add_to(folium_map)
                                    
                                   

                                    # Add marker for Manufacturing
                                    Manufactures =df['Manufacturing_Plant'].unique()

                                    
                                    
                                    for manfo in Manufactures:
                                        df_Manufacture = df[df['Manufacturing_Plant'] == manfo][['Latitude', 'Longitude']].drop_duplicates()
                                        lat1 = list(df_Manufacture['Latitude'])
                                        long1 = df_Manufacture['Longitude'].values.tolist()   
                                            
                                        

                                        folium.Marker(
                                        location=[lat1[0], long1[0]],
                                        popup=manfo,
                                        icon=folium.Icon(icon='factory', prefix='fa', color='green')
                                    ).add_to(folium_map)
                                        
                             

                             
                                # Display in the corresponding column
                                if i % 2 == 0:
                                    col1.subheader(f'Distances from {selected_plant} to distributors :')
                                    col1.write(distance_info)
                                    # print("Distance info -> " ,distance_info)


                                    
                                    col3, col4 = st.columns(2)
                            
                                    
                                    df_mp1 = df[df['Manufacturing_Plant'] == selected_plant][['Latitude', 'Longitude']].drop_duplicates()
                                    dict1 = {
                                        selected_plant: (df_mp1['Latitude'].iloc[0], df_mp1['Longitude'].iloc[0])
                                    }

                                    distributors = list(distance_info['Distributor'])
                                    for dist1 in distributors:
                                        df_dealer1 = df[df['Distributor'] == dist1][['Latitude_D', 'Longitude_D']].drop_duplicates()
                                        dict1[dist1] = (float(df_dealer1['Latitude_D'].values[0]), float(df_dealer1['Longitude_D'].values[0]))

                                    route_1 = shortest_route(dict1)
                                    best_route_1 = calculate_distances(route_1, dict1)

                                    
                                    with col3:
                                        st.subheader('Best route From MP1')
                                        st.markdown(format_routes(best_route_1), unsafe_allow_html=True)
                                        # st.write("Distance", best_route_1)
                                    # Prepare data for MP1
                                    dict1 = {
                                        selected_plant: (df_mp1['Latitude'].iloc[0], df_mp1['Longitude'].iloc[0])
                                    }
                                    for dist1 in distance_info['Distributor']:
                                        df_dealer1 = df[df['Distributor'] == dist1][['Latitude_D', 'Longitude_D']].drop_duplicates()
                                        # Add marker for Dealers
                                        
                                        dict1[dist1] = (float(df_dealer1['Latitude_D'].values[0]), float(df_dealer1['Longitude_D'].values[0]))
                                        
                                        
                                    

                                else:
                                    col2.subheader(f'Distances from {selected_plant} to distributors:')
                                    col2.write(distance_info)

                                    df_mp2 = df[df['Manufacturing_Plant'] == selected_plant][['Latitude', 'Longitude']].drop_duplicates()
                                    dict2 = {
                                        selected_plant: (float(df_mp2['Latitude'].values[0]), float(df_mp2['Longitude'].values[0]))
                                    }

                                    distributors = list(distance_info['Distributor'])
                                    for dist2 in distributors:
                                        df_dealer2 = df[df['Distributor'] == dist2][['Latitude_D', 'Longitude_D']].drop_duplicates()
                                        dict2[dist2] = (float(df_dealer2['Latitude_D'].values[0]), float(df_dealer2['Longitude_D'].values[0]))

                                    route_2 = shortest_route(dict2)
                                    best_route_2 = calculate_distances(route_2, dict2)


                                    with col4:
                                        st.subheader('Best route From MP2')
                                        st.markdown(format_routes(best_route_2), unsafe_allow_html=True)

                
                                        
                                        # Adding the lines for best route
                                        def add_routes_to_map(folium_map, routes, location_dict, color):
                                            for start, end, distance in routes:
                                                if start in location_dict and end in location_dict:
                                                    locations = [location_dict[start], location_dict[end]]
                                                    folium.PolyLine(
                                                        locations=locations,
                                                        color=color,
                                                        weight=5,
                                                        dash_array="5, 10",
                                                        tooltip=f"{start} to {end}: {distance}",
                                                        line_opacity=0.6
                                                    ).add_to(folium_map)
                                                #     print("start -> ", start, "end -> ", end, "distance -> ", distance)
                                                # else:
                                                #     print(f"Missing coordinates for: {start} or {end}")

                                        

                                        # # Add routes for MP1
                                        add_routes_to_map(folium_map, best_route_1, dict1, color="blue")

                                        # Prepare data for MP2
                                        dict2 = {
                                            selected_plant: (df_mp2['Latitude'].iloc[0], df_mp2['Longitude'].iloc[0])
                                        }
                                        for dist2 in distance_info['Distributor']:
                                            df_dealer2 = df[df['Distributor'] == dist2][['Latitude_D', 'Longitude_D']].drop_duplicates()
                                            dict2[dist2] = (float(df_dealer2['Latitude_D'].values[0]), float(df_dealer2['Longitude_D'].values[0]))

                                        # Add routes for MP2
                                        add_routes_to_map(folium_map, best_route_2, dict2, color="red")

                        # Define HTML for colored dots with labels
                        green_dot = '<span style="color: green;">●</span> Manufacturing Plant'
                        blue_dot = '<span style="color: blue;">●</span> Distributor'
                        
                        st.subheader(f'Locations in {city} :  ')
      
                        # Display the subheader with HTML support
                        st.markdown(f'<br>{green_dot}<br>{blue_dot}', unsafe_allow_html=True)
                        # Display the map in Streamlit
                        folium_static(folium_map, width=800, height=500)


                else:
                    st.write("Please select a month to continue.")
            else:
                st.write("Please select a category to continue.")
        else:
            st.write("Please select a city to continue.")
    else:
        st.write("Please select a state to continue.")
else:
    st.write("Please select a country to continue.")




    
