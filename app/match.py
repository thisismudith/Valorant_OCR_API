import cv2
import pytesseract as pyt
import re
from math import floor
from misc import CONFIG, compare_images, extract_numbers

# Add trigger events
ULT = {
    "astra": 7,
    "breach": 9,
    "brimstone": 8,
    "chamber": 8,
    "clove": 8,
    "cypher": 6,
    "deadlock": 7,
    "fade": 8,
    "gekko": 8,
    "harbor": 7,
    "iso": 7,
    "jett": 8,
    "kayo": 8,
    "killjoy": 9,
    "neon": 7,
    "omen": 7,
    "phoenix": 6,
    "raze": 8,
    "reyna": 6,
    "sage": 8,
    "skye": 8,
    "sova": 8,
    "viper": 9,
    "vyse": 8,
    "yoru": 7
}


class Match():
    def __init__(self):
        """Initialiaze Pytesseract and load the image"""
        pyt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.loc = self.img = self.attack = self.defense = self.scores = None

        # self.attack = self.img[453:675, 763:1725]
        # self.defense = self.img[758:985, 763:1725]
        # self.scores = self.img[680:758, 763:1725]

        self.players = []
        self.round_phase = 0


    def updateSnapshot(self, loc: str = None):
        """Updates the image snapshot"""
        if loc is not None:
            self.loc = loc

        self.img = cv2.imread(self.loc, cv2.IMREAD_GRAYSCALE)
        if self.img is None:
            return False

        self.attack = self.img[453:675, 763:1725]
        self.defense = self.img[758:985, 763:1725]
        self.scores = self.img[680:758, 763:1725]

        return True


    def get_player_by_name(self, i: int):
        """Gets the player name and updates the side"""
        if i < 5:
            name = pyt.image_to_string(self.attack[45*i:45*(i+1), 93:323], config=CONFIG).strip()
            side = "attack"
            team = "A"
        else:
            name = pyt.image_to_string(self.defense[45*(i-5):45*(i-4), 93:323], config=CONFIG).strip()
            side = "defense"
            team = "B"

        for player in self.players:
            if player["name"] == name:
                player["side"] = side
                return player

        # Create new player if player set not full
        if len(self.players) < 10:
            player = {"name": name, "side": side, "team": team}
            self.players.append(player)
            return player


    def get_player_info_from_loading_screen(self):
        """Gets the player names and agents from loading screen"""

        # Fetch side snapshots
        attack_names = self.img[453:1241, 100:400]
        attack_agents = self.img[453:1241, 620:716]
        defense_names = self.img[453:1241, 1844:2144]
        defense_agents = self.img[453:1241, 2364:2460]

        # Fill with nullset
        self.players = [{} for _ in range(10)]

        for i in range(5):
            lower_limit = floor(187.5*i)
            upper_limit = lower_limit + 37

            # Attack side
            name = pyt.image_to_string(attack_names[lower_limit:upper_limit], config=CONFIG).strip()
            agent = pyt.image_to_string(attack_agents[lower_limit:upper_limit], config=CONFIG).strip().lower()
            self.players[i]["name"] = name
            self.players[i]["agent"] = agent
            self.players[i]["side"] = "attack"
            self.players[i]["team"] = "A"

            # Defense side
            name = pyt.image_to_string(defense_names[lower_limit:upper_limit], config=CONFIG).strip()
            agent = pyt.image_to_string(defense_agents[lower_limit:upper_limit], config=CONFIG).strip().lower()
            self.players[i+5]["name"] = name
            self.players[i+5]["agent"] = agent
            self.players[i]["side"] = "defense"
            self.players[i]["team"] = "B"

        return self.players


    def get_round_phase(self):
        """Gets the round phase (Buy - 0, During - 1, Post - 2)"""
        pass


    def get_ultimate_status(self, side_attack: bool, agent: str, lower_limit: int, upper_limit: int):
        """Returns the ultimate status of the player"""
        if side_attack:
            res = extract_numbers(self.attack[lower_limit:upper_limit, 370:435], True)
            if len(res) == 0:
                res = [ULT[agent] for _ in range(2)]
            return res
        else:
            res = extract_numbers(self.defense[lower_limit:upper_limit, 370:435], True)
            if len(res) == 0:
                res = [ULT[agent] for _ in range(2)]
            return res


    def get_kda(self, side_attack: bool, lower_limit: int, upper_limit: int):
        """Returns the KDA of the player"""
        if side_attack:
            return extract_numbers(self.attack[lower_limit:upper_limit, 482:642], True)
            return re.findall('\d+', pyt.image_to_string(self.attack[lower_limit:upper_limit, 482:642], config=CONFIG))
        else:
            return extract_numbers(self.defense[lower_limit:upper_limit, 482:642], True)
            return re.findall('\d+', pyt.image_to_string(self.defense[lower_limit:upper_limit, 482:642], config=CONFIG))


    def get_weapon(self, side_attack: bool, lower_limit: int, upper_limit: int):
        """Returns the weapon of the player"""
        gun_list = ["vandal", "phantom", "spectre", "operator", "odin", "dead", "sheriff", "guardian", "bulldog", "ghost", "judge", "marshal", "frenzy", "classic", "stinger", "ares", "bucky", "melee"]
        if side_attack:
            gun_img = self.attack[lower_limit:upper_limit, 642:800]
        else:
            gun_img = self.defense[lower_limit:upper_limit, 642:800]

        scores = []
        
        for gun in gun_list:
            res = compare_images(gun_img, cv2.imread(r'C:\Users\dagam\Codes\Valorant_OCR_API\assets\guns_tab\{}.png'.format(gun), cv2.IMREAD_GRAYSCALE))

            # Threshold
            if res > 0.95:
                return gun

            scores.append(res)

        # If all failed, return minimum score
        return gun_list[scores.index(max(scores))]


    def get_shield(self, side_attack: bool, lower_limit: int, upper_limit: int):
        """Returns the shield of the player"""
        shield_list = ["heavy", "light", "none"]
        if side_attack:
            shield_img = self.attack[lower_limit:upper_limit, 800:840]
        else:
            shield_img = self.defense[lower_limit:upper_limit, 800:840]


        scores = []
        for shield in shield_list:
            res = compare_images(shield_img, cv2.imread(r'C:\Users\dagam\Codes\Valorant_OCR_API\assets\shields_tab\{}.png'.format(shield), cv2.IMREAD_GRAYSCALE))

            # Threshold
            if res > 0.95:
                return shield

            scores.append(res)
        
        # If all failed, return minimum score
        return shield_list[scores.index(max(scores))]

    def get_creds(self, side_attack: bool, lower_limit: int, upper_limit: int):
        """Returns the creds of the player"""
        if side_attack:
            return extract_numbers(self.attack[lower_limit:upper_limit, 880:940])
            return pyt.image_to_string(self.attack[lower_limit:upper_limit, 880:940], config=CONFIG).strip()
        else:
            return extract_numbers(self.defense[lower_limit:upper_limit, 880:940])
            return pyt.image_to_string(self.defense[lower_limit:upper_limit, 880:940], config=CONFIG).strip()


    def updatePreRound(self):
        """Update creds and weapon pre round (Buy Phase)"""

        # This function currently calls updateDuringRound
        self.updateDuringRound()


    def updateDuringRound(self, firstTime: bool = False):
        """Update ultimate status, KDA and weapons (including death) during round"""

        # Fetch new image
        self.updateSnapshot()

        for i in range(10):
            # Attack side
            if i < 5:
                lower_limit, upper_limit = 45*i, 45*(i+1)
                player = self.get_player_by_name(i)

                # Temp
                agents = ["reyna", "omen", "gekko", "kayo", "phoenix"]
                player["agent"] = agents[i]

                # If player doesn't exist, skip... (avoid errors while streaming)
                if player is None:
                    continue

                # Position
                player["position"] = i+1

                # Ultimate status
                player["ult"] = self.get_ultimate_status(True, player["agent"], lower_limit, upper_limit)

                # KDA
                player["kda"] = self.get_kda(True, lower_limit, upper_limit)

                # Weapon
                player["weapon"] = self.get_weapon(True, lower_limit, upper_limit)

                # Shield
                player["shield"] = self.get_shield(True, lower_limit, upper_limit)

                # Creds
                player["creds"] = self.get_creds(True, lower_limit, upper_limit)

                # First Time
                player["firstTime"] = firstTime

            # Defense side
            else:
                lower_limit, upper_limit = 45*(i-5), 45*(i-4)
                player = self.get_player_by_name(i)

                # Temp
                agents = ["neon", "killjoy", "sage", "jett", "fade"]
                player["agent"] = agents[i-5]

                # If player doesn't exist, skip... (avoid errors while streaming)
                if player is None:
                    continue
                
                # Position
                player["position"] = i-4

                # Ultimate status
                player["ult"] = self.get_ultimate_status(False, player["agent"], lower_limit, upper_limit)

                # KDA
                player["kda"] = self.get_kda(False, lower_limit, upper_limit)

                # Weapon
                player["weapon"] = self.get_weapon(False, lower_limit, upper_limit)

                # Shield
                player["shield"] = self.get_shield(False, lower_limit, upper_limit)

                # Creds
                player["creds"] = self.get_creds(False, lower_limit, upper_limit)

                # First Time
                player["firstTime"] = firstTime

        return self.players


    def updatePostRound(self):
        """Update scores, round number and weapon post round"""

        # This function currently calls updateDuringRound
        self.updateDuringRound()