import json
import re
from typing import List


class CandidateUser:
    def __init__(self, rest_id: str, name: str, screen_name: str, bsky_handle_candidate: List[str]):
        self.rest_id = rest_id
        self.name = name
        self.screen_name = screen_name
        self.bsky_handle_candidate = bsky_handle_candidate


def parse_description(description: str, entities: dict) -> List[str]:
    if description is None:
        return []

    # match all t.co urls followed by possible marks for bluesky handles
    url_candidates = map(
        lambda x: re.findall(x+".{0,6}https?:\\/\\/t.co[^\\s]+", description),
        [
            "bsky",
            "🦋",
            "bluesky",
            "BSKY",
            "BlueSky",
            "BLUESKY",
        ]
    )
    url_candidates = filter(lambda x: len(x) > 0, url_candidates)

    # record the corresponding t.co urls
    handle_url_candidates: List[str] = []
    for matches in url_candidates:
        for match in matches:
            url_identifier = match.split("https://t.co/")[1]
            handle_url_candidates.append("https://t.co/"+url_identifier)

    if entities is None:
        return []
    entities_description = entities.get('description')
    if entities_description is None:
        return []

    # find the corresponding expanded urls and return them
    urls = entities_description.get('urls')
    handle_candidates: List[str] = []
    for url in urls:
        expanded_url: str = url.get('expanded_url')
        url: str = url.get('url')
        if url is not None:
            for candidate_url in handle_url_candidates:
                if url == candidate_url:
                    handle_candidates.append(expanded_url)

    handle_candidates: List[str] = list(
        filter(lambda x: (x is not None), handle_candidates))
    handle_candidates: List[str] = list(map(lambda x: x.replace(
        "http://", "").replace("https://", ""), handle_candidates))
    return handle_candidates

# collect all *.bsky.* urls in profile


def parse_entities_urls(entities: dict) -> List[str]:
    if entities is None:
        return []
    url = entities.get('url')
    if url is None:
        return []
    urls: List[str] = entities.get('urls')
    if urls is None:
        return []
    url_list: List[str] = map(lambda x: x.get('expanded_url'), urls)
    url_list: List[str] = list(filter(lambda x: (x is not None)
                                      and (x.find("bsky") >= 0), url_list))
    url_list: List[str] = list(map(lambda x: x.replace(
        "http://", "").replace("https://", ""), url_list))
    return url_list


def parse_name(input: str) -> List[str]:
    if input is None:
        return []
    # all url-looking stuff followed after 🦋
    matches1 = re.findall("🦋[ ]?[a-zA-Z0-9\.\-^\\s]+", input)
    # url-looking stuff that includes '.bsky.' followed after @
    matches2 = re.findall("@[ ]?[a-zA-Z0-9\-]+\.bsky\.[a-zA-Z0-9\-]+", input)
    matches = list(map(
        lambda x: x.replace("🦋", "").replace(
            "@", "").replace("http://", "").replace("https://", "").strip(),
        matches1+matches2
    ))
    return matches


def parse_json(input: str) -> List[CandidateUser]:
    list_following = json.loads(input)
    ls = []
    for following in list_following:
        rest_id = following.get('rest_id')
        legacy = following.get('legacy')
        if legacy is None:
            continue
        name: str = legacy.get('name')
        screen_name: str = legacy.get('screen_name')
        description: str = legacy.get('description')
        entities = legacy.get('entities')
        if entities is not None:
            candidates_from_description = parse_description(
                description, entities)
            candidates_from_url = parse_entities_urls(entities)
            candidates_from_name = parse_name(name)
            all_candidates = list(
                set(
                    candidates_from_description+candidates_from_url+candidates_from_name
                )
            )
            ls.append(
                CandidateUser(
                    rest_id=rest_id,
                    name=name,
                    screen_name=screen_name,
                    bsky_handle_candidate=all_candidates
                )
            )
    return ls
