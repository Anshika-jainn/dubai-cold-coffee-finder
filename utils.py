from geopy.distance import geodesic
from datetime import datetime
def cal_distance(user_location,row):
       lat= row["lat"]
       lng=row["lng"]
       spot_location = (lat,lng)
       dis = geodesic(user_location,spot_location).km
       return round(dis,2)



def is_open_spot(row):
       open = row["opening_time"]
       close = row["closing_time"]
       a = datetime.now().strftime("%H:%M")
       if open <= a <= close:
              return "open"
       else:
              return "close"
       

def get_spot_icon(spot_type):
    icons = ["🏡","🛒","🚚"]
    if spot_type == "cafe" :
          return icons[0]
    elif  spot_type == "cart":
            return icons[1]
    else:
            return icons[2]