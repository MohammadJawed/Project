from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from application.models import UploadedFile, departmentData, employeeData
#from application import models
from .forms import FileUploadForm
import pandas as pd
from django.db.models import Count,Q
#from rest_framework import viewsets
from .serializer import Employee_CountSerializer, UserSerializer, CustomUser
#from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token


CustomUser = get_user_model()
# Create your views here.
@login_required(login_url='/')
def home(request):
    received_data = request.session.get('data', '')
    return render(request,"index.html",{"fname":received_data})
    # return render(request, "index.html")

def signup(request):
    return render(request, "signup.html")
class SignUpUser(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        public_visibility = request.POST.get('public_visibility')
        if pass1 != pass2:
            return JsonResponse({'error': 'Password and confirm password are different'})
        if public_visibility == 'on':
            public_visibility = True
        else:
            public_visibility = False        
        myuser = CustomUser.objects.create_user(email, username, pass1)
        myuser.first_name = fname
        myuser.last_name = lname 
        myuser.public_visibility = public_visibility == 'true'
        myuser.save()
        token, _ = Token.objects.get_or_create(user=myuser)
        redirection_url = "/"
        print(token.key)
        response_data = {'token': token.key, 'redirection_url': redirection_url}
        return Response(response_data,status=status.HTTP_200_OK)
    
class SignInUser(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        email = request.POST['email']
        pass1 = request.POST['pass1']
        user = authenticate(username=email, password=pass1)
        if user is None:
            return Response({'error':'Bad Credentials'},status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        print("Logged In")
        redirection_url = "index"
        print(token.key)
        response_data = {'token': token.key, 'redirection_url': redirection_url}
        return Response(response_data,status=status.HTTP_200_OK)

def signin(request):
    return render(request, "signin.html")

def signout(request):
    logout(request)
    messages.success(request,"Logged out successfully")
    return redirect('signin')


class DisplayUsers(APIView):
    def get(self, request):
        users = CustomUser.objects.all()
        print(users)
        serializer = UserSerializer(users, many=True)
        # redirection_url = "display/"
        # response_data = {'users': serializer.data, 'redirection_url': redirection_url}
        return Response(serializer.data, status=status.HTTP_200_OK)
        
def display(request):
    return render(request,'display_users.html')

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.user = request.user
            uploaded_file.save()
            messages.success(request, 'Book uploaded successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Error uploading the book. Please check the form.')
    else:
        form = FileUploadForm()

    return render(request, 'upload_files.html', {'form': form})

@login_required
def uploaded_images(request):
    received_data = request.session.get('data', '')
    user_files = UploadedFile.objects.filter(user = request.user)
    print(user_files.query)
    return render(request, 'uploaded_files.html', {'user_files': user_files, 'received_data' : received_data})

@login_required
def upload_data(request):
    if request.method == "POST":
        choice = request.POST.get('Upload')
        data = request.FILES.get('upload_file')
        if(data):
            try:
                df = pd.read_csv(data)
                print(df)
                if choice == "Department Data":
                    departmentData.objects.all().delete()
                    unique_departments = df['name'].unique()
                    # deparment_headings = df[['name','description']]
                    # departmentData.objects.bulk_create([departmentData(**row) for row in deparment_headings.to_dict(orient='records')])
                    for department_name in unique_departments:
                        department_instance, created = departmentData.objects.get_or_create(name=department_name, description=f'Description for {department_name}')
                        # print(department_instance)
                elif choice == "Employee Data":
                    employee_data = df[['first_name', 'last_name', 'email', 'year_joined', 'department']]
                    employeeData.objects.all().delete()

                    for _, row in employee_data.iterrows():
                        department_name = row['department']                        
                        # Retrieve the corresponding department instance based on the name
                        department_instance = departmentData.objects.get(name=department_name)
                    # employee_headings = df[['first_name','last_name','email','year_joined','department']]
                    # employeeData.objects.bulk_create([employeeData(**row) for row in employee_headings.to_dict(orient='records')])
                        new_employee = employeeData(
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            email=row['email'],
                            year_joined=row['year_joined'],
                            department=department_instance
                        )
                        new_employee.save()
            except pd.errors.ParserError:
                print("Error")
    list = employeeData.objects.values('department__name').annotate(user_count=Count('department'))
    print(list.query)
    # print(list)
    return render(request,'upload_data.html', {'departments': list})
    
class Employee_Count(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        list = employeeData.objects.values('department__name').annotate(user_count=Count('department'))
        print(list)
        #list_1 = departmentData.objects.values('name').annotate(employee_count=Count('employeedata'))print(list_1)
       # list_2 = departmentData.objects.values('name').annotate(employee_count=Count('employeeData', filter=Q(employeeData__year_joined__gt=2020)&Q(employeeData__first_name="Brittney")))print(list_2)

        serializer = Employee_CountSerializer(list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)