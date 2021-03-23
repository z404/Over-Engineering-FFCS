from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadTeacherDataForm
from django.core.files.storage import FileSystemStorage


def testView(request):
    return HttpResponse("test view yayy")


def UploadTeacherDataView(request):
    if (request.method == 'POST'):
        form = UploadTeacherDataForm(request.POST, request.FILES)
        if form.is_valid():
            # form.save()
            excel_file = request.FILES['excel_file']
            fs = FileSystemStorage()
            filename = fs.save(excel_file.name, excel_file)
            uploaded_file_url = fs.url(filename)
            return HttpResponse(f"{type(request.FILES['excel_file'])}")
    else:
        form = UploadTeacherDataForm()
        context = {
            'form': form,
        }
    return render(request, 'oeffcs/UploadExcel.html', context=context)
