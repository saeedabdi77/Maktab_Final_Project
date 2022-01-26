from django.urls import path, include
from .views import *

urlpatterns = [
    path('', SearchPageView.as_view(), name="search"),
    path('home/', Home.as_view(), name="home"),
    path('categories/', CategoryList.as_view(), name="category"),
    path('categories/<str:title>/', category_detail, name="category-detail"),
    path('categories/edit/<str:title>/', edit_category, name="edit-category"),
    path('categories/delete/<str:title>/', delete_category, name="delete-category"),
    path('add-category/', AddCategory.as_view(), name="add-category"),
    path('tags/', TagList.as_view(), name="tags"),
    path('tags/<str:name>/', tag_detail, name="tag-detail"),
    path('tags/edit/<str:name>/', edit_tag, name="edit-tag"),
    path('tags/delete/<str:name>/', delete_tag, name="delete-tag"),
    path('add-tag/', AddTag.as_view(), name="add-tag"),
    path('create-post/', CreatePost.as_view(), name="create-post"),
    path('update-draft-post/<slug:slug>/', edit_draft_post, name="update-draft-post"),
    path('update-published-post/<slug:slug>/', edit_published_post, name="update-published-post"),
    path('delete-post/<slug:slug>/', delete_post, name="delete-post"),
    path('my-posts/', MyPosts.as_view(), name="my-posts"),
    path('post-detail/<slug:slug>/', PostDetail.as_view(), name="post-detail"),
    path('contact-us/', get_message, name='get-message'),
    path('thanks-for-submission/', Submission.as_view()),
]
