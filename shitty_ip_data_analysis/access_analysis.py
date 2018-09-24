import re
import numpy as  np
import matplotlib.pyplot as plt
import pygeoip

def ipLocator(ip):
    #location of downloaded GeoLiteCity database
    #download from here: https://dev.maxmind.com/geoip/legacy/geolite/#Downloads
 GeoIPDatabase = 'GeoLiteCity.dat'
 ipData = pygeoip.GeoIP(GeoIPDatabase)
 record = ipData.record_by_name(ip)
 print('The geolocation for IP Address %s is:' % ip)
 print('Accurate Location: %s, %s, %s' % (record['city'], record['region_code'], record['country_name']))
 print('General Location: %s' % (record['metro_code']))

def ipLocatorCountry(ip):
    GeoIPDatabase = 'GeoLiteCity.dat'
    ipData = pygeoip.GeoIP(GeoIPDatabase)
    record = ipData.record_by_name(ip)
    return record['country_name']

content_ip = []
filename = "haxors.txt" #filename of log file to analyze
#filter out all ip addresses:
with open(filename, "r") as processed_file:
    content = processed_file.readlines()
    content_stripped = [x.strip() for x  in content]
    for x in content_stripped:
        curr_ip = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", x) #only find ip-adresses in the logfile
        content_ip.append(curr_ip.group(0))

uniqips = sorted(set(content_ip)) #remove duplicate words and sort
country_file = open('countries.txt','w') #open file for countries
ip_count = []
for ip in uniqips:
    ip_count.append(content_ip.count(ip)) #count occurences of unique ips
    #do some geolocation:
    #country_file.write(ipLocatorCountry(ip))
    try:
        print(ipLocatorCountry(ip)) #do the geolocation of each unique ip
        country_file.write(ipLocatorCountry(ip))
        country_file.write("\n")
    except:
        print("error")

country_file.close()

#do some statistics and plotting

total_access_tries = sum(ip_count) #compute total nr. of access as sum of all lines/ips etc
ip_count_np = np.asarray(ip_count) #convert to numpy array
fractional_count = ip_count_np/total_access_tries #calculate fraction and multiply by 100 to get percent
fractional_count = fractional_count * 100

#plot nice pie chart

fig1, ax1 = plt.subplots()
ax1.pie(fractional_count, shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title('Fractional Count: Total Access Tries: {} from {} different ips. \nTop Hit: {} tries'.format(total_access_tries, ip_count_np.size, ip_count_np.max()))
plt.show()

