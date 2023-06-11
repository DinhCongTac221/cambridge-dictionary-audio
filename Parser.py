import bs4
import requests
from typing import Optional

DEFAULT_REQUESTS_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
LINK_PREFIX = "https://dictionary.cambridge.org"
    

def get_phonetics(
    header_block: Optional[bs4.Tag]):

    uk_audio_links: list[str] = []

    if header_block is None:
        return uk_audio_links

    audio_block = header_block.find_all("span", {"class": "daud"})

    for daud in audio_block:
        parent_class = [item.lower() for item in daud.parent.get("class")]
        audio_source = daud.find("source")
        if audio_source is None:
            continue
        audio_source_link = audio_source.get("src")
        if not audio_source_link:  # None or empty
            continue

        result_audio_link = f"{LINK_PREFIX}/{audio_source_link}"

        if "uk" in parent_class:
            uk_audio_links.append(result_audio_link)

    return uk_audio_links



def define(word, save_path,
           request_headers: Optional[dict]=None,  
           timeout:float=5.0):

    if request_headers is None:
        request_headers = DEFAULT_REQUESTS_HEADERS
    
    link = f"{LINK_PREFIX}/dictionary/english/{word}"

    page = requests.get(link, headers=request_headers, timeout=timeout)

    soup = bs4.BeautifulSoup(page.content, "html.parser")

    primal_block = soup.find_all("div", {'class': 'di-body'})

    ans = ""

    for dictionary_index in range(len(primal_block)):

        main_block = primal_block[dictionary_index].find_all("div", {"class": lambda x: "entry-body__el" in x if x is not None else False})

        main_block.extend(primal_block[dictionary_index].find_all("div", {"class": "pr dictionary"}))
        main_block.extend(primal_block[dictionary_index].find_all("div", {"class": "pv-block"}))
        main_block.extend(primal_block[dictionary_index].find_all("div", {"class": "pr idiom-block"}))

        for entity in main_block:
            header_block = entity.find("div", {"class": "dpos-h"})

            parsed_word_block = entity.find("h2", {"class": "headword"})
            
            if parsed_word_block is None:
                parsed_word_block = header_block.find("h2", {"class": "di-title"}) if header_block is not None else None
            if parsed_word_block is None:
                parsed_word_block = header_block.find("div", {"class": "di-title"}) if header_block is not None else None
            header_word = parsed_word_block.text if parsed_word_block is not None else ""

            uk_audio_links = get_phonetics(header_block)

            try:
                ans = uk_audio_links[0]

                page = requests.get(ans, headers=request_headers, timeout=timeout)


                with open(save_path,'wb') as f:
                    f.write(page.content)

                print('Succeful file downloaded to ' + save_path)

                return ans

                break

            except: pass

    return ans