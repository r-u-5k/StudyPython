from django.shortcuts import render

from AdvDjango.CBV.models import Test


# Create your views here.
def BoardsFunctionView(request):
    boardList = Test.objects.all()
    return render(request, 'boardsfunctionview.html',
                  {'boardList': boardList})
