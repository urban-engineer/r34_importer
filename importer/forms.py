from django import forms

import importer.models


class PostForm(forms.Form):
    post_id = forms.IntegerField(label="Ingest Post")


class BulkPostForm(forms.Form):
    posts = forms.FileField()


class CategoryTagEditForm(forms.Form):
    pass
