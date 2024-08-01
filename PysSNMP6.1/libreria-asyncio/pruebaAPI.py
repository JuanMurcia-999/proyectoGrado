import aiohttp
import asyncio
import time

async def get_characters_by_page(session, page: int = 1):
    url = f"https://rickandmortyapi.com/api/character/?page={page}"
    print(f"For url: {url}")

    async with session.get(url) as response:
        if response.status == 200:
            characters = await response.json()
            return characters['info']['pages'], characters['results']
        else:
            raise Exception((await response.json())['error'])

async def get_characters_parallel():
    async with aiohttp.ClientSession() as session:
        pages, characters = await get_characters_by_page(session)
        all_characters = characters

        print(f'Num pages {pages}')

        tasks = []
        for page in range(2, pages + 1):
            tasks.append(get_characters_by_page(session, page))

        additional_characters = await asyncio.gather(*tasks)
        for page_characters in additional_characters:
            all_characters.extend(page_characters[1])  # Añadir solo los personajes de cada página

        return all_characters

if __name__ == '__main__':
    init = time.time()
    all_characters = asyncio.run(get_characters_parallel())
    print('Num results:')
    print(len(all_characters))
    print('Time ' + str(time.time() - init))
