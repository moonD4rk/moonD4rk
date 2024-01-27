import re
import requests
from dataclasses import dataclass
from random import SystemRandom
from bs4 import BeautifulSoup


@dataclass(frozen=True, slots=True)
class Constants:
    def __init__(self):
        pass

    main_url: str = "https://letterboxd.com/moonD4rk/films/"
    size_in_path: str = '-0-460-0-690-crop'
    name_split_pattern = re.compile(r"[\w']+")
    start_comment: str = '<!--START_SECTION:movie_cover-->'
    end_comment: str = '<!--END_SECTION:movie_cover-->'
    block_pattern: str = f'{start_comment}[\\s\\S]+{end_comment}'
    readme_path: str = "../../README.md"
    img_template: str = "https://a.ltrbxd.com/resized/film-poster/{id}-{name}{size}.jpg"
    ajax_template: str = "https://letterboxd.com/ajax/poster{link}std/70x105/"


session = requests.Session()


def fetch_all_movies() -> list[tuple[str, str, str]]:
    response = session.get(Constants.main_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, features="lxml")
    div_list = soup.find_all('div', attrs={"class": "film-poster"})
    return [(img.attrs["alt"], i.attrs["data-film-id"], i.attrs["data-target-link"])
            for i in div_list if (img := i.find("img"))]


def generate_cover_url(film_name: str, film_id: str) -> str:
    id_path = "/".join(list(film_id)) + f"/{film_id}"
    name = "-".join(Constants.name_split_pattern.findall(film_name)).lower()
    return Constants.img_template.format(id=id_path, name=name, size=Constants.size_in_path)


def fetch_image_url_with_ajax(target_link: str) -> str:
    response = session.get(Constants.ajax_template.format(link=target_link))
    response.raise_for_status()

    soup = BeautifulSoup(response.content, features="lxml")
    img = soup.find("img", attrs={"class": "image"})
    if img and (src := img.attrs.get("src")):
        return src.replace("-0-70-0-105-crop", Constants.size_in_path)
    raise ValueError("Image source not found in AJAX response")


def is_url_exist(url: str) -> bool:
    return session.head(url).ok


def new_img_tag(url: str) -> str:
    return f'<img align="right" src="{url}" width="242" height="340" alt="letter-movie-cover">'


if __name__ == '__main__':
    consts = Constants()
    rand = SystemRandom()

    print("Downloading image...")
    movies = fetch_all_movies()
    movie_urls = [(i, generate_cover_url(name, film_id)) for i, (name, film_id, _) in enumerate(movies)]
    movie_url = rand.choice(movie_urls)

    if not is_url_exist(movie_url[1]):
        movie_url = (movie_url[0], fetch_image_url_with_ajax(movies[movie_url[0]][2]))

    print("Reading old README...")
    with open(Constants.readme_path, "r") as old_readme:
        content = old_readme.read()

    new_readme = re.sub(
        pattern=Constants.block_pattern,
        repl=f'{Constants.start_comment}\n{new_img_tag(movie_url[1])}\n{Constants.end_comment}',
        string=content
    )

    print("Writing to new README...")
    with open(Constants.readme_path, "w") as f:
        f.write(new_readme)

    print("Finished!")
