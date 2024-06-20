from django.shortcuts import render, redirect
from django.contrib.auth.models import auth, User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message
from django.db.models import Q
from .forms import RoomForm, UserForm


# Create your views here.


def home(request):
    
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(description__icontains = q)
    )
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(
        Q(room__name__icontains=q) |
        Q(room__description__icontains = q) |
        Q(room__topic__name__icontains = q)
    )
    context = {
        'rooms': rooms,
        'topics': topics,
        'rooms_count': rooms.count(),
        'room_messages': room_messages
    }
    return render(request, 'core/home.html', context)


def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    room = message.room.id
    message.delete()

    return redirect('room', room)


def room(request, pk):
    room = Room.objects.get(id=int(pk))
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        new_message = request.POST['message']
        
        if new_message != None or new_message != '':
            Message.objects.create(
                user = request.user,
                room = room,
                body = new_message
            )
            room.participants.add(request.user)
            return redirect('room', pk=room.id)


    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants
    }
    return render(request, 'core/room.html', context)



@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room_name = request.POST.get('name')
        description = request.POST.get('description')
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = room_name,
            description = description
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'core/room_form.html', context)



@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=int(pk))
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')

    context = {
        'room': room,
        'form': form,
        'topics': topics,
        
    }
    return render(request, 'core/room_form.html', context)



@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=int(pk))

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'core/delete.html', {'obj': room.name})


def profile(request, pk):
    user = User.objects.get(id=int(pk))
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user_': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics
    }
    return render(request, 'core/profile.html', context)


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
    return render(request, 'core/update_user.html', {'form':form})


def login(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'invalid credentials')
    context = {
        'page': page
    }
    return render(request, 'core/login_register.html', context)



def logout(request):
    auth.logout(request)
    return redirect('home')



def register(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            auth.login(request, user)
            return redirect('home')
        
    context = {
        'page': page,
        'form': form
    }
    return render(request, 'core/login_register.html', context)
