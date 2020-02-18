from django.shortcuts import render

# Create your views here.
def privacy_statement(request):
    template_name = 'privacy/privacy_statement.html'
    context = {}

    if request.method == 'GET':
        pass

    return render(request, template_name, context)