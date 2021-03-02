from django.urls import path

from . import views

app_name = "importer"
urlpatterns = [
    path('', views.index, name='index'),

    # Posts
    path('posts/', views.posts_index, name='posts-index'),
    path('posts/all/', views.PostListView.as_view(), name='posts-all'),
    path('posts/ingest/', views.ingest_from_ids, name='posts-ingest-ids'),
    path('posts/unimported/', views.UnimportedPostListView.as_view(), name='posts-unimported'),
    path('posts/<int:post_id>/', views.detail, name='posts-detail'),

    # Posts - you don't really "go" to these pages, they get POST'd to
    path('posts/<int:post_id>/import/', views.import_to_shimmie, name='posts-detail-import'),
    path('posts/fix/', views.fix_posts, name='posts-fix'),

    # Tags
    path('tags/', views.tags_index, name='tags-index'),
    path('tags/all/', views.TagListView.as_view(), name='tags'),
    path('tags/<str:category>/', views.category_tags, name='tags-category'),
    path('tags/<str:category>/edit', views.category_tags_edit, name='tags-category-edit'),
]
