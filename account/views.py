from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def signup(request):
    if request.method == "POST":
        print("POST received:", request.POST)

        form = CreateUserForm(request.POST)

        print("Form valid:", form.is_valid())

        if form.is_valid():
            form.save()
            print("User created successfully!")
            return redirect("signin")
        else:
            print("Form errors:", form.errors)

    else:
        form = CreateUserForm()

    return render(request, "signup.html", {"form": form})

def signin(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                next_url = request.GET.get("next")

                if next_url:
                    return redirect(next_url)

                return redirect("home")

    else:
        form = LoginForm()

    return render(request, "signin.html", {"form": form})

def signout(request):
    if request.method == "POST":
        logout(request)

    return redirect("home")