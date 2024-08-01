import requests
import time

from threading import Thread

all_characters = []

def get_characters_by_page(page: int = 1):
    url = f"https://rickandmortyapi.com/api/character/?page={page}"
    print(f"For url: {url}")

    response = requests.get(url)

    if(response.status_code == 200):
        characters = response.json()
        for character in characters['results']:
            all_characters.append(character)

        return characters['info']['pages']

    raise Exception(response.json()['error'])

def get_characters_parallel():
    pages = get_characters_by_page()

    print(f'Num pages {pages}')

    limit_threads = 20

    request_threads = {}
    for page in range(2, (pages + 1)):

        if len(request_threads) >= limit_threads:

            check_request_threads = True

            while check_request_threads:
                request_threads = clean_old_request_threads(request_threads)
                if len(request_threads) >= limit_threads:
                    print('Wait 1 second')
                    time.sleep(1)
                else:
                    check_request_threads = False

        request_threads[page] = Thread(target=get_characters_by_page, kwargs={'page':page})
        print(request_threads)
        request_threads[page].start()


    while(True):
        request_threads = clean_old_request_threads(request_threads)

        if len(request_threads) < 1:
            break

def clean_old_request_threads(request_threads):

    for key, value in request_threads.copy().items():
        if not value.is_alive():
            del request_threads[key]

    return request_threads



if __name__ == '__main__':
    init = time.time()
    get_characters_parallel()
    print('Num results:')
    print(len(all_characters))
    print('Time ' + str(time.time() - init))

    