from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
import base64
import cv2
import numpy as np
from PIL import Image
import cv2
import io
from .forms import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import *
from django.http.response import StreamingHttpResponse
from streamapp.camera import VideoCamera, IPWebCam


import face_recognition
import imutils
import pickle
import time
import os
import json


def home(request):
    nbar = 'home'
    return render(request, 'index.html', {'nbar': nbar})


@csrf_exempt
def signup(request):
    nbar = 'signup'
    if request.method == 'GET':
        form = UserForm()
        return render(request, 'signup.html', {'nbar': nbar, 'form': form})
    elif request.method == 'POST':
        print("post request")
        form = UserForm(request.POST)
        if(form.is_valid()):
            form.save()
            # print(form.cleaned_data['username'])
            user = get_object_or_404(
                User, username=form.cleaned_data['username'])
            facedata = FaceData.objects.create(user=user)

            print(user)
            if user is not None:
                login(request, user)
            else:
                pass

            print("form is valid!")
            return redirect('home:register_face')
        else:
            print("invalid form")
            return render(request, 'signup.html', {'nbar': nbar, 'form': form})


@csrf_exempt
def register_face(request):
    nbar = 'signup'
    if request.method == 'GET':
        return render(request, 'register_face.html', {'nbar': nbar})
    elif request.method == 'POST':
        received_json_data = json.loads(request.body)
        # print(received_json_data)
        imageBase64 = received_json_data['imageBase64']
        # print(imageBase64)
        imageBase64 = imageBase64.split(',')[1]
        # print(request.user.username)

        encoding, err = get_face_encoding_from_base64(imageBase64)
        facedata = get_object_or_404(FaceData, user=request.user)

        if(err):
            return JsonResponse({'success': False, 'count': facedata.count, 'message': "No face detected!"})
        all_encondings = json.loads(facedata.encodings)
        all_encondings.append(encoding.tolist())
        all_encondings = json.dumps(all_encondings)
        FaceData.objects.filter(user=request.user).update(
            encodings=all_encondings, count=facedata.count+1)

        return JsonResponse({'success': True, 'count': facedata.count+1})


def get_face_encoding_from_base64(base64String):
    image = face_recognition.load_image_file(
        io.BytesIO(base64.b64decode(base64String)))
    image_encodeing = face_recognition.face_encodings(image)
    if len(image_encodeing) == 0:
        return [], True
    return image_encodeing[0], False


def signin(request):
    nbar = 'signin'
    context = {'nbar': nbar}
    context['userb_exists'] = False
    if request.method == "GET":
        username = request.GET.get('username')
        print(username)
        if(username != None and len(username) != 0):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None
            if(user == None):
                context['form_error'] = "User doesn't exist"
            else:
                context['user_exists'] = True
        return render(request, 'signin.html', context)

    return render(request, 'signin.html', context)


def signout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('home:index')


def getUserFaceData(username):
    user = get_object_or_404(User, username=username)
    if user == None:
        return None
    facedata = get_object_or_404(FaceData, user=user)
    return facedata


def compareFace(encodings, encoding):
    results = face_recognition.compare_faces(
        encodings, encoding, tolerance=0.6)
    return results


# def afterLogin(request):
#     return render(request, 'afterLogin.html', {'username': username})

def recognize(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        username = received_json_data['username']
        imageBase64 = received_json_data['imageBase64']
        imageBase64 = imageBase64.split(',')[1]

        encoding, err = get_face_encoding_from_base64(imageBase64)
        if err:
            return JsonResponse({'success': False, 'message': "No face detected!"})
        print(encoding)
        facedata = getUserFaceData(username)
        all_encondings = json.loads(facedata.encodings)
        print("initital: ", type(all_encondings), type(encoding))
        print(all_encondings)
        all_encondings = [np.array(x) for x in all_encondings]
        encoding = np.array(encoding)
        all_encondings = np.array(all_encondings)
        print("converted: ", type(all_encondings), type(encoding))
        results = compareFace(all_encondings, encoding)
        print(results)
        print(username)
        return JsonResponse({'success': True})

        # total = results.length
        # count=0
        # for res in results:
        #     if res==True:
        #         count+=1

        # accuracy = count*100/total
        # if accuracy >= 50:
        #     return render(request, 'afterLogin.html', {'username': username})

    else:
        return JsonResponse({'success': False})
