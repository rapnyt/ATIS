import re
from num2words import num2words

metar = "METAR XXXX 241100Z 26020KT 5500 FEW020TCU SCT030CB BKN060 OVC080 09/M00 Q1005 RMK 090 053 3/3="

def stretch(s):
    return " ".join(s)

def wind_decode(var):
    wind = ""
    _wind = re.search(r"(VRB)?(\d{3})?(\d{2}G)?(\d{2}KT)(\d{3})?V?(\d{3})?", var)
    variable, direction, speed1, speed2, var1, var2 = _wind.groups()

    if variable:
        wind += f"Wind variable at {speed2[1]} knots." if speed2[0] == '0' else f"Wind variable at {stretch(speed2[0:2])} knots."
    else:
        wind += f"Wind {stretch(direction)} degrees"
        if speed1:
            wind += f" at {speed2[1]} knots. Gusting {stretch(speed2[0:2])} knots." if speed1[0] == '0' else \
                    f" at {stretch(speed1[0:2])} knots. Gusting {stretch(speed2[0:2])} knots."
        else:
            wind += f" at {speed2[1]} knots." if speed2[0] == '0' else f" at {stretch(speed2[0:2])} knots."

        if var1:
            wind += f" Variable between {stretch(var1)} and {stretch(var2)} degrees."

        if direction == "000" and speed2 == "00KT":
            wind = "Wind calm."

    return wind

def visibility_decoder(var):
    visibility = ""
    _visibility = re.search(r"\s(\d{4})([NWES]{1,2})?\s", var)
    visibility_number, direction = _visibility.groups()

    visibility += f"Visibility {'10 kilometers or more.' if visibility_number == '9999' else num2words(visibility_number)} meters."

    if direction:
        visibility = visibility.replace(".", f" at direction ")
        direction_dictionary = {"N": "north", "W": "west", "E": "east", "S": "south"}
        for i in direction:
            visibility += f"{direction_dictionary[i]} "

    return visibility

def phenomena_decoder(var):
    wx = {
        "-VC": "Nearby light",
        "+VC": "Nearby heavy",
        "-": "Light",
        "+": "Heavy",
        "VC": "Nearby",
        "MI": "shallow",
        "BC": "patches of",
        "DR": "low drifting",
        "BL": "blowing",
        "SH": "showers",
        "TS": "thunderstorm",
        "FZ": "freezing",
        "DZ": "drizzle",
        "RA": "rain",
        "SN": "snow",
        "SG": "snow grains",
        "IC": "ice crystals",
        "PL": "ice pellets",
        "GR": "hail",
        "GS": "snow pellets",
        "UP": "unknown precipitation",
        "BR": "mist",
        "FG": "fog",
        "FU": "smoke",
        "VA": "volcanic ash",
        "DU": "dust",
        "SA": "sand",
        "HZ": "haze",
        "PO": "sand whirls",
        "SQ": "squalls",
        "FC": "funnel cloud",
        "SS": "sandstorm",
        "DS": "dust storm"
    }
    phenomena = " ".join(wx.get(m.group(), "") for m in re.finditer(r"([-+]?[A-Z]{2,7})", var))
    return f"Moderate {phenomena}" if phenomena and not phenomena.startswith(('Light', 'Heavy', 'Nearby')) else phenomena

def sky_decoder(var):
    clouds = {"FEW": "Few", "SCT": "Scattered", "BKN": "Broken", "OVC": "Overcast"}
    sky = " ".join(f"{clouds[match.group(1)]} at {num2words(int(match.group(2)) * 100)} feet." for match in re.finditer(r"(FEW|SCT|BKN|OVC)(\d{3})([TCBU]{2,3})?", var))
    return f"Clouds {sky}" if sky else ""

def temperature_decoder(var):
    temperature = re.search(r"(M)?(\d{2})/(M)?(\d{2})", var)
    if temperature:
        minus_temp, temp, minus_dew_point, dew_temp = temperature.groups()
        temperature = f"Temperature {'minus ' if minus_temp else ''}{temp} degrees dew point {'minus ' if minus_dew_point else ''}{dew_temp} degrees."
    return temperature if temperature else ""

def qnh_decoder(var):
    qnh = re.search(r"Q(\d{3,4})", var)
    return f"QNH {' '.join(num2words(digit) for digit in qnh.group(1))}." if qnh else ""

def decode_metar(var):
    decoded_metar = wind_decode(var) + " " + visibility_decoder(var) + " " + phenomena_decoder(var) + " " + sky_decoder(var) + " " + temperature_decoder(var) + " " + qnh_decoder(var)
    return " ".join(decoded_metar.split())

if __name__ == "__main__":
    decoded_metar = decode_metar(metar)
    print(decoded_metar)
