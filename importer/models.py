import datetime

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


from utils import requests_handler
from utils import rule34_api


class Post(models.Model):
    # R34 Provided Tags
    post_id = models.IntegerField(default=-1)  # Use this to search in the R34 API
    tags = ArrayField(models.CharField(max_length=256))  # Tags from R34 API

    # Originally uploaded file information
    file_url = models.CharField(max_length=256, default=None)
    height = models.IntegerField(default=-1)
    width = models.IntegerField(default=-1)

    # Sample URL - reduced to make viewing easier (specifically used here for the detail view)
    sample_url = models.CharField(max_length=256, default=None, null=True)
    sample_height = models.IntegerField(default=-1)
    sample_width = models.IntegerField(default=-1)

    # Preview URL - displayed in the index / post listing
    preview_url = models.CharField(max_length=256, default=None, null=True)
    preview_height = models.IntegerField(default=-1)
    preview_width = models.IntegerField(default=-1)

    # Metadata about the post
    md5_hash = models.CharField(max_length=32, default="z" * 32)
    source_url = models.CharField(max_length=256, default=None)
    parent_id = models.IntegerField(default=-1, blank=True)
    has_children = models.BooleanField(default=False)

    # Importer specific fields
    imported = models.BooleanField(default=False)  # whether the post has been imported or not
    imported_tags = ArrayField(models.CharField(max_length=256), default=list)  # Tags actually imported to booru
    creation_timestamp = models.IntegerField(default=0)  # when the post was looked up
    import_timestamp = models.IntegerField(default=0)  # when the post was imported from r34 to booru
    shimmie_id = models.IntegerField(default=-1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return str(self.post_id)

    def get_post_url(self):
        return rule34_api.RULE_34_POST_URL.format(self.post_id)

    def get_api_url(self):
        return "{}&id={}".format(rule34_api.RULE_34_API_URL, self.post_id)

    def get_children(self) -> list:
        child_posts = []
        if self.has_children:
            for child in rule34_api.get_post_children(str(self.post_id)):
                child_posts.append(get_or_create_post(child))
        return child_posts

    def fix_broken_links(self) -> bool:
        media = requests_handler.get_url(self.file_url).content
        changed = False
        if "content=" in str(media):
            if self.file_url and "xxx//" not in self.file_url:
                self.file_url = self.file_url.replace("xxx", "xxx/")
                changed = True

            if self.sample_url and "xxx//" not in self.sample_url:
                self.sample_url = self.sample_url.replace("xxx", "xxx/")
                changed = True

            if self.preview_url and "xxx//" not in self.preview_url:
                self.preview_url = self.preview_url.replace("xxx", "xxx/")
                changed = True

            self.save()

        return changed


class Tag(models.Model):
    CATEGORY_COPYRIGHT = "COPYRIGHT"
    CATEGORY_CHARACTER = "CHARACTER"
    CATEGORY_ARTIST = "ARTIST"
    CATEGORY_METADATA = "METADATA"
    CATEGORY_GENERAL = "GENERAL"
    CATEGORY_CHOICES = [
        (CATEGORY_COPYRIGHT, "COPYRIGHT"),
        (CATEGORY_CHARACTER, "CHARACTER"),
        (CATEGORY_ARTIST, "ARTIST"),
        (CATEGORY_METADATA, "METADATA"),
        (CATEGORY_GENERAL, "GENERAL")
    ]

    # R34 attributes
    tag_name = models.CharField(max_length=256)  # tag you search
    tag_category = models.CharField(
        max_length=256, choices=CATEGORY_CHOICES, default=CATEGORY_GENERAL
    )  # Category the tag appears under in the tag bar

    # Importer attributes
    auto_deny = models.BooleanField(default=False)
    auto_approve = models.BooleanField(default=False)
    tag_notes = models.TextField(blank=True)
    import_timestamp = models.IntegerField(default=0)

    class Meta:
        ordering = ["tag_category", "tag_name"]

    def __str__(self):
        if self.tag_category == self.CATEGORY_COPYRIGHT:
            return "series:{}".format(self.tag_name)
        if self.tag_category == self.CATEGORY_ARTIST:
            return "artist:{}".format(self.tag_name)
        elif self.tag_category == self.CATEGORY_CHARACTER:
            return "character:{}".format(self.tag_name)
        elif self.tag_category == self.CATEGORY_METADATA:
            return "metadata:{}".format(self.tag_name)
        else:
            return "{}".format(self.tag_name)


def get_tag_category_from_name(tag_name: str) -> Tag.CATEGORY_CHOICES:
    if tag_name.startswith("series:"):
        return Tag.CATEGORY_COPYRIGHT
    elif tag_name.startswith("artist:"):
        return Tag.CATEGORY_ARTIST
    elif tag_name.startswith("character:"):
        return Tag.CATEGORY_CHARACTER
    elif tag_name.startswith("metadata:"):
        return Tag.CATEGORY_METADATA
    else:
        return Tag.CATEGORY_GENERAL


def get_true_tag_name(tag_name: str) -> Tag.CATEGORY_CHOICES:
    if tag_name.startswith(("series:", "artist:", "character:", "metadata:")):
        return ":".join(tag_name.split(":")[1:])
    else:
        return tag_name


def get_category_tags(category: Tag.CATEGORY_CHOICES) -> list:
    return Tag.objects.filter(tag_category=category).order_by("tag_name")


def get_or_create_tag(tag_name: str) -> Tag:
    """
    expects tag input to be of "<category>:<name>" or "<name>"

    :param tag_name: tag to check
    :return: Tag object of provided tag
    """
    category = get_tag_category_from_name(tag_name)
    tag_name = get_true_tag_name(tag_name)

    try:
        tag_object = Tag.objects.get(tag_name=tag_name, tag_category=category)
    except ObjectDoesNotExist:
        tag_object = Tag(
            tag_name=tag_name, tag_category=category,
            import_timestamp=datetime.datetime.timestamp(datetime.datetime.now())
        )
        tag_object.save()

    return tag_object


def get_or_create_post(post_id: str) -> Post:
    try:
        post = Post.objects.get(post_id=post_id)
    except ObjectDoesNotExist:
        post_info_raw = rule34_api.get_post_info(post_id)

        parent_id = post_info_raw["parent_id"]
        if not parent_id:
            parent_id = -1

        post = Post(
            post_id=post_id,
            tags=post_info_raw["tags"],
            file_url=post_info_raw["file_url"],
            height=post_info_raw["height"],
            width=post_info_raw["width"],
            sample_url=post_info_raw["sample_url"],
            sample_height=post_info_raw["sample_height"],
            sample_width=post_info_raw["sample_width"],
            preview_url=post_info_raw["preview_url"],
            preview_height=post_info_raw["preview_height"],
            preview_width=post_info_raw["preview_width"],
            md5_hash=post_info_raw["md5"],
            source_url=post_info_raw["source"],
            parent_id=parent_id,
            has_children=post_info_raw["has_children"].lower() == "true",
            creation_timestamp=datetime.datetime.timestamp(datetime.datetime.now()),
        )

        post.save()

    # post.fix_broken_links()
    return post
