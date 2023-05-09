from django.db import models

class 모델(models.Model):
    path = models.CharField(max_length=500, null=True)
    모델이름 = models.TextField(null=True)
    
    def __str__(self):
        return self.모델이름

class 유저(models.Model):
    닉네임 = models.CharField(max_length=10, unique=True)
    아이디 = models.CharField(max_length=45, unique=True)
    비밀번호 = models.CharField(max_length=45)
    가입날짜 = models.DateTimeField(auto_now_add=True)
    is_super = models.BooleanField(default=False)
    토큰 = models.CharField(max_length=300, null=True, unique=True)
    토큰생성시간 = models.DateTimeField(auto_now=True)


class 유저_import_모델(models.Model):
    유저 = models.ForeignKey(유저, on_delete=models.CASCADE)
    모델 = models.ForeignKey(모델, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.유저} - {self.모델}"


class 게시물(models.Model):
    모델 = models.OneToOneField(모델, on_delete=models.CASCADE, primary_key=True)
    유저 = models.ForeignKey(유저, on_delete=models.CASCADE)
    제목 = models.CharField(max_length=100)
    글내용_모델 = models.TextField(blank=True, null=True)
    글내용_데이터 = models.TextField(blank=True, null=True)
    작성일 = models.DateTimeField(auto_now_add=True)
    수정일 = models.DateTimeField(auto_now=True)
    
class 데이터셋(models.Model):
    모델 = models.ForeignKey(모델, on_delete=models.CASCADE)
    path = models.CharField(max_length=500, null=True)
    데이터 = models.TextField(null=True)


class 태그모음(models.Model):
    태그이름 = models.CharField(max_length=20)
    모델 = models.ForeignKey(게시물, on_delete=models.CASCADE)