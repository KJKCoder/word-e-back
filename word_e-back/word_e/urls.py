from django.contrib import admin
from django.urls import path
from word_e_back.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    
    path("model/search/<str:tag>/<int:page_num>/", 게시물View.as_view()),

    path("model/write/", 글작성View.as_view()),
    path("model/read/<int:모델_id>/", 글읽기View.as_view()),
    path("model/modify/<int:모델_id>/", 글수정View.as_view()),
    path("model/read/<int:모델_id>/import", 모델불러오기View.as_view()),
    
    path("login/", 로그인View.as_view()),
    path("signup/", 회원가입View.as_view()),
    path("checktoken/", 유효한토큰인지확인View.as_view()),
    
    path("user-import-model/<int:모델_id>/", 유저임포트모델View.as_view()),
    path("user-import-model-list/", 유저임포트모델_list_View.as_view()),\
    path("user-import-model-delete/<int:모델_id>/", 유저임포트모델_delete_View.as_view()),
    
    path('api/upload/<int:모델_id>', FileUploadView.as_view(), name='file-upload'),
    path('api/download/<int:모델_id>', DownloadMultipleFilesView.as_view()),
    
    path("demo/word", 단어유사도데모_View.as_view()),
    path("demo/sentence", 문장유사도데모_View.as_view()),
]

