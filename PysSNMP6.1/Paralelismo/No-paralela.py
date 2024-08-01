import requests
import time

all_characters = []

def get_characters(page: int = 1):
    url = f"https://rickandmortyapi.com/api/character/?page={page}"
    print(f"For url: {url}")

    response = requests.get(url)

    if(response.status_code == 200):
        characters = response.json()
        for character in characters['results']:
            all_characters.append(character)

        if(characters['info']['next']):
            page += 1
            return get_characters(page)
        else:
            return

if __name__ == '__main__':
    init = time.time()
    get_characters()
    print('Num results:')
    print(len(all_characters))
    print('Time ' + str(time.time() - init))