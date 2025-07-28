from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return render(request, 'index.html')

def explaboral(request):   
    return render(request, 'explaboral.html')

def proyectos_redirect(request):
    return redirect('https://github.com/willi0710')
