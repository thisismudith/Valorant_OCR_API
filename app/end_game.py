
import cv2
import pytesseract as pyt
from misc import CONFIG, extract_numbers


class Stats():
    def __init__(self):
        """Initialiaze Pytesseract and load the image"""
        pyt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.img = None

        self.players = [{} for _ in range (10)]


    def get_date(self):
        """Gets the date, gamemode, map and time"""
        info = pyt.image_to_string(self.img[130:210, 100:235], config=CONFIG).strip()
        date, gamemode, map, time = info.lower().split("\n")
        return {"date": date, "gamemode": gamemode, "map": map.split(' - ')[-1], "time": time}
    

    def get_scores(self):
        """Gets the score of the match"""
        scores = pyt.image_to_string(self.img[130:210, 1000:1300], config=CONFIG).strip()
        attack, defense = scores.split(" - ")
        return {"attack": attack, "defense": defense}


    def get_scores(self):
        """Gets scores of green and red team"""
        green_score = int(pyt.image_to_string(self.img[120:210, 950:1100], config=CONFIG).strip())
        red_score = int(pyt.image_to_string(self.img[120:210, 1400:1550], config=CONFIG).strip())
        return {"green": green_score, "red": red_score}


    def get_name_and_team(self, lower_limit: int, upper_limit: int):
        """Gets the name of the player"""
        img = self.img[lower_limit:upper_limit, 500:800] #440:800
        if img[0,0,0] < 80 and img[0,0,1] < 80:
            return (pyt.image_to_string(img, config=CONFIG).strip(), "red")
        return (pyt.image_to_string(img, config=CONFIG).strip(), None)


    def get_acs(self, lower_limit: int, upper_limit: int):
        """Gets the ACS of the player"""
        return int(pyt.image_to_string(self.img[lower_limit:upper_limit, 930:1030], config=CONFIG).strip())


    def get_kda(self, lower_limit: int, upper_limit: int):
        """Gets the KDA of the player"""
        return list(extract_numbers(self.img[lower_limit:upper_limit, 1105:1305], sep=True))


    def get_econ_rating(self, lower_limit: int, upper_limit: int):
        """Gets the econ rating of the player"""
        return extract_numbers(cv2.cvtColor(self.img[lower_limit:upper_limit, 1350:1450], cv2.COLOR_BGR2GRAY))


    def get_first_bloods(self, lower_limit: int, upper_limit: int):
        """Gets the first bloods of the player"""
        return extract_numbers(self.img[lower_limit:upper_limit, 1555:1655])
    

    def get_plants(self, lower_limit: int, upper_limit: int):
        """Gets the plants of the player"""
        return extract_numbers(self.img[lower_limit:upper_limit, 1750:1850])
    

    def get_defuses(self, lower_limit: int, upper_limit: int):
        """Gets the defuses of the player"""
        return extract_numbers(self.img[lower_limit:upper_limit, 1955:2055])


    def get_match_stats(self, loc: str):
        """Gets the match stats"""

        if loc is not None:
            self.loc = loc
            self.img = cv2.resize(cv2.imread(loc), (2560, 1440))

        if self.img is None:
            return {"error": "No image received"}

        res = self.get_scores() | self.get_date() | {"players": []}

        for i in range(10):
            lower_limit, upper_limit = 455 + 70*i, 520 + 70*i
            player = {}

            player["name"], player["team"] = self.get_name_and_team(lower_limit, upper_limit)
            player["acs"] = self.get_acs(lower_limit, upper_limit)
            player["kda"] = self.get_kda(lower_limit, upper_limit)
            player["econ_rating"] = self.get_econ_rating(lower_limit, upper_limit)
            player["first_bloods"] = self.get_first_bloods(lower_limit, upper_limit)
            player["plants"] = self.get_plants(lower_limit, upper_limit)
            player["defuses"] = self.get_defuses(lower_limit, upper_limit)

            # Add player
            res["players"].append(player)

        return res


# First Half - Defense (Green Team)
# Second Half - Attack (Green Team)