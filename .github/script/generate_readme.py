import re
from dataclasses import dataclass
from random import SystemRandom

from requests import get as req_get
from requests import head as req_head
from bs4 import BeautifulSoup


@dataclass(frozen=True, slots=True)
class Constants:
    """
    MovieCoverConstants
    -------------
    """
    main_url: str = "https://letterboxd.com/moonD4rk/films/"
    size_in_path: str = '-0-460-0-690-crop'
    name_split_pattern = re.compile(r"[\w']+")
    start_comment: str = '<!--START_SECTION:movie_cover-->'
    end_comment: str = '<!--END_SECTION:movie_cover-->'
    block_pattern: str = f'{start_comment}[\\s\\S]+{end_comment}'


def fetch_all_urls() -> tuple[str, str, str]:
    """
    return image url, and image title.
    """
    content = req_get(consts.main_url).content
    soup = BeautifulSoup(content, features="lxml")
    div_list = soup.find_all('div', attrs={
        "class": "film-poster"
    })
    urls = []
    for i in div_list:
        film_id = i.attrs["data-film-id"]
        ajax_link = i.attrs["data-target-link"]
        img = i.find("img")
        film_name = img.attrs["alt"]
        urls.append((film_name, film_id, ajax_link))
    return urls


def cover_url(index, film_name, film_id):
    s = "https://a.ltrbxd.com/resized/film-poster/{}-{}{}.jpg"
    id = "{}/{}".format("/".join(list(film_id)), film_id)
    name = "-".join(consts.name_split_pattern.findall(film_name)).lower()
    return index, s.format(id, name, consts.size_in_path)


def image_url_with_ajax(index: int, target_link: str):
    s = "https://letterboxd.com/ajax/poster{}std/70x105/".format(target_link)
    r = req_get(s)
    soup = BeautifulSoup(r.content, features="lxml")
    img = soup.find("img", attrs={
        "class": "image"
    })
    link = img.attrs["src"]
    return index, link.replace("-0-70-0-105-crop", consts.size_in_path)


def is_url_exist(url):
    return req_head(url=url[1]).ok


def new_img(url: str):
    return f'<img align="right" src="{url}" width="242" height="340" alt="letter-movie-cover">'


# fetch_image()
if __name__ == '__main__':
    consts = Constants()
    rand = SystemRandom()

    print("download image...")
    fetched_urls: list[tuple[str, str, str]] = fetch_all_urls()
    urls: list[tuple[int, str]] = [cover_url(i, v[0], v[1]) for i, v in enumerate(fetched_urls)]
    url: tuple[int, str] = rand.choice(urls)
    if not is_url_exist(url):
        url: tuple[int, str] = image_url_with_ajax(url[0], fetched_urls[url[0]][2])

    print("read old readme...")
    with open("../../readme.md", "r") as old_readme:
        content = old_readme.read()

    new_readme = re.sub(
        pattern=consts.block_pattern,
        repl=f'{consts.start_comment}\n{new_img(url[1])}\n{consts.end_comment}',
        string=content
    )

    print("write to new readme...")
    with open("../../readme.md", "w+") as f:
        f.write(new_readme)

    print("finished!")
