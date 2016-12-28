from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

def home(request):
    # user = request.user
    # context = {}
    # context['user'] = user
    return render(request, 'index.html') #, context)
