using HTTP
using JSON

key = "AIzaSyApQzC_OLdxiITS7ynh_XsWZZOU8XOKQHs"
ostr = "origin=-3.729086,-38.507326"
dstr = "destination=-3.747068,-38.575223"
tstr = "departure_time=0"
qstr = "$ostr&$dstr&travel_mode=driving&units=metric&key=$key"
url = "https://maps.googleapis.com/maps/api/directions/json?$qstr"

r = HTTP.request("GET", url)
data = Nothing
if r.status == 200
    data = String(r.body)
    data = JSON.Parser.parse(data)
end