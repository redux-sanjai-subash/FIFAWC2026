from datetime import datetime

from ..db import db
from ..models import Match


QUALIFIED_TEAMS = [
    {"name": "Algeria", "code": "ALG", "flag": "🇩🇿", "confederation": "CAF"},
    {"name": "Argentina", "code": "ARG", "flag": "🇦🇷", "confederation": "CONMEBOL"},
    {"name": "Australia", "code": "AUS", "flag": "🇦🇺", "confederation": "AFC"},
    {"name": "Austria", "code": "AUT", "flag": "🇦🇹", "confederation": "UEFA"},
    {"name": "Belgium", "code": "BEL", "flag": "🇧🇪", "confederation": "UEFA"},
    {"name": "Bosnia and Herzegovina", "code": "BIH", "flag": "🇧🇦", "confederation": "UEFA"},
    {"name": "Brazil", "code": "BRA", "flag": "🇧🇷", "confederation": "CONMEBOL"},
    {"name": "Cabo Verde", "code": "CPV", "flag": "🇨🇻", "confederation": "CAF"},
    {"name": "Canada", "code": "CAN", "flag": "🇨🇦", "confederation": "CONCACAF"},
    {"name": "Colombia", "code": "COL", "flag": "🇨🇴", "confederation": "CONMEBOL"},
    {"name": "Congo DR", "code": "COD", "flag": "🇨🇩", "confederation": "CAF"},
    {"name": "Croatia", "code": "CRO", "flag": "🇭🇷", "confederation": "UEFA"},
    {"name": "Curacao", "code": "CUW", "flag": "🇨🇼", "confederation": "CONCACAF"},
    {"name": "Czechia", "code": "CZE", "flag": "🇨🇿", "confederation": "UEFA"},
    {"name": "Cote d'Ivoire", "code": "CIV", "flag": "🇨🇮", "confederation": "CAF"},
    {"name": "Ecuador", "code": "ECU", "flag": "🇪🇨", "confederation": "CONMEBOL"},
    {"name": "Egypt", "code": "EGY", "flag": "🇪🇬", "confederation": "CAF"},
    {"name": "England", "code": "ENG", "flag": "🏴", "confederation": "UEFA"},
    {"name": "France", "code": "FRA", "flag": "🇫🇷", "confederation": "UEFA"},
    {"name": "Germany", "code": "GER", "flag": "🇩🇪", "confederation": "UEFA"},
    {"name": "Ghana", "code": "GHA", "flag": "🇬🇭", "confederation": "CAF"},
    {"name": "Haiti", "code": "HAI", "flag": "🇭🇹", "confederation": "CONCACAF"},
    {"name": "IR Iran", "code": "IRN", "flag": "🇮🇷", "confederation": "AFC"},
    {"name": "Iraq", "code": "IRQ", "flag": "🇮🇶", "confederation": "AFC"},
    {"name": "Japan", "code": "JPN", "flag": "🇯🇵", "confederation": "AFC"},
    {"name": "Jordan", "code": "JOR", "flag": "🇯🇴", "confederation": "AFC"},
    {"name": "Korea Republic", "code": "KOR", "flag": "🇰🇷", "confederation": "AFC"},
    {"name": "Mexico", "code": "MEX", "flag": "🇲🇽", "confederation": "CONCACAF"},
    {"name": "Morocco", "code": "MAR", "flag": "🇲🇦", "confederation": "CAF"},
    {"name": "Netherlands", "code": "NED", "flag": "🇳🇱", "confederation": "UEFA"},
    {"name": "New Zealand", "code": "NZL", "flag": "🇳🇿", "confederation": "OFC"},
    {"name": "Norway", "code": "NOR", "flag": "🇳🇴", "confederation": "UEFA"},
    {"name": "Panama", "code": "PAN", "flag": "🇵🇦", "confederation": "CONCACAF"},
    {"name": "Paraguay", "code": "PAR", "flag": "🇵🇾", "confederation": "CONMEBOL"},
    {"name": "Portugal", "code": "POR", "flag": "🇵🇹", "confederation": "UEFA"},
    {"name": "Qatar", "code": "QAT", "flag": "🇶🇦", "confederation": "AFC"},
    {"name": "Saudi Arabia", "code": "KSA", "flag": "🇸🇦", "confederation": "AFC"},
    {"name": "Scotland", "code": "SCO", "flag": "🏴", "confederation": "UEFA"},
    {"name": "Senegal", "code": "SEN", "flag": "🇸🇳", "confederation": "CAF"},
    {"name": "South Africa", "code": "RSA", "flag": "🇿🇦", "confederation": "CAF"},
    {"name": "Spain", "code": "ESP", "flag": "🇪🇸", "confederation": "UEFA"},
    {"name": "Sweden", "code": "SWE", "flag": "🇸🇪", "confederation": "UEFA"},
    {"name": "Switzerland", "code": "SUI", "flag": "🇨🇭", "confederation": "UEFA"},
    {"name": "Tunisia", "code": "TUN", "flag": "🇹🇳", "confederation": "CAF"},
    {"name": "Turkiye", "code": "TUR", "flag": "🇹🇷", "confederation": "UEFA"},
    {"name": "USA", "code": "USA", "flag": "🇺🇸", "confederation": "CONCACAF"},
    {"name": "Uruguay", "code": "URU", "flag": "🇺🇾", "confederation": "CONMEBOL"},
    {"name": "Uzbekistan", "code": "UZB", "flag": "🇺🇿", "confederation": "AFC"},
]

TEAM_LOOKUP = {team["name"]: team for team in QUALIFIED_TEAMS}

TEAM_NAME_ALIASES = {
    "United States": "USA",
    "Turkey": "Turkiye",
    "Republic of Korea": "Korea Republic",
    "South Korea": "Korea Republic",
    "Iran": "IR Iran",
    "Ivory Coast": "Cote d'Ivoire",
    "Cape Verde": "Cabo Verde",
    "DR Congo": "Congo DR",
}

MVP_PLAYER_OPTIONS = [
    {"name": "Riyad Mahrez", "team": "Algeria", "position": "Forward"},
    {"name": "Lautaro Martinez", "team": "Argentina", "position": "Forward"},
    {"name": "Julian Alvarez", "team": "Argentina", "position": "Forward"},
    {"name": "Mat Ryan", "team": "Australia", "position": "Goalkeeper"},
    {"name": "Marcel Sabitzer", "team": "Austria", "position": "Midfielder"},
    {"name": "Kevin De Bruyne", "team": "Belgium", "position": "Midfielder"},
    {"name": "Edin Dzeko", "team": "Bosnia and Herzegovina", "position": "Forward"},
    {"name": "Vinicius Junior", "team": "Brazil", "position": "Forward"},
    {"name": "Rodrygo", "team": "Brazil", "position": "Forward"},
    {"name": "Ryan Mendes", "team": "Cabo Verde", "position": "Forward"},
    {"name": "Alphonso Davies", "team": "Canada", "position": "Defender"},
    {"name": "Jonathan David", "team": "Canada", "position": "Forward"},
    {"name": "Luis Diaz", "team": "Colombia", "position": "Forward"},
    {"name": "Yoane Wissa", "team": "Congo DR", "position": "Forward"},
    {"name": "Luka Modric", "team": "Croatia", "position": "Midfielder"},
    {"name": "Leandro Bacuna", "team": "Curacao", "position": "Midfielder"},
    {"name": "Patrik Schick", "team": "Czechia", "position": "Forward"},
    {"name": "Sebastien Haller", "team": "Cote d'Ivoire", "position": "Forward"},
    {"name": "Moises Caicedo", "team": "Ecuador", "position": "Midfielder"},
    {"name": "Mohamed Salah", "team": "Egypt", "position": "Forward"},
    {"name": "Jude Bellingham", "team": "England", "position": "Midfielder"},
    {"name": "Harry Kane", "team": "England", "position": "Forward"},
    {"name": "Kylian Mbappe", "team": "France", "position": "Forward"},
    {"name": "Aurelien Tchouameni", "team": "France", "position": "Midfielder"},
    {"name": "Jamal Musiala", "team": "Germany", "position": "Midfielder"},
    {"name": "Florian Wirtz", "team": "Germany", "position": "Midfielder"},
    {"name": "Mohammed Kudus", "team": "Ghana", "position": "Forward"},
    {"name": "Duckens Nazon", "team": "Haiti", "position": "Forward"},
    {"name": "Mehdi Taremi", "team": "IR Iran", "position": "Forward"},
    {"name": "Ali Jasim", "team": "Iraq", "position": "Forward"},
    {"name": "Takefusa Kubo", "team": "Japan", "position": "Forward"},
    {"name": "Kaoru Mitoma", "team": "Japan", "position": "Forward"},
    {"name": "Musa Al-Taamari", "team": "Jordan", "position": "Forward"},
    {"name": "Heung-min Son", "team": "Korea Republic", "position": "Forward"},
    {"name": "Hwang Hee-chan", "team": "Korea Republic", "position": "Forward"},
    {"name": "Santiago Gimenez", "team": "Mexico", "position": "Forward"},
    {"name": "Edson Alvarez", "team": "Mexico", "position": "Midfielder"},
    {"name": "Achraf Hakimi", "team": "Morocco", "position": "Defender"},
    {"name": "Sofyan Amrabat", "team": "Morocco", "position": "Midfielder"},
    {"name": "Xavi Simons", "team": "Netherlands", "position": "Midfielder"},
    {"name": "Virgil van Dijk", "team": "Netherlands", "position": "Defender"},
    {"name": "Chris Wood", "team": "New Zealand", "position": "Forward"},
    {"name": "Erling Haaland", "team": "Norway", "position": "Forward"},
    {"name": "Martin Odegaard", "team": "Norway", "position": "Midfielder"},
    {"name": "Adalberto Carrasquilla", "team": "Panama", "position": "Midfielder"},
    {"name": "Miguel Almiron", "team": "Paraguay", "position": "Forward"},
    {"name": "Bruno Fernandes", "team": "Portugal", "position": "Midfielder"},
    {"name": "Rafael Leao", "team": "Portugal", "position": "Forward"},
    {"name": "Akram Afif", "team": "Qatar", "position": "Forward"},
    {"name": "Salem Al-Dawsari", "team": "Saudi Arabia", "position": "Forward"},
    {"name": "Scott McTominay", "team": "Scotland", "position": "Midfielder"},
    {"name": "Che Adams", "team": "Scotland", "position": "Forward"},
    {"name": "Sadio Mane", "team": "Senegal", "position": "Forward"},
    {"name": "Ronwen Williams", "team": "South Africa", "position": "Goalkeeper"},
    {"name": "Lamine Yamal", "team": "Spain", "position": "Forward"},
    {"name": "Rodri", "team": "Spain", "position": "Midfielder"},
    {"name": "Alexander Isak", "team": "Sweden", "position": "Forward"},
    {"name": "Viktor Gyokeres", "team": "Sweden", "position": "Forward"},
    {"name": "Granit Xhaka", "team": "Switzerland", "position": "Midfielder"},
    {"name": "Youssef Msakni", "team": "Tunisia", "position": "Forward"},
    {"name": "Hakan Calhanoglu", "team": "Turkiye", "position": "Midfielder"},
    {"name": "Christian Pulisic", "team": "USA", "position": "Forward"},
    {"name": "Weston McKennie", "team": "USA", "position": "Midfielder"},
    {"name": "Federico Valverde", "team": "Uruguay", "position": "Midfielder"},
    {"name": "Darwin Nunez", "team": "Uruguay", "position": "Forward"},
    {"name": "Eldor Shomurodov", "team": "Uzbekistan", "position": "Forward"},
]

SEEDED_MATCHES = [
    {
        "team_a": "Czechia",
        "team_b": "Mexico",
        "stage": "Group A",
        "venue": "Mexico City Stadium",
        "kickoff_time": datetime(2026, 6, 11, 20, 0),
    },
    {
        "team_a": "South Africa",
        "team_b": "Korea Republic",
        "stage": "Group A",
        "venue": "Estadio Monterrey",
        "kickoff_time": datetime(2026, 6, 12, 19, 0),
    },
    {
        "team_a": "Switzerland",
        "team_b": "Canada",
        "stage": "Group B",
        "venue": "BC Place Vancouver",
        "kickoff_time": datetime(2026, 6, 12, 22, 0),
    },
    {
        "team_a": "Bosnia and Herzegovina",
        "team_b": "Qatar",
        "stage": "Group B",
        "venue": "Seattle Stadium",
        "kickoff_time": datetime(2026, 6, 13, 1, 0),
    },
    {
        "team_a": "Scotland",
        "team_b": "Brazil",
        "stage": "Group C",
        "venue": "Miami Stadium",
        "kickoff_time": datetime(2026, 6, 13, 20, 0),
    },
    {
        "team_a": "Morocco",
        "team_b": "Haiti",
        "stage": "Group C",
        "venue": "Atlanta Stadium",
        "kickoff_time": datetime(2026, 6, 13, 23, 0),
    },
    {
        "team_a": "Argentina",
        "team_b": "Curacao",
        "stage": "Featured Fixture",
        "venue": "MetLife Stadium",
        "kickoff_time": datetime(2026, 6, 14, 2, 0),
    },
    {
        "team_a": "Germany",
        "team_b": "Tunisia",
        "stage": "Featured Fixture",
        "venue": "Philadelphia Stadium",
        "kickoff_time": datetime(2026, 6, 14, 19, 0),
    },
    {
        "team_a": "England",
        "team_b": "Japan",
        "stage": "Featured Fixture",
        "venue": "Los Angeles Stadium",
        "kickoff_time": datetime(2026, 6, 14, 22, 0),
    },
    {
        "team_a": "France",
        "team_b": "Panama",
        "stage": "Featured Fixture",
        "venue": "Houston Stadium",
        "kickoff_time": datetime(2026, 6, 15, 1, 0),
    },
    {
        "team_a": "Portugal",
        "team_b": "USA",
        "stage": "Featured Fixture",
        "venue": "Dallas Stadium",
        "kickoff_time": datetime(2026, 6, 15, 20, 0),
    },
    {
        "team_a": "Spain",
        "team_b": "Uruguay",
        "stage": "Featured Fixture",
        "venue": "San Francisco Bay Area Stadium",
        "kickoff_time": datetime(2026, 6, 15, 23, 0),
    },
]


def normalize_team_name(team_name):
    clean_name = TEAM_NAME_ALIASES.get(team_name, team_name)
    return clean_name


def team_choices():
    return sorted(QUALIFIED_TEAMS, key=lambda team: team["name"])


def seed_matches_if_empty():
    if Match.query.count() > 0:
        return

    for item in SEEDED_MATCHES:
        db.session.add(
            Match(
                team_a=item["team_a"],
                team_b=item["team_b"],
                stage=item["stage"],
                venue=item["venue"],
                kickoff_time=item["kickoff_time"],
                is_locked=False,
            )
        )

    db.session.commit()

