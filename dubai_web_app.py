import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from helper.utils import cal_distance, is_open_spot , get_spot_icon

df = pd.read_csv("./dubai_cold_coffee_spots_clean.csv")
df_areas = pd.read_csv("./dubai_area_label.csv")
st.set_page_config(page_title="Dubai Cold Coffee Finder" , page_icon="☕",layout = "wide")
st.title("☕ Dubai Cold Coffee Finder")
st.write("Find the nearest cold coffee spots around you in Dubai")
st.write("Explore cafes, carts, and trucks based on distance, rating, and availability.")
st.header("📍 Select Your Area")
areas_label = list(df_areas["Label"])
# areas_label.insert(0,"Select Area")
selected_area = st.selectbox("Choose your area" , areas_label)

with st.sidebar :

  st.sidebar.header("🔍 Search & Filters")
  spot_name = st.text_input("Search by spot name", placeholder = "e.g. Arctic Brew")
  
  st.divider()
  st.header("⚙️ Filter")
  options = list(df["type"].unique())
  options.insert(0,"All")
  spot_type = st.selectbox("Spot type" ,options)
  max_dis = st.slider("Max Distance (km)" , min_value=1 , max_value=20,value = 10)
  min_rating = st.slider("Min Rating",min_value=1.0,max_value=5.0, value = 3.1 , step = 0.1)
  show_only_open = st.checkbox("Show only open spots",False)
  sort_by =st.radio("Sort by",["Distance","Rating"])
ss = df_areas[df_areas["Label"] == selected_area][["lat" ,"lng"]]
user_location = tuple(ss.iloc[0]) 

def get_row(row):
  return cal_distance(user_location,row)

df["distance_km"] = df.apply(get_row,axis=1) 
df["is_open"] = df.apply(is_open_spot,axis = 1)
df2 = df.copy()

if spot_type != "All":
  df = df[df["type"]== spot_type]

df = df[df["distance_km"] <= max_dis]
df = df[df["rating"] >= min_rating]

if show_only_open:
  df = df[df["is_open"] == "Open"]

if sort_by == "Distance":
  df = df.sort_values(by="distance_km")
else:
  df = df.sort_values(by="rating" , ascending=False)

if spot_name:
  df = df[df["name"].str.contains(spot_name,case= False)]


tab1 ,tab2 , tab3 = st.tabs(["🗺️ Nearby Spots","📊 Analytics","🏆 Leaderboard"])
with tab1:
  st.subheader(f"{len(df)} spots found")
  
  dubai_map = folium.Map(location = user_location , zoom_start= 13)
  marker_icon = folium.Icon(color="blue" , icon= "user")
  area_marker = folium.Marker(user_location , icon = marker_icon,tooltip= f"Area : { selected_area}")
  area_marker.add_to(dubai_map)

  for data in df.iterrows():
    row = data[1]
    lat = row["lat"]
    lng = row["lng"]
    name = row["name"]
    type = row["type"]
    is_open = row["is_open"]
    color = "black"
    if is_open == "close":
        color = "red"

    spot_location = (lat , lng)
    spot_icon = folium.Icon(color=color , icon="coffee",prefix= "fa")
    marker = folium.Marker(spot_location,icon=spot_icon , tooltip= f"Cafe /{type} : {name} ")
    marker.add_to(dubai_map)
  
  st_folium(dubai_map,height=350,use_container_width=True)
  for i in range(0,len(df),2):
    small_df = df.iloc[i:i+2]
    columns = st.columns(2)
    for j in range(0,2):
      with columns[j]:
        with st.container(border=True):
          row = small_df.iloc[j]
          spot_type= row["type"]
          icons = get_spot_icon(spot_type)
          st.subheader(f"{icons} {row["name"]}")
          col1 , col2 = st.columns(2)
          
          col1.markdown(f"**Type**:- {row["type"]}")
          col1.markdown(f"**Distance**:- {row["distance_km"]}")
          
          st.caption((f"{row["opening_time"]} - {row["closing_time"]}")) 

  
          if is_open == "open":
              status = "🟢Open"
          else:
              status = "🔴Close"


          col2.markdown(f"**status** :- {status}")
          rating = row["rating"]
          col2.markdown(f"**Rating**:-{"⭐"*int(rating)} {rating}  ")
            



with tab2:
  st.header("📊Analytics")
  st.subheader("📈 Summary Stats")
  c1 ,c2,c3,c4= st.columns(4)
  total_spots = len(df2) 
  avg_rating = round(df2["rating"].mean(),2)
  open_spots = len(df2[df2["is_open"] == "open"])
  sorted_data = df2.sort_values(by="distance_km")
  min_dis = sorted_data["distance_km"].iloc[0]
  c1.metric("Total spots" ,total_spots )
  c2.metric("Avg_rating" , avg_rating)
  c3.metric("Open Now" ,f"{open_spots} / {total_spots}")
  c4.metric("Nearest Spot", f"{min_dis} km")

  st.subheader("🏷️ Spots by Type")
  spot_counts = df2["type"].value_counts()
  st.bar_chart(spot_counts)
  
  st.subheader("⭐ Average Rating by Type")
  average_rating = df2.groupby("type")["rating"].mean()
  st.bar_chart(average_rating , color= "#00ffff" )
  

with tab3:
  df3 = pd.read_csv("./dubai_cold_coffee_spots_clean.csv")
  df3["distance_km"] = df3.apply(get_row,axis=1) 
  df3["is_open"] = df3.apply(is_open_spot,axis = 1)
  st.subheader("🏆 Leaderboard")
  st.subheader("🏆 Top 10 Rated Spots")
  df3= df3.sort_values(by="rating" , ascending=False).reset_index(drop = True).head(10)
  df3.index = df3.index +1
  st.dataframe(df3[["name","type","rating","distance_km"]])

  st.divider()

  st.subheader("📍 Nearest 10 Spots to You")
  df3 = df3.sort_values(by="distance_km").reset_index(drop=True).head(10)
  df3.index = df3.index +1
  st.dataframe(df3[["name","type","rating","distance_km"]])
  
  