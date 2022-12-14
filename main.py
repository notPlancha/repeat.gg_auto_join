import httpx

from config import userGameRegionId, refreshToken, api_key

# headers for get requests are needed it seems
headers = {
    'authority': 'www.repeat.gg',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-GB,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}

# TODO implement it later
# The user Game Region Id can be get with https://www.repeat.gg/api/user/game_regions/v1?userHandle={your handle}, the others I'm sure sure yet
# but it's foundable with a little bit of exploring through the network tab


if __name__ == "__main__":

    with httpx.Client(http2=True, timeout=60, headers=headers) as client:

        r2 = client.get("https://www.repeat.gg/tournaments", headers=headers)
        print("posting account")
        tokens = client.post(url=r"https://securetoken.googleapis.com/v1/token",
                             params={
                                 "key": api_key,
                                 "grant_type": "refresh_token",
                                 "refresh_token": refreshToken
                             })
        tokens.raise_for_status()
        tokens = tokens.json()
        id_token = tokens["id_token"]
        account = client.post(url=r'https://identitytoolkit.googleapis.com/v1/accounts:lookup',
                              params={
                                  "idToken": id_token,
                                  "key": api_key,
                              })
        account.raise_for_status()
        account = account.json()
        print("account from token:", account["users"][0]["displayName"])
        print("getting tournaments")
        r = client.get(url=r'https://www.repeat.gg/api/tournaments/v1?filters={"gameKey":"league_of_legends"}',)
        #r.raise_for_status()
        #tournaments = r.json()["tournaments"]
        print("got tournaments")
        gotInList = []
        headers.update({
            "authorization": "Bearer " + id_token
        })
        print("posting tournaments")
        for tour in [{
            "entry_fee": 0,
            "id": "f81b94cf-3b25-422a-953c-a633359c691c"
        }]:
            if tour["entry_fee"] == 0:
                r = client.post(
                    url="https://www.repeat.gg/sp-tournament/enter/" + tour["id"],
                    headers=headers,
                    data={
                        "userGameRegionId": userGameRegionId
                    },
                )
                if r.status_code == 200:
                    print("got in tour ", tour["name"])
                    gotInList.append(tour)
                elif r.status_code == 400:
                    try:
                        print(
                            f"Skipping '{tour['name']}'; 400: {r.json()['result']}; https://www.repeat.gg/league-of-legends/tournaments/{tour['id']}")
                    except KeyError:
                        r.raise_for_status()
                else:
                    r.raise_for_status()
            else:
                print("Skipping '", tour["name"], "'; entry fee is ", str(tour["entry_fee"]),
                      ";https://www.repeat.gg/league-of-legends/tournaments/", tour["id"])

        print("finished")
