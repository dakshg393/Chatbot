from django.shortcuts import render ,redirect
from django.http import JsonResponse
import openai

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.conf import settings 
from django.utils import timezone

import google.generativeai as genai

def generate_response(message):
    genai.configure(api_key="AIzaSyBQ9H-kEB2P-YxoLsCkA6GgHg4uriM2fx8")
    
    # Set up the model
    generation_config = {
      "temperature": 0.9,
      "top_p": 1,
      "top_k": 1,
      "max_output_tokens": 2048,
    }    
    
    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config=generation_config,
                                  )
    
    convo = model.start_chat(history=[])
    convo.send_message(message)
    
    return convo.last.text

def chatbot(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        chats = Chat.objects.filter(user=request.user)

        if request.method == 'POST':
            message =request.POST.get('message')
            response = generate_response(message)

            chat =Chat(user=request.user, message=message, response=response,created_at=timezone.now())
            chat.save()
            return JsonResponse({'message':message, 'response':response})
    return render(request,'chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message' : error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')



def logout(request):
    auth.logout(request)
    return redirect('/login')


