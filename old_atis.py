import re   


def stretch(s):
    return " ".join([c for c in s])


def sep():
    return " "


wx_int = {"-VC": "nearby light",
          "+VC": "nearby heavy",
          "-": "light",
          "+": "heavy",
          "VC": "nearby"}
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
sky_cov = {"FEW": "few",
           "SCT": "scattered",
           "BKN": "broken",
           "OVC": "overcast"}

metar = "METAR XXXX 241100Z 26020KT 6000 FEW020TCU SCT030CB BKN060 OVC080 09/M00 Q1005 RMK 090 053 3/3="

_wind = re.search(r"(\d{3})?(VRB)?(\d{2})KT(?:G(\d+))?(?:.+(\d{3})V(\d{3}))?", metar)
_vis = re.search(r"\s(\d{4})\s((?:\d{4}[NWSE]))?(?:R(\d{2}[LR]?)/(\d{4}[NDU]))?", metar)
_wx_det = re.findall(r"([-+]?[A-Z]{2,7})", metar)
_sky_few = re.search(r"(FEW)(\d{3})(CB)?(TCU)?", metar)
_sky_sct = re.search(r"(SCT)(\d{3})(CB)?(TCU)?", metar)
_sky_bkn = re.search(r"(BKN)(\d{3})(CB)?(TCU)?", metar)
_sky_ovc = re.search(r"(OVC)(\d{3})(CB)?(TCU)?", metar)
_sky_skc = re.search(r"SKC", metar)
_sky_nsc = re.search(r"NSC", metar)
_sky_vv = re.search(r"VV(\d{3})", metar)
_cavok = re.search(r"CAVOK", metar)
_temp_pres = re.search(r"(M?\d{2})/(M?\d{2}).Q(\d{3,4})", metar)

_wind_dir, _wind_var, _wind_speed, _wind_gusts, _wind_var_from, _wind_var_to = _wind.groups()

if _vis is not None:
    _vis_reg, _vis_dir, _vis_rvr_rw, _vis_rvr_vis = _vis.groups()

if _sky_few is not None:
    _sky_few_cov, _sky_few_quan, _sky_few_cb, _sky_few_tcu = _sky_few.groups()
else:
    _sky_few_cov = None

if _sky_sct is not None:
    _sky_sct_cov, _sky_sct_quan, _sky_sct_cb, _sky_sct_tcu = _sky_sct.groups()
else:
    _sky_sct_cov = None

if _sky_bkn is not None:
    _sky_bkn_cov, _sky_bkn_quan, _sky_bkn_cb, _sky_bkn_tcu = _sky_bkn.groups()
else:
    _sky_bkn_cov = None

if _sky_ovc is not None:
    _sky_ovc_cov, _sky_ovc_quan, _sky_ovc_cb, _sky_ovc_tcu = _sky_ovc.groups()
else:
    _sky_ovc_cov = None

if _sky_vv is not None:
    _sky_vv_det = _sky_vv.groups()
    for i in _sky_vv_det:
        _sky_vv = _sky_vv_det[0]

_t, _dew, _qnh = _temp_pres.groups()

if _wind_dir is None:
    _wind_dir = "001"

wind = ""
vis = ""
sky = "Clouds "
wx_final = ""
temp_group = ""
qnh = ""

# Wind decoding

if int(_wind_dir) == 0 and int(_wind_speed) == 0:
    wind = "Wind calm. "
else:
    if int(_wind_dir) != 0 and str(_wind_var) != "VRB":
        wind += "Wind " + stretch(_wind_dir) + " degrees "
    else:
        wind += "Wind variable "
    if int(_wind_speed) != 0:
        wind += "at " + stretch(_wind_speed) + " knots. "
    if _wind_gusts and int(_wind_gusts) != 0:
        wind += "Gusting " + stretch(_wind_gusts) + " knots. "
    if _wind_var_from:
        wind += "Variable between " + stretch(_wind_var_from) + " degrees and " + stretch(_wind_var_to) + " degrees. "

# Visibility decoding

if _vis_reg is not None:
    if int(_vis_reg) == 9999:
        vis = "Visibility 10 kilometers or more.  "
    else:
        if int(_vis_reg) < 9999 and int(_vis_reg) >= 6000:
            vis = "Visibility " + _vis_reg[0] + " kilometers. "
        if int(_vis_reg) < 6000 and int(_vis_reg) >= 1000:
            if int(_vis_reg[1]) == 0:
                vis = "Visibility " + _vis_reg[0] + " thousand meters. "
            else:
                vis = "Visibility " + _vis_reg[0] + " thousands " + _vis_reg[1] + " hundred meters. "
        if int(_vis_reg) < 1000:
            vis = "Visibility " + _vis_reg[0] + " meters. "
        if _vis_dir is not None and int(_vis_dir[1]) == 0 and len(_vis_dir) == 5:
            vis += "Directional visibility " + _vis_dir[0] + " kilometers " + _vis_dir[4] + "."
        elif _vis_dir is not None and int(_vis_dir[1]) != 0 and len(_vis_dir) == 5:
            vis += "Directional visibility " + _vis_dir[0] + " kilometers " + _vis_dir[1] + " hundred meters " + _vis_dir[4] + "."
        elif _vis_dir is not None and int(_vis_dir[1]) != 0 and len(_vis_dir) == 5:
            vis += "Directional visibility " + _vis_dir[0] + " hundred meters " + _vis_dir[4] + "."
        if _vis_dir is not None:
            vis = vis.replace("W", "West")
            vis = vis.replace("N", "North")
            vis = vis.replace("E", "East")
            vis = vis.replace("S", "South")
        if _vis_rvr_rw is not None and _vis_rvr_vis is not None and _vis_rvr_vis[1] != 0:
            vis += "Runway visual range, runway " + stretch(_vis_rvr_rw) + " . " + _vis_rvr_vis[0] + " thousand " + _vis_rvr_vis[1] + " hundred meters. " + _vis_rvr_vis[4] + ". "
        elif _vis_rvr_rw is not None and _vis_rvr_vis is not None and _vis_rvr_vis[1] == 0:
            vis += "Runway visual range, runway " + stretch(_vis_rvr_rw) + " . " + _vis_rvr_vis[0] + " thousand meters. " + _vis_rvr_vis[4] + ". "
        elif _vis_rvr_rw is not None and _vis_rvr_vis is not None and _vis_rvr_vis[0] == 0:
            vis += "Runway visual range, runway " + stretch(_vis_rvr_rw) + " . " + _vis_rvr_vis[1] + " hundred meters. " + _vis_rvr_vis[4] + ". "
        if _vis_rvr_rw is not None:
            vis = vis.replace(" D.", " decreasing ")
            vis = vis.replace(" N.", " non-changing ")
            vis = vis.replace(" U.", " raising ")

# Sky clouds or sky decoding

if _sky_few_cov is not None:
    if _sky_few_quan[1] != "0" and _sky_few_quan[2] != "0":
        sky += sky_cov[_sky_few_cov] + " at " + _sky_few_quan[1] + " thousand " + _sky_few_quan[2] + " hundred feet. "
    elif _sky_few_quan[2] == "0":
        sky += sky_cov[_sky_few_cov] + " at " + _sky_few_quan[1] + " thousand feet. "
    elif _sky_few_quan[1] == "0":
        sky += sky_cov[_sky_few_cov] + " at " + _sky_few_quan[2] + " hundred feet. "
    if _sky_few_cb is not None:
        sky += " Cumulus. "
    if _sky_few_tcu is not None:
        sky += " Tower Cumulus. "

if _sky_sct_cov is not None:
    if _sky_sct_quan[1] != "0" and _sky_sct_quan[2] != "0":
        sky += sky_cov[_sky_sct_cov] + " at " + _sky_sct_quan[1] + " thousand " + _sky_sct_quan[2] + " hundred feet. "
    elif _sky_sct_quan[2] == "0":
        sky += sky_cov[_sky_sct_cov] + " at " + _sky_sct_quan[1] + " thousand feet. "
    elif _sky_sct_quan[1] == "0":
        sky += sky_cov[_sky_sct_cov] + " at " + _sky_sct_quan[2] + " hundred feet. "
    if _sky_sct_cb is not None:
        sky += " Cumulus. "
    if _sky_sct_tcu is not None:
        sky += " Tower Cumulus. "

if _sky_bkn_cov is not None:
    if _sky_bkn_quan[1] != "0" and _sky_bkn_quan[2] != "0":
        sky += sky_cov[_sky_bkn_cov] + " at " + _sky_bkn_quan[1] + " thousand " + _sky_bkn_quan[2] + " hundred feet. "
    elif _sky_bkn_quan[2] == "0":
        sky += sky_cov[_sky_bkn_cov] + " at " + _sky_bkn_quan[1] + " thousand feet. "
    elif _sky_bkn_quan[1] == "0":
        sky += sky_cov[_sky_bkn_cov] + " at " + _sky_bkn_quan[2] + " hundred feet. "
    if _sky_bkn_cb is not None:
        sky += " Cumulus. "
    if _sky_bkn_tcu is not None:
        sky += " Tower Cumulus. "

if _sky_ovc_cov is not None:
    if _sky_ovc_quan[1] != "0" and _sky_ovc_quan[2] != "0":
        sky += sky_cov[_sky_ovc_cov] + " at " + _sky_ovc_quan[1] + " thousand " + _sky_ovc_quan[2] + " hundred feet. "
    elif _sky_ovc_quan[2] == "0":
        sky += sky_cov[_sky_ovc_cov] + " at " + _sky_ovc_quan[1] + " thousand feet. "
    elif _sky_ovc_quan[1] == "0":
        sky += sky_cov[_sky_ovc_cov] + " at " + _sky_ovc_quan[2] + " hundred feet. "
    if _sky_ovc_cb is not None:
        sky += " Cumulus. "
    if _sky_ovc_tcu is not None:
        sky += " Tower Cumulus. "

if _sky_vv is not None:
    sky = "Vertical visibility " + _sky_vv[0] + " " + _sky_vv[1] + " thousand " + _sky_vv[2] + " hundred feet. "
    sky = sky.replace("0 0 thousand", "")
    sky = sky.replace("0 hundred", "")

if _sky_skc is not None:
    sky = "Sky clear. "

# CAVOK

if _cavok is not None:
    vis = ""
    sky = _cavok[0]

# Weather details decoding


for i in _wx_det:
    for j in wx_int:
        if i.startswith(j) is True:
            wx_final += wx_int[j] + sep()
            i = i.replace(j, "")
    for j in wx_desc:
        if i.startswith(j) is True:
            wx_final += wx_desc[j] + sep()
            i = i.replace(j, "")
    for j in wx_prec:
        if i.startswith(j) is True:
            wx_final += wx_prec[j] + sep()
            i = i.replace(j, "")
    for j in wx_obsc:
        if i.startswith(j) is True:
            wx_final += wx_obsc[j] + sep()
            i = i.replace(j, "")
    for j in wx_msc:
        if i.startswith(j) is True:
            wx_final += wx_msc[j] + sep()
            i = i.replace(j, "")

# Temperature and pressure decoding

temp_group += " Temperature " + stretch(_t) + " degrees. Dew point " + stretch(_dew) + " degrees. "
if " M " in temp_group:
    temp_group = temp_group.replace("M", "minus")
qnh += " QNH " + stretch(_qnh)

print(wind+vis+sky+wx_final+temp_group+qnh)
