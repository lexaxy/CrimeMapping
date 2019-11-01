# In[12]:


import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import shapely as shapely


map_df = gpd.read_file("Singapore_AL382.shp")

station_df = gpd.read_file("MRTLRT.shp")



# In[13]:


#! /usr/bin/python

import math

class SVY21:
    # Ref: http://www.linz.govt.nz/geodetic/conversion-coordinates/projection-conversions/transverse-mercator-preliminary-computations/index.aspx
    
    # WGS84 Datum
    a = 6378137
    f = 1 / 298.257223563

    # SVY21 Projection
    # Fundamental point: Base 7 at Pierce Resevoir.
    # Latitude: 1 22 02.9154 N, longitude: 103 49 31.9752 E (of Greenwich).

    # Known Issue: Setting (oLat, oLon) to the exact coordinates specified above
    # results in computation being slightly off. The values below give the most 
    # accurate represenation of test data.
    oLat = 1.366666     # origin's lat in degrees
    oLon = 103.833333   # origin's lon in degrees
    oN = 38744.572      # false Northing
    oE = 28001.642      # false Easting
    k = 1               # scale factor

    def __init__(self):
        self.b = self.a * (1 - self.f)
        self.e2 = (2 * self.f) - (self.f * self.f)
        self.e4 = self.e2 * self.e2
        self.e6 = self.e4 * self.e2
        self.A0 = 1 - (self.e2 / 4) - (3 * self.e4 / 64) - (5 * self.e6 / 256);
        self.A2 = (3. / 8.) * (self.e2 + (self.e4 / 4) + (15 * self.e6 / 128));
        self.A4 = (15. / 256.) * (self.e4 + (3 * self.e6 / 4));
        self.A6 = 35 * self.e6 / 3072;

    def computeSVY21(self, lat, lon):
        """
        Returns a pair (N, E) representing Northings and Eastings in SVY21.
        """

        latR = lat * math.pi / 180
        sinLat = math.sin(latR)
        sin2Lat = sinLat * sinLat
        cosLat = math.cos(latR)
        cos2Lat = cosLat * cosLat
        cos3Lat = cos2Lat * cosLat
        cos4Lat = cos3Lat * cosLat
        cos5Lat = cos4Lat * cosLat
        cos6Lat = cos5Lat * cosLat
        cos7Lat = cos6Lat * cosLat

        rho = self.calcRho(sin2Lat)
        v = self.calcV(sin2Lat)
        psi = v / rho
        t = math.tan(latR)
        w = (lon - self.oLon) * math.pi / 180

        M = self.calcM(lat)
        Mo = self.calcM(self.oLat)

        w2 = w * w
        w4 = w2 * w2
        w6 = w4 * w2
        w8 = w6 * w2

        psi2 = psi * psi
        psi3 = psi2 * psi
        psi4 = psi3 * psi

        t2 = t * t
        t4 = t2 * t2
        t6 = t4 * t2

        # Compute Northing
        nTerm1 = w2 / 2 * v * sinLat * cosLat
        nTerm2 = w4 / 24 * v * sinLat * cos3Lat * (4 * psi2 + psi - t2)
        nTerm3 = w6 / 720 * v * sinLat * cos5Lat * ((8 * psi4) * (11 - 24 * t2) - (28 * psi3) * (1 - 6 * t2) + psi2 * (1 - 32 * t2) - psi * 2 * t2 + t4)
        nTerm4 = w8 / 40320 * v * sinLat * cos7Lat * (1385 - 3111 * t2 + 543 * t4 - t6)
        N = self.oN + self.k * (M - Mo + nTerm1 + nTerm2 + nTerm3 + nTerm4)

        # Compute Easting
        eTerm1 = w2 / 6 * cos2Lat * (psi - t2)
        eTerm2 = w4 / 120 * cos4Lat * ((4 * psi3) * (1 - 6 * t2) + psi2 * (1 + 8 * t2) - psi * 2 * t2 + t4)
        eTerm3 = w6 / 5040 * cos6Lat * (61 - 479 * t2 + 179 * t4 - t6)
        E = self.oE + self.k * v * w * cosLat * (1 + eTerm1 + eTerm2 + eTerm3)

        return (N, E)

    def calcM(self, lat):
        latR = lat * math.pi / 180
        return self.a * ((self.A0 * latR) - (self.A2 * math.sin(2 * latR)) + (self.A4 * math.sin(4 * latR)) - (self.A6 * math.sin(6 * latR)))

    def calcRho(self, sin2Lat):
        num = self.a * (1 - self.e2)
        denom = math.pow(1 - self.e2 * sin2Lat, 3. / 2.)
        return num / denom

    def calcV(self, sin2Lat):
        poly = 1 - self.e2 * sin2Lat
        return self.a / math.sqrt(poly)

    def computeLatLon(self, N, E):
        """
        Returns a pair (lat, lon) representing Latitude and Longitude.
        """

        Nprime = N - self.oN
        Mo = self.calcM(self.oLat)
        Mprime = Mo + (Nprime / self.k)
        n = (self.a - self.b) / (self.a + self.b)
        n2 = n * n
        n3 = n2 * n
        n4 = n2 * n2
        G = self.a * (1 - n) * (1 - n2) * (1 + (9 * n2 / 4) + (225 * n4 / 64)) * (math.pi / 180)
        sigma = (Mprime * math.pi) / (180. * G)
        
        latPrimeT1 = ((3 * n / 2) - (27 * n3 / 32)) * math.sin(2 * sigma)
        latPrimeT2 = ((21 * n2 / 16) - (55 * n4 / 32)) * math.sin(4 * sigma)
        latPrimeT3 = (151 * n3 / 96) * math.sin(6 * sigma)
        latPrimeT4 = (1097 * n4 / 512) * math.sin(8 * sigma)
        latPrime = sigma + latPrimeT1 + latPrimeT2 + latPrimeT3 + latPrimeT4

        sinLatPrime = math.sin(latPrime)
        sin2LatPrime = sinLatPrime * sinLatPrime

        rhoPrime = self.calcRho(sin2LatPrime)
        vPrime = self.calcV(sin2LatPrime)
        psiPrime = vPrime / rhoPrime
        psiPrime2 = psiPrime * psiPrime
        psiPrime3 = psiPrime2 * psiPrime
        psiPrime4 = psiPrime3 * psiPrime
        tPrime = math.tan(latPrime)
        tPrime2 = tPrime * tPrime
        tPrime4 = tPrime2 * tPrime2
        tPrime6 = tPrime4 * tPrime2
        Eprime = E - self.oE
        x = Eprime / (self.k * vPrime)
        x2 = x * x
        x3 = x2 * x
        x5 = x3 * x2
        x7 = x5 * x2

        # Compute Latitude
        latFactor = tPrime / (self.k * rhoPrime)
        latTerm1 = latFactor * ((Eprime * x) / 2)
        latTerm2 = latFactor * ((Eprime * x3) / 24) * ((-4 * psiPrime2) + (9 * psiPrime) * (1 - tPrime2) + (12 * tPrime2))
        latTerm3 = latFactor * ((Eprime * x5) / 720) * ((8 * psiPrime4) * (11 - 24 * tPrime2) - (12 * psiPrime3) * (21 - 71 * tPrime2) + (15 * psiPrime2) * (15 - 98 * tPrime2 + 15 * tPrime4) + (180 * psiPrime) * (5 * tPrime2 - 3 * tPrime4) + 360 * tPrime4)
        latTerm4 = latFactor * ((Eprime * x7) / 40320) * (1385 - 3633 * tPrime2 + 4095 * tPrime4 + 1575 * tPrime6)
        lat = latPrime - latTerm1 + latTerm2 - latTerm3 + latTerm4

        # Compute Longitude
        secLatPrime = 1. / math.cos(lat)
        lonTerm1 = x * secLatPrime
        lonTerm2 = ((x3 * secLatPrime) / 6) * (psiPrime + 2 * tPrime2)
        lonTerm3 = ((x5 * secLatPrime) / 120) * ((-4 * psiPrime3) * (1 - 6 * tPrime2) + psiPrime2 * (9 - 68 * tPrime2) + 72 * psiPrime * tPrime2 + 24 * tPrime4)
        lonTerm4 = ((x7 * secLatPrime) / 5040) * (61 + 662 * tPrime2 + 1320 * tPrime4 + 720 * tPrime6)
        lon = (self.oLon * math.pi / 180) + lonTerm1 - lonTerm2 + lonTerm3 - lonTerm4

        return (lat / (math.pi / 180), lon / (math.pi / 180))


# In[14]:


map_df.head()


# In[15]:


station_df


# In[16]:


map_df['geometry']


# In[17]:


map_df.plot()


# In[18]:


station_df.plot()


# In[19]:


x_list = []
y_list = []
points =[]

for coordinate in station_df['geometry']:
    x_list.append(coordinate.xy[0][0])
    y_list.append(coordinate.xy[1][0])
    
for i in range(0,len(x_list)):
    points.append([x_list[i], y_list[i]])

station_df['points'] = points

svy = SVY21()
station_df['new_coordinates'] = station_df.points.apply(lambda x: svy.computeLatLon(x[1], x[0]))
station_df.head()


# In[29]:


swap_coords = []

for i in station_df['new_coordinates']:
    swap_coords.append((i[1], i[0]))

new_station_df = pd.DataFrame(
    {'coordinates': swap_coords})


# In[65]:


point_list = []
for i in new_station_df['coordinates']:
    point_list.append(shapely.geometry.point.Point(i))


# In[66]:


s = gpd.GeoDataFrame({"geometry":point_list})


# In[67]:


s["station-names"] = station_df["STN_NAME"]
shortened_names = []
for i in s["station-names"]:
    shortened_names.append(i[:-12])
    
s["station-names"] = shortened_names


# In[68]:


s.head()


# In[37]:


s.plot()


# In[38]:


fig, ax = plt.subplots(figsize=(15,15))
map_df.plot(ax=ax)
s.plot(color = 'orange', ax=ax)


# In[93]:


import ast
crimeRates = ast.literal_eval("{'Admiralty': 2, 'Aljunied': 12, 'Ang Mo Kio': 35, 'Bartley': 0, 'Bayfront': 0, 'Beauty World': 2, 'Bedok': 46, 'Bedok North': 8, 'Bencoolen': 2, 'Bendemeer': 1, 'Bishan': 9, 'Boon Keng': 5, 'Boon Lay': 14, 'Botanic Gardens': 1, 'Braddell': 0, 'Bras Basah': 0, 'Buangkok': 2, 'Bugis': 3, 'Bukit Batok': 17, 'Bukit Gombak': 2, 'Bukit Panjang': 9, 'Buona Vista': 0, 'Caldecott': 0, 'Cashew': 0, 'Changi Airport': 20, 'Chinatown': 5, 'Chinese Garden': 0, 'Choa Chu Kang': 22, 'City Hall': 0, 'Clarke Quay': 8, 'Clementi': 25, 'Commonwealth': 9, 'Dakota': 0, 'Dhoby Ghaut': 1, 'Dover': 0, 'Downtown': 2, 'Esplanade': 0, 'Eunos': 3, 'Expo': 4, 'Farrer Park': 0, 'Farrer Road': 1, 'Fort Canning': 0, 'Geylang Bahru': 0, 'Gul Circle': 0, 'HarbourFront': 0, 'Haw Par Villa': 2, 'Hillview': 1, 'Holland Village': 3, 'Hougang': 18, 'Jalan Besar': 6, 'Joo Koon': 4, 'Jurong East': 9, 'Kaki Bukit': 7, 'Kallang': 7, 'Kembangan': 0, 'Kent Ridge': 0, 'Khatib': 0, 'King Albert Park': 2, 'Kovan': 6, 'Kranji': 7, 'Labrador Park': 1, 'Lakeside': 0, 'Lavender': 3, 'Little India': 26, 'Lorong Chuan': 0, 'MacPherson': 5, 'Marina Bay': 15, 'Marina South Pier': 0, 'Marsiling': 9, 'Marymount': 2, 'Mattar': 0, 'Mountbatten': 3, 'Newton': 1, 'Nicoll Highway': 0, 'Novena': 0, 'one-north': 1, 'Orchard': 45, 'Outram Park': 0, 'Pasir Panjang': 1, 'Pasir Ris': 16, 'Paya Lebar': 7, 'Pioneer': 3, 'Potong Pasir': 0, 'Promenade': 0, 'Punggol': 18, 'Queenstown': 1, 'Raffles Place': 1, 'Redhill': 1, 'Rochor': 5, 'Sembawang': 12, 'Sengkang': 21, 'Serangoon': 23, 'Simei': 8, 'Sixth Avenue': 0, 'Somerset': 0, 'Stadium': 1, 'Stevens': 0, 'Tai Seng': 1, 'Tampines': 16, 'Tan Kah Kee': 0, 'Tanah Merah': 4, 'Tanjong Pagar': 9, 'Telok Ayer': 0, 'Telok Blangah': 1, 'Tiong Bahru': 2, 'Toa Payoh': 24, 'Tuas Crescent': 0, 'Ubi': 3, 'Upper Changi': 13, 'Woodlands': 72, 'Woodleigh': 0, 'Yew Tee': 2, 'Yio Chu Kang': 2, 'Yishun': 44}")


# In[100]:


crimeRates = {k.upper(): v for k,v in crimeRates.items()}


# In[111]:


s['crimeRate'] = 0


# In[109]: currently here, trying to merge the two 


for i in s['station-names']:
    print(i)
    print(crimeRates.get(i))
    s['crimeRate'] = crimeRates.get(i)
