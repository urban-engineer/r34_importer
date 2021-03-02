import xml.etree.ElementTree as ElementTree


from bs4 import BeautifulSoup


from utils import requests_handler


RULE_34_BASE_URL = "https://rule34.xxx/index.php?page="
RULE_34_TAGS_URL = "{}tags&s=list&tags={}&sort=asc&order_by=updated".format(RULE_34_BASE_URL, "{}")
RULE_34_POST_URL = "{}post&s=view&id={}".format(RULE_34_BASE_URL, "{}")
RULE_34_API_URL = "{}dapi&s=post&q=index".format(RULE_34_BASE_URL)


def __fix_tag(tag: str) -> str:
    request = requests_handler.get_url(RULE_34_TAGS_URL.format(tag))
    soup = BeautifulSoup(request.text, "html.parser")
    tag_type = str(soup.find(class_="highlightable").find_all("tr")[1].find_all("td")[2].text.split(" (")[0])
    if ", " in tag_type:
        tag_type = tag_type.replace(", ambiguous", "")

    if ", " in tag_type:
        raise RuntimeError("Tag returned with additional type: [{}]".format(tag_type))

    if tag_type in ["general", "metadata"]:
        return tag
    elif tag_type == "character":
        return "character:{}".format(tag)
    elif tag_type == "artist":
        return "artist:{}".format(tag)
    elif tag_type == "copyright":
        return "series:{}".format(tag)
    else:
        raise RuntimeError("Type [{}] unknown!".format(tag_type))


def __process_post_xml(post_xml: ElementTree.Element) -> dict:
    return {
        "post_id": post_xml.attrib["id"],
        "tags": get_post_tags(post_xml.attrib["id"]),
        "file_url": post_xml.attrib["file_url"],
        "height": post_xml.attrib["height"],
        "width": post_xml.attrib["width"],
        "sample_url": post_xml.attrib["sample_url"],
        "sample_height": post_xml.attrib["sample_height"],
        "sample_width": post_xml.attrib["sample_width"],
        "preview_url": post_xml.attrib["preview_url"],
        "preview_height": post_xml.attrib["preview_height"],
        "preview_width": post_xml.attrib["preview_width"],
        "md5": post_xml.attrib["md5"],
        "source": post_xml.attrib.get("source", None),
        "parent_id": post_xml.attrib["parent_id"],
        "has_children": post_xml.attrib["has_children"],
    }


def get_post_tags(post_id: str) -> list:
    soup = BeautifulSoup(requests_handler.get_url("{}&id={}".format(RULE_34_POST_URL, post_id)).text, "html.parser")
    tags = []
    for tag in soup.find_all(class_="tag-type-copyright"):
        tags.append("series:{}".format(tag.a.text))
    for tag in soup.find_all(class_="tag-type-artist"):
        tags.append("artist:{}".format(tag.a.text))
    for tag in soup.find_all(class_="tag-type-character"):
        tags.append("character:{}".format(tag.a.text))
    for tag in soup.find_all(class_="tag-type-metadata"):
        tags.append("metadata:{}".format(tag.a.text))
    for tag in soup.find_all(class_="tag-type-general"):
        tags.append("{}".format(tag.a.text))

    return [x.replace(" ", "_") for x in tags]


def get_post_info(post_id: str) -> dict:
    root = ElementTree.fromstring(requests_handler.get_url("{}&id={}".format(RULE_34_API_URL, post_id)).text)
    if int(root.attrib["count"]) == 0:
        raise RuntimeError("Hash [{}] does not exist in rule34".format(post_id))
    elif int(root.attrib["count"]) > 1:
        raise RuntimeError("Found [{}] results for hash [{}]".format(int(root.attrib["count"]), post_id))
    else:
        post_info = __process_post_xml(root[0])

    return post_info


def get_post_children(post_id: str) -> list:
    root = ElementTree.fromstring(requests_handler.get_url("{}&tags=parent%3a{}".format(RULE_34_API_URL, post_id)).text)
    raw_posts = root.findall("post")

    post_ids = []
    for raw_post in raw_posts:
        if raw_post.attrib["id"] == post_id:
            continue
        post_ids.append(raw_post.attrib["id"])

    return post_ids


