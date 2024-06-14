from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from .models import Room, Topic
from django.db.models import Q
from .forms import RoomForm
# Create your views here.



def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'invalid credentials')
    context = {}
    return render(request, 'core/login_register.html', context)

def logout(request):
    auth.logout(request)
    return redirect('home')

def home(request):
    
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(description__icontains = q)
    )
    topics = Topic.objects.all()
    context = {
        'rooms': rooms,
        'topics': topics,
        'rooms_count': rooms.count()
    }
    return render(request, 'core/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=int(pk))

    context = {
        'room': room
    }
    return render(request, 'core/room.html', context)

def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'core/room_form.html', context)


def update_room(request, pk):
    room = Room.objects.get(id=int(pk))
    form = RoomForm(instance=room)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {
        'room': room,
        'form': form
    }
    return render(request, 'core/room_form.html', context)

def delete_room(request, pk):
    room = Room.objects.get(id=int(pk))

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'core/delete.html', {'obj': room.name})