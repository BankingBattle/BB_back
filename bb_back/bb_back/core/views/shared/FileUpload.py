from django.shortcuts import render
from django.http import HttpResponseRedirect
from bb_back.core.models import ResumeForm

# Создайте здесь представления.


def upload_resume(request):
    if request.method == "POST":
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/")
    else:
        form = ResumeForm
    return render(request, "files/resume.html", {"form": form})
