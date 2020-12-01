import requests
import argparse
import datetime
import sys

WIN_RESULTS = ["win"]
DRAW_RESULTS = ["timevsinsufficient", "insufficient", "repetition", "stalemate", "agreed"]
LOSS_RESULTS = ["timeout", "resigned", "checkmated"]

parser = argparse.ArgumentParser(description='Head to head results of players on chess.com in the current month')
parser.add_argument('player_one', help='The first player')
parser.add_argument('player_two', help='The second player')
parser.add_argument('--timeframe', help='input timeframe you want to check in the format <year>/<month>-<year>/<month>, i.e. 2020/11-2020/12',
                    default=False)
parser.add_argument('--all', help='Get the entire match history of the two players', action='store_true')
parser.add_argument('--game_type', help="specify the game format you'd like to view results on.  Multiple can be specified in the format <game_type>,<game_type>,<etc>")

args = parser.parse_args()

if args.game_type:
    game_types = args.game_type.split(',')

username1 = args.player_one
username2 = args.player_two

try:
    game_records = requests.get(f'https://api.chess.com/pub/player/{username1}/games/archives/').json()['archives']
except KeyError:
    print(f"Error! Unable to access {args.player_one}'s games! Is their game history set to private?")
    sys.exit(1)


# create list of urls to read through based on args passed in
urls = []
if args.timeframe:
    start_date = args.timeframe.split('-')[0]
    end_date = args.timeframe.split('-')[1]

    for date in game_records:
        year = int(date.split('/')[7])
        month = int(date.split('/')[8])
        # the ending
        if year == int(end_date.split('/')[0]):
            if month < int(end_date.split('/')[1]):
                urls.append(date)
            elif month == int(end_date.split('/')[1]):
                urls.append(date)
                break
        elif year >= int(start_date.split('/')[0]):
            urls.append(date)
        else:
            break
    print('Urls for the requested timeframe have been collected, requesting information from api.chess.com')
    print('Warning: The chess.com api is slow, this could take some time')

elif args.all:
    urls = game_records
    print('Looking through players ENTIRE history to find complete win/draw/loss record')
    print('Warning: The chess.com api is slow, this could take some time')
else:
    # Get the current months records
    now = datetime.datetime.today()
    urls.append(f'https://api.chess.com/pub/player/{username1}/games/{now.year}/{now.month}')
    print("Getting player records for the current month.  If you'd like a different timeframe, use --timeframe or --all")
    print('Warning: The chess.com api is slow, this could take some time')

# read through data and figure out the users record against the other user
user1record = {"wins": 0, "draws": 0, "losses": 0}
for url in urls:
    data = requests.get(url)
    for game in data.json()['games']:
        if args.game_type:
            if game["time_class"].lower() not in game_types:
                continue
        result = ''
        if game['white']['username'] == username1 and game['black']['username'] == username2:
            # user1 played white
            result = game['white']['result']
        elif game['black']['username'] == username1 and game['white']['username'] == username2:
            # user1 played black
            result = game['black']['result']

        if result in WIN_RESULTS:
            user1record['wins'] += 1
        elif result in DRAW_RESULTS:
            user1record['draws'] += 1
        elif result in LOSS_RESULTS:
            user1record['losses'] += 1

# Make the print statement look nice
if not args.game_type:
    args.game_type = ''
else:
    args.game_type = args.game_type + ' '
print(f'\n{args.player_one} has the following {args.game_type}record against {args.player_two}:')
print(user1record)
# print(f'w/l = {user1record["wins"] / user1record["losses"]}')
