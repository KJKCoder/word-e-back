from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .serializer import *
import re
import datetime
import shutil
import os


base_path = settings.MEDIA_ROOT




'''
로그인 관련-------------------------------------------------------------------------------------------------------------------------------
'''
def get_auth_user(request):
    try:
        token = request.data["access-token"]
        if token == None: return False

        user = 유저.objects.get(토큰=token)
        expire_time = timezone.now() + datetime.timedelta(0.1)

        if expire_time > user.토큰생성시간:
            return user
        else:
            return False

    except KeyError:
        return False

class 유효한토큰인지확인View(APIView):
    authentication_classes = ()
    def post(self, request):
        auth_user = get_auth_user(request)
        if auth_user:
            return Response({"닉네임":auth_user.닉네임, "유저_id":auth_user.id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': '허가된 사용자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)


from rest_framework_simplejwt.tokens import RefreshToken
class 로그인View(APIView):
    def post(self, request, *args, **kwargs):
        아이디 = request.data.get('아이디')
        비밀번호 = request.data.get('비밀번호')

        try:
            user = 유저.objects.get(아이디=아이디, 비밀번호=비밀번호)

            refresh = RefreshToken.for_user(user)
            token = refresh.access_token

            serializer = 유저Serializer(user, data={"토큰":str(token)}, partial=True)
            if serializer.is_valid():
                serializer.save()
            return Response({'access_token': str(token)})
        
        except:
            return Response({'error': 'Invalid credentials'}, status=401)

class 회원가입View(APIView):
    def post(self, request, *args, **kwargs):
        
        닉네임 = request.data.get('닉네임')
        아이디 = request.data.get('아이디')
        비밀번호 = request.data.get('비밀번호')

        serializer = 유저Serializer(data={"닉네임":닉네임, "아이디":아이디, "비밀번호":비밀번호})
        if serializer.is_valid():
            serializer.save()
            return Response({"state":True, "message":"User Created Success"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"state":False, "error":f"{list(serializer.errors.keys())[0]}이(가) 이미 존재합니다."}, status=status.HTTP_226_IM_USED)




'''
파일 업로드 / 다운로드 관련-------------------------------------------------------------------------------------------------------------------------------
'''
class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None, *args, **kwargs):

        model_id = kwargs["모델_id"]
        req_data_dict = request.data
        keys = req_data_dict.keys()

        print(req_data_dict)

        check_bool = False
        for key in keys:
            if "model" in key:
                check_bool = True; break
        
        if check_bool == False:
            Response("모델 파일은 적어도 하나가 존재해야 합니다.", status=status.HTTP_406_NOT_ACCEPTABLE)

        if model_id != 0:
            # 모델 수정
            auth_user = get_auth_user(request)
            author = 유저.objects.get(게시물=model_id)
            
            if auth_user != author:
                return Response("허가된 사용자가 아닙니다.", status=status.HTTP_401_UNAUTHORIZED)
            model_path = 모델.objects.get(id=model_id).path
            data_path = 데이터셋.objects.get(모델=model_id).path
            
            shutil.rmtree(base_path + model_path)
            shutil.rmtree(base_path + data_path)
            
        else:
            # 모델 추가
            auth_user = get_auth_user(request)

            if not auth_user:
                return Response("허가된 사용자가 아닙니다.", status=status.HTTP_401_UNAUTHORIZED)

            

            model_serializer = 모델Serializer(data={"모델이름":req_data_dict["name"], "path":"dummy"})
            if model_serializer.is_valid():
                model_instance = model_serializer.save()

            model_id = int(모델.objects.last().id)

            model_serializer = 모델Serializer(model_instance, data={"모델이름":req_data_dict["name"], "path":f"\\model_{model_id}\\"}, partial=True)
            if model_serializer.is_valid():
                model_instance = model_serializer.save()
            
            data_serializer = 데이터셋Serializer(data={"모델":model_instance.id, "path":f"\\data_{model_id}\\", "데이터":req_data_dict["name"]})
            if data_serializer.is_valid():
                data_serializer.save()

        models = []; datas = []
        for key in keys:
            if re.search("^model",key):
                models.append(req_data_dict[key])
            elif re.search("^data",key):
                datas.append(req_data_dict[key])
            else:
                continue

        fs = FileSystemStorage()

        file_urls = []
        for model in models:
            filename = fs.save(base_path + f"/model_{model_id}/" + model.name, model)
            file_url = fs.url(filename)
            file_urls.append(file_url)
        for data in datas:
            filename = fs.save(base_path + f"/data_{model_id}/" + data.name, data)
            file_url = fs.url(filename)
            file_urls.append(file_url)

        return Response({'모델_id': model_id}, status=status.HTTP_201_CREATED)

import zipfile
from django.http import FileResponse
class DownloadMultipleFilesView(APIView):
    def get(self, request, *args, **kwargs):
        model_id = kwargs["모델_id"]

        model_obj = 모델.objects.get(id=model_id)
        data_obj = 데이터셋.objects.get(모델=model_id)
        
        target_path_model = base_path + model_obj.path
        target_path_data = base_path + data_obj.path

        zip_file = f"model_and_data_{model_obj.id}.zip"
        zip_path = os.path.join(base_path, zip_file)

        with zipfile.ZipFile(zip_path, 'w') as zip:
            for file_name in os.listdir(target_path_model):
                file_path = os.path.join(target_path_model, file_name)
                zip.write(file_path, file_name)
            for file_name in os.listdir(target_path_data):
                file_path = os.path.join(target_path_data, file_name)
                zip.write(file_path, file_name)

        response = FileResponse(open(zip_path, 'rb'), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_file}"'

        return response




'''
게시물 태그 추가 삭제-------------------------------------------------------------------------------------------------------------------------------
'''
def add_tag(model_id, tags):
    tags = re.sub("[^\w,]","",tags).split(",")
    tags = [cur.strip() for cur in tags]

    for tag in tags:
        serializer = 태그Serializer(data={"태그이름":tag, "모델":model_id})
        if serializer.is_valid():
            serializer.save()

def delete_tag(model_id):
    tags = 태그모음.objects.filter(모델=model_id)

    for tag in tags:
        try:
            instance = 태그모음.objects.get(태그이름=tag.태그이름, 모델=model_id)
            instance.delete()
        except 태그모음.DoesNotExist:
            print('tag does not exist')
            pass




'''
모델 목록 보기-------------------------------------------------------------------------------------------------------------------------------
'''        
class 게시물View(APIView):
    def get(self, request, *args, **kwargs):
        tag = kwargs['tag']
        page_num = kwargs['page_num']
        post_num = 10

        serializer = 게시물태그필터Serializer()
        data, all_post_num = serializer.filter_data(tag, post_num, page_num)
        serialized_data = serializer.to_representation(data, all_post_num)
        
        if len(data) == 0:
            return Response("데이터가 없습니다", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serialized_data)
    



'''
모델 작성 / 수정-------------------------------------------------------------------------------------------------------------------------------
'''
class 글작성View(APIView):
    
    def get(self, request):
        auth_user = get_auth_user(request)
        if auth_user:
            return JsonResponse({"제목":"제목을 입력하세요"})
        else:
            return Response({'error': '허가된 사용자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def post(self, request, *args, **kwargs):
        
        auth_user = get_auth_user(request)

        if auth_user:

            data = request.data
            del data["access-token"]
 
            tags = data["태그"]
            del data["태그"]

            serializer = 게시물Serializer(data = data)

            if serializer.is_valid():
                serializer.save()
                add_tag(data["모델"], tags)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '허가된 사용자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)

class 글수정View(APIView):
    def post(self, request, *args, **kwargs):

        post_id = kwargs["모델_id"]

        serializers = 게시물태그보기Serializer()
        contents, tags = serializers.get_post(post_id)
        data = serializers.to_representation(contents, tags)

        auth_user = get_auth_user(request)
        author = 유저.objects.get(닉네임=data["작성자"])

        if auth_user == author:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'error': '허가된 사용자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
    def put(self, request, *args, **kwargs):
        data = request.data
        print(data)
        auth_user = get_auth_user(request)
        author = 유저.objects.get(닉네임=data["작성자"])

        if auth_user == author:
            post = 게시물.objects.get(모델=kwargs["모델_id"])

            tags = str(data["태그"])
            del data["access-token"]
            del data["태그"]
            data["유저"] = auth_user.id
            
            serializer = 게시물Serializer(post, data = data, partial=True)

            if serializer.is_valid():
                serializer.save()
                delete_tag(data["모델_id"])
                add_tag(data["모델_id"], tags)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




'''
모델(게시물) 열기-------------------------------------------------------------------------------------------------------------------------------
'''
class 글읽기View(APIView):
    def get(self, request, *args, **kwargs):
        post_id = kwargs["모델_id"]

        serializers = 게시물태그보기Serializer()
        contents, tags = serializers.get_post(post_id)
        data = serializers.to_representation(contents, tags)

        auth_user = get_auth_user(request)
        author = 유저.objects.get(닉네임=data["작성자"])
        if auth_user == author:
            data["is_author"] = True
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(data, status=status.HTTP_200_OK)



class 모델불러오기View(APIView):
    def post(self, request, *args, **kwargs):
        post_id = kwargs["모델_id"]
        post = 게시물.objects.get(모델=kwargs["모델_id"])

        auth_user = get_auth_user(request)
        author = 유저.objects.get(id=post.유저_id)

        if auth_user == author:
            serializer = 유저_import_모델Serializer(data={"모델_id":post_id, "유저_id":author.id})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




'''
IMPORT / EXPORT 구현-------------------------------------------------------------------------------------------------------------------------------
'''
class 유저임포트모델_list_View(APIView):
    def post(self, request, *args, **kwargs):

        auth_user = get_auth_user(request)
        
        if not auth_user:
            return Response({'error': '허가된 사용자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializers = 유저_import_모델Serializer()
        data = serializers.get_user_import_relation(auth_user.id)
        
        if len(data) == 0:
            return Response({"데이터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        user_import_models = serializers.to_json(data)

        return Response(user_import_models, status=status.HTTP_200_OK)
    

class 유저임포트모델View(APIView):
    
    def post(self, request, *args, **kwargs):
        model_id = kwargs["모델_id"]

        auth_user = get_auth_user(request)

        if not auth_user:
            return Response({'error': '허가된 사용자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            target = 유저_import_모델.objects.get(유저=auth_user.id, 모델=model_id)
            serializer =유저_import_모델Serializer(target)
            return Response(serializer.data , status=status.HTTP_200_OK)
        except 유저_import_모델.DoesNotExist:
            return Response(False , status=status.HTTP_204_NO_CONTENT)
        
    def put(self, request, *args, **kwargs):
        model_id = kwargs["모델_id"]

        auth_user = get_auth_user(request)

        if not auth_user:
            return Response({'error': '허가된 사용자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = 유저_import_모델Serializer(data = {"유저":auth_user.id, "모델":model_id})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class 유저임포트모델_delete_View(APIView):
    def post(self, request, *args, **kwargs):
        model_id = kwargs["모델_id"]

        auth_user = get_auth_user(request)

        if not auth_user:
            return Response({'error': '허가된 사용자가 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            instance = 유저_import_모델.objects.get(유저=auth_user.id, 모델=model_id)
            instance.delete()
            return Response("user model relation deleted", status=status.HTTP_200_OK)

        except 유저_import_모델.DoesNotExist:
            return Response('user model relation does not exist', status=status.HTTP_400_BAD_REQUEST)
    



'''
데모페이지-------------------------------------------------------------------------------------------------------------------------------
'''    
from .demo_run import word2vec_run
class 단어유사도데모_View(APIView):
    def post(self, request, *args, **kwargs):
        datas = request.data

        model_id = datas["모델_id"]
        input_words = datas["input_words"]
        model_path = base_path + 모델.objects.get(id=model_id).path

        similar_list = word2vec_run.calculate_word_similarity(model_path, input_words)

        if similar_list == "path or type error":
            return Response(similar_list, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif similar_list == "model error":
            return Response(similar_list, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(similar_list, status=status.HTTP_200_OK)
        
class 문장유사도데모_View(APIView):
    def post(self, request, *args, **kwargs):
        datas = request.data
        print(datas)
        model_id = datas["모델_id"]
        input_sentence = datas["input_sentence"]
        sentence_list = datas["sentence_list"]
        model_path = base_path + 모델.objects.get(id=model_id).path

        similar_list = word2vec_run.calculate_sentence_similarity(model_path, input_sentence, sentence_list)

        if similar_list == "path or type error":
            return Response(similar_list, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif similar_list == "model error":
            return Response(similar_list, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(similar_list, status=status.HTTP_200_OK)

