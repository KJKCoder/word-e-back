from rest_framework import serializers
from .models import *
from django.db import connection

base_db = "word_e_back_"


class 게시물Serializer(serializers.ModelSerializer):
    class Meta:
        model = 게시물
        fields = '__all__'


class 유저Serializer(serializers.ModelSerializer):
    class Meta:
        model = 유저
        fields = '__all__'


class 태그Serializer(serializers.ModelSerializer):
    class Meta:
        model = 태그모음
        fields = '__all__'


class 모델Serializer(serializers.ModelSerializer):
    class Meta:
        model = 모델
        fields = '__all__'


class 데이터셋Serializer(serializers.ModelSerializer):
    class Meta:
        model = 데이터셋
        fields = '__all__'


class 유저_import_모델Serializer(serializers.ModelSerializer):

    def get_user_import_relation(self, user_id):
            
        where_condition = f"WHERE A.유저_id='{user_id}'"

        sql = f"SELECT A.모델_id, 제목 as 모델이름\
                FROM {base_db}유저_import_모델 AS A JOIN {base_db}게시물 AS B ON A.모델_id = B.모델_id\
                {where_condition}\
                "
        with connection.cursor() as cursor:
            cursor.execute(sql)
            contents = cursor.fetchall()

        return contents
    
    def to_json(self, contents):
        return {
                "모델_id": [cur[0] for cur in contents],
                "모델이름": [cur[1] for cur in contents],
            }
    
    class Meta:
        model = 유저_import_모델
        fields = '__all__'


class 게시물태그필터Serializer(serializers.ModelSerializer):
    
    def filter_data(self, tag, post_num, page):

        if tag=="전체":
            where_condition = ""
        else:
            where_condition = f"WHERE 태그이름='{tag}'"

        sql = f"SELECT DISTINCT 제목, 닉네임, 수정일, 모델_id\
                FROM {base_db}유저 AS USER\
                JOIN ({base_db}게시물 JOIN {base_db}태그모음 USING(모델_id))\
                ON USER.id = 유저_id\
                {where_condition}\
                ORDER BY 수정일 DESC\
                LIMIT {post_num} OFFSET {(page-1)*post_num}"
        
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

        sql = f"SELECT COUNT(DISTINCT 모델_id)\
                FROM {base_db}유저 AS USER\
                JOIN ({base_db}게시물 JOIN {base_db}태그모음 USING(모델_id))\
                ON USER.id = 유저_id\
                {where_condition}\
                "
        with connection.cursor() as cursor:
            cursor.execute(sql)
            all_post_num = cursor.fetchone()

        return rows, all_post_num

    def to_representation(self, instance, all_post_num):
        return {
                "제목":[cur[0] for cur in instance],
                "작성자":[cur[1] for cur in instance],
                "최종수정일":[str(cur[2])[:11] for cur in instance],
                "모델_id":[cur[3] for cur in instance],
                "총글개수":all_post_num
            }


class 게시물태그보기Serializer(serializers.ModelSerializer):
    def get_post(self, post_id):
            
        where_condition = f"WHERE 모델_id='{post_id}'"

        sql = f"SELECT DISTINCT 모델_id, 제목, 닉네임, 작성일, 수정일, 글내용_모델, 글내용_데이터, 유저_id\
                FROM {base_db}유저 AS USER\
                JOIN ({base_db}게시물 JOIN {base_db}태그모음 USING(모델_id))\
                ON USER.id = 유저_id\
                {where_condition}\
                "
        with connection.cursor() as cursor:
            cursor.execute(sql)
            contents = cursor.fetchone()

        sql = f"SELECT DISTINCT 태그이름\
                FROM {base_db}유저 AS USER\
                JOIN ({base_db}게시물 JOIN {base_db}태그모음 USING(모델_id))\
                ON USER.id = 유저_id\
                {where_condition}\
                "
        with connection.cursor() as cursor:
            cursor.execute(sql)
            tags = cursor.fetchall()

        return contents, tuple(tag[0] for tag in tags)

    def to_representation(self, contents, tags):
        return {
                "모델_id": contents[0],
                "제목": contents[1],
                "작성자": contents[2],
                "작성일": str(contents[3])[:11],
                "수정일": str(contents[4])[:11],
                "글내용_모델": contents[5],
                "글내용_데이터": contents[6],
                "유저_id": contents[7],
                "태그": tags
            }
