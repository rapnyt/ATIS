import re
from num2words import num2words
metar = "METAR XXXX 241100Z 26020KT 5500 FEW020TCU SCT030CB BKN060 OVC080 09/M00 Q1005 RMK 090 053 3/3="


def stretch(s):
    return " ".join([c for c in s])


def sep():
    return " "


def wind_decode(var):
    wind = ""
    _wind = re.search(r"(VRB)?(\d{3})?(\d{2}G)?(\d{2}KT)(\d{3})?V?(\d{3})?", var)
    variable, direction, speed1, speed2, var1, var2 = _wind.groups()
    # print(variable, direction, speed1, speed2, var1, var2)
    if variable is not None:
        wind += "Wind variable at "
        if speed2[0] == 0:
            wind += speed2[1] + " knots. "
        else:
            wind += stretch(speed2[0:2]) + " knots. "
    else:
        wind += "Wind " + stretch(direction) + " degrees"
        if speed1 is not None:
            wind += " at "
            if speed1[0] == 0:
                wind += speed2[1] + " knots. Gusting " + stretch(speed2[0:2]) + " knots. "
            else:
                wind += stretch(speed1[0:2]) + " knots. Gusting " + stretch(speed2[0:2]) + " knots. "
        else:
            wind += " at "
            if speed2[0] == 0:
                wind += speed2[1] + " knots. "
            else:
                wind += stretch(speed2[0:2]) + " knots. "
        if var1 is not None:
            wind += "Variable between " + stretch(var1) + " and " + stretch(var2) + " degrees."
        if direction == "000" and speed2 == "00KT":
            wind = "Wind calm. "
    return wind


def visibility_decoder(var):
    visibility = ""
    _visibility = re.search(r"\s(\d{4})([NWES]{1,2})?\s", var)
    visibility_number, direction = _visibility.groups()
    visibility += "Visibility "
    if visibility_number == "9999":
        visibility += "10 kilometers or more. "
    else:
        visibility += num2words(visibility_number) + " meters. "
    if direction is not None:
        visibility = visibility.replace(".", " at direction ")
        direction_dictionary = {"N": "north", "W": "west", "E": "east", "S": "south"}
        for i in direction:
            visibility += str(direction_dictionary[i]) + " "
    return visibility


def phenomena_decoder(var):
    wx_int = {"-VC": "Nearby light",
              "+VC": "Nearby heavy",
              "-": "Light",
              "+": "Heavy",
              "VC": "Nearby"}
    wx_desc = {"MI": "shallow",
               "BC": "patches of",
               "DR": "low drifting",
               "BL": "blowing",
               "SH": "showers",
               "TS": "thunderstorm",
               "FZ": "freezing"}
    wx_prec = {"DZ": "drizzle",
               "RA": "rain",
               "SN": "snow",
               "SG": "snow grains",
               "IC": "ice crystals",
               "PL": "ice pellets",
               "GR": "hail",
               "GS": "snow pellets",
               "UP": "unknown precipitation", }
    wx_obsc = {"BR": "mist",
               "FG": "fog",
               "FU": "smoke",
               "VA": "volcanic ash",
               "DU": "dust",
               "SA": "sand",
               "HZ": "haze", }
    wx_msc = {"PO": "sand whirls",
              "SQ": "squalls",
              "FC": "funnel cloud",
              "SS": "sandstorm",
              "DS": "dust storm"}
    phenomena_list = [wx_int, wx_desc, wx_prec, wx_obsc, wx_msc]
    phenomena = ""
    _phenomena = re.search(r"([-+]?[A-Z]{2,7})", var)
    _phenomena = _phenomena.groups()[0]

    if _phenomena is not None:
        phenomena = phenomena_auxiliary(phenomena, _phenomena, phenomena_list)
    phenomena = phenomena.replace("  ", " ")
    return phenomena


def phenomena_auxiliary(var1, var2, var3):  # var1 - phenomena, var2 - _phenomena, var3 - wx...
    for j in var3:
        for i in j:
            if var2.startswith(i):
                var1 += i
                var1 = var1.replace(i, j[i])
                var2 = var2[len(i):]
        var1 += " "
    if var1 is not None and var1.startswith(('Light', 'Heavy', 'Nearby')) is False:
        var1 = "Moderate " + var1
    return var1


def sky_decoder(var):
    sky = ""
    _sky_few = re.search(r"(FEW)(\d{3})([TCBU]{2,3})?", var)
    _sky_sct = re.search(r"(SCT)(\d{3})([TCBU]{2,3})?", var)
    _sky_bkn = re.search(r"(BKN)(\d{3})([TCBU]{2,3})?", var)
    _sky_ovc = re.search(r"(OVC)(\d{3})([TCBU]{2,3})?", var)

    if _sky_few is not None:
        sky_few, sky_few_quantity, sky_few_cb = _sky_few.groups()
        sky += sky_decoder_concentration(sky_few, sky_few_quantity, sky_few_cb)
    if _sky_sct is not None:
        sky_sct, sky_sct_quantity, sky_sct_cb = _sky_sct.groups()
        sky += sky_decoder_concentration(sky_sct, sky_sct_quantity, sky_sct_cb)
    if _sky_bkn is not None:
        sky_bkn, sky_bkn_quantity, sky_bkn_cb = _sky_bkn.groups()
        sky += sky_decoder_concentration(sky_bkn, sky_bkn_quantity, sky_bkn_cb)
    if _sky_ovc is not None:
        sky_ovc, sky_ovc_quantity, sky_ovc_cb = _sky_ovc.groups()
        sky += sky_decoder_concentration(sky_ovc, sky_ovc_quantity, sky_ovc_cb)
    sky = "Clouds " + sky
    if sky == "Clouds ":
        pass
    return sky


def sky_decoder_concentration(clouds, quantity, cb):
    clouds_dictionary = {"FEW": "Few", "SCT": "Scaterred", "BKN": "Broken", "OVC": "Overcast"}
    var = ""
    quantity = int(quantity) * 100
    var += clouds + " at " + num2words(quantity) + " feet. "
    if cb is not None:
        var += cb + " "
        var = var.replace("CB", "Cumulonimbus.")
        var = var.replace("TCU", "Towering cumulus.")
    var = var.replace(clouds, clouds_dictionary[clouds])
    return var


def temperature_decoder(var):
    temperature = "Temperature "
    _temperature = re.search(r"(M)?(\d{2})/(M)?(\d{2})", var)
    minus_temp, temp, minus_dew_point, dew_temp = _temperature.groups()
    if minus_temp is not None:
        temperature += "minus "
    for i in temp:
        temperature += num2words(i) + " "
    temperature += "dew point "
    if minus_dew_point is not None:
        temperature += "minus "
    for i in dew_temp:
        temperature += num2words(i) + " "
    return temperature


def qhn_decoder(var):
    qhn = " "
    _qhn = re.search(r"Q(\d{3,4})", var)
    qhn_pressure = _qhn.groups()[0]
    qhn += "QNH "
    for i in qhn_pressure:
        qhn += num2words(i) + " "
    return qhn


def changing_words_into_numbers(var):
    number_dictionary = {"one": " 1 ", "two": " 2 ", "three": " 3 ", "four": " 4 ", "five": " 5 ",
                         "six": " 6 ", "seven": " 7 ", "eight": " 8 ", "nine": " 9 ", "zero": " 0 "}
    for number in number_dictionary:
        var = var.replace(number, number_dictionary[number])
    return var


if __name__ == "__main__":
    decoded_metar = ""
    decoded_metar += wind_decode(metar)
    print(metar.find("CAVOK"))
    if metar.find("CAVOK") != -1:
        decoded_metar += "CAVOK. "
        decoded_metar += temperature_decoder(metar) + qhn_decoder(metar)
    else:
        decoded_metar += visibility_decoder(metar) + phenomena_decoder(metar) + sky_decoder(metar) + temperature_decoder(metar) + qhn_decoder(metar)
    decoded_metar = changing_words_into_numbers(decoded_metar)
    decoded_metar = decoded_metar.replace("  ", " ")
    print(decoded_metar)
