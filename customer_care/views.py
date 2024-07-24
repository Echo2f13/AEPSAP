from django.shortcuts import render


def login(request):
    return render(request, "customer_care\login.html")
