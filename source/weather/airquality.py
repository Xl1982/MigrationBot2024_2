api_key = "75dd8a1c967ae833bfbfe749710213518bfe92752a4e62645537c05c8cb1db68"

import requests

def get_air_quality(api_key):
    url = "http://api.airvisual.com/v2/city?city=Alicante&country=Spain&key=" + api_key
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        return data["data"]["current"]["pollution"]
    else:
        return None
print(get_air_quality(api_key))
