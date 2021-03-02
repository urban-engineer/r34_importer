import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

import importer.models
import importer.forms

from utils import config
from utils import requests_handler


# View classes
class PostListView(generic.ListView):
    model = importer.models.Post
    template_name = "importer/posts/posts.html"

    def get_queryset(self):
        return importer.models.Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shimmie_link"] = config.load_shimmie_config()["link"]
        return context


class UnimportedPostListView(generic.ListView):
    model = importer.models.Post
    template_name = "importer/posts/unimported_posts.html"

    def get_queryset(self):
        return importer.models.Post.objects.filter(imported=False)


class TagListView(generic.ListView):
    model = importer.models.Tag
    template_name = "importer/tags/all_tags.html"


########################################################################################################################
# Actual Views
########################################################################################################################
def index(request):
    return render(request, "importer/index.html")


########################################################################################################################
# Post views
########################################################################################################################
def posts_index(request):
    if request.method == "POST":
        form = importer.forms.PostForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('importer:posts-detail', args=(request.POST["post_id"],)))
    return render(request, "importer/posts/index.html", {"form": importer.forms.PostForm()})


def ingest_from_ids(request):
    if request.method == "POST":
        new_posts = request.POST["PostList"].split()
        for post in new_posts:
            importer.models.get_or_create_post(post)
        return HttpResponseRedirect(reverse("importer:posts-unimported"))
    return render(request, "importer/posts/bulk_import.html")


def detail(request, post_id):
    post = importer.models.get_or_create_post(post_id)
    height_ratio = min(int(post.sample_height), 900) / float(post.sample_height)
    ignored_tags = [str(x) for x in importer.models.Tag.objects.filter(auto_deny=True).all()]
    possible_tags = [importer.models.get_or_create_tag(x) for x in post.tags if str(x) not in ignored_tags]

    context = {
        "post": post,
        "tags": possible_tags,
        "sample_height": float(post.sample_height) * height_ratio,
        "sample_width": float(post.sample_width) * height_ratio,
        "shimmie_link": config.load_shimmie_config()["link"]
    }

    if post.imported:
        return render(request, "importer/posts/detail.html", context)
    else:
        return render(request, "importer/posts/detail_importable.html", context)


def import_to_shimmie(request, post_id):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("importer:posts-detail", args=(post_id,)))

    post = get_object_or_404(importer.models.Post, post_id=post_id)
    post_media = requests_handler.get_url(post.file_url).content
    if "content=" in str(post_media):
        return HttpResponseRedirect(request, reverse("importer:posts-fix"))

    try:
        selected_tags = request.POST.getlist("selected_tags")
    except KeyError:
        return HttpResponse("Could not get selected tags from post [{}]".format(post_id))

    if not selected_tags:
        selected_tags = [str(importer.models.get_or_create_tag("metadata:tagme"))] + post.tags

    shimmie_config = config.load_shimmie_config()
    data = {
        "login": shimmie_config["login"],
        "password": shimmie_config["password"],
        "tags": " ".join(selected_tags),
        "source": post.source_url
    }
    shimmie_request = requests_handler.send_post_with_file(
        "{}/api/danbooru/add_post".format(shimmie_config["link"]), data, file=post_media, errors_okay=True
    )

    if shimmie_request.status_code != 200:
        danbooru_error = shimmie_request.headers.get("X-Danbooru-Errors", None)
        if not danbooru_error:
            raise RuntimeError("Something broke during upload, returned code [{}]".format(shimmie_request.status_code))
        elif danbooru_error == "duplicate":
            pass
        if danbooru_error == "authentication error":
            raise RuntimeError("Authentication failed")
        elif danbooru_error == "fopen read error":
            raise RuntimeError("Unable to download url provided (can this happen?")
        elif danbooru_error == "no input files":
            raise FileNotFoundError("No files provided to upload")
        elif danbooru_error == "md5 mismatch":
            raise RuntimeError("Downloaded file does not match file uploaded to Shimmie")
        elif danbooru_error.startswith("exception - "):
            raise RuntimeError("Unknown error when uploading: [{}]".format(danbooru_error))

    shimmie_link = shimmie_request.headers.get("X-Danbooru-Location", None)
    if not shimmie_link or shimmie_link.endswith("post/view"):
        raise RuntimeError("Could not get valid link from Shimmie, something went wrong")

    post.imported = True
    post.imported_tags = selected_tags
    post.import_timestamp = datetime.datetime.timestamp(datetime.datetime.now())
    post.shimmie_id = shimmie_link.split("post/view/")[1]
    post.save()

    context = {
        "post": post,
        "shimmie_link": shimmie_link,
        "imported_tags": selected_tags,
    }
    return render(request, "importer/posts/import_success.html", context)


def fix_posts(request):
    posts_to_fix = importer.models.Post.objects.filter(imported=False).all()
    fixed_posts = []
    for x in range(len(posts_to_fix)):
        if posts_to_fix[x].fix_broken_links():
            fixed_posts.append(posts_to_fix[x])

    context = {
        "fixed_posts": fixed_posts
    }
    return render(request, "importer/posts/fixed.html", context)


########################################################################################################################
# Tags Views
########################################################################################################################
def tags_index(request):
    all_tags = importer.models.Tag.objects.all()
    categories = []
    for category in importer.models.Tag.CATEGORY_CHOICES:
        categories.append((category[0], len(list(all_tags.filter(tag_category=category[0])))))

    context = {
        "categories": categories,
        "total_number_of_tags": len(all_tags)
    }
    return render(request, "importer/tags/index.html", context)


def category_tags(request, category):
    context = {
        "tags": importer.models.Tag.objects.filter(tag_category=category),
        "category": category
    }
    return render(request, "importer/tags/category.html", context)


def category_tags_edit(request, category):
    if request.method == "GET":
        context = {
            "tags": importer.models.Tag.objects.filter(tag_category=category),
            "category": category
        }
        return render(request, "importer/tags/category_edit.html", context)
    elif request.method == "POST":
        form = importer.forms.CategoryTagEditForm(request.POST)
        if form.is_valid():
            if request.POST["action"] == "Update":
                tags_in_category = [importer.models.Tag.objects.get(id=int(x)) for x in request.POST.getlist("tags")]
                denied_tags = [importer.models.Tag.objects.get(id=int(x)) for x in request.POST.getlist("denies")]
                approved_tags = [importer.models.Tag.objects.get(id=int(x)) for x in request.POST.getlist("approves")]

                for x in range(len(tags_in_category)):
                    changes = False
                    active_tag = tags_in_category[x]

                    if active_tag.tag_notes != request.POST.getlist("notes")[x]:
                        active_tag.tag_notes = request.POST.getlist("notes")[x]
                        changes = True
                    if active_tag in denied_tags:
                        active_tag.auto_approve = False
                        active_tag.auto_deny = True
                        changes = True
                    elif active_tag in approved_tags:
                        active_tag.auto_approve = True
                        active_tag.auto_deny = False
                        changes = True

                    if changes:
                        tags_in_category[x].save()
    return HttpResponseRedirect(reverse("importer:tags-category", args=(category, )))
