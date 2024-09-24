from django.shortcuts import render, redirect
from django.urls import reverse
from . import forms
from .models import FarmInfo
from django.contrib.auth import login
from django.contrib import messages
from .forms import UploadDocument, AddFileCategory, JoinFarmForm
from .models import FarmInfo, FileRecord, FileCategory
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, FileResponse
from UserAuth.models import UserProfile, SecurityGroup
from datetime import date
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required # This indicates that logging in is required
import random, string
from django.utils import timezone
from Settings.models import LinkingCode
from UserAuth.models import user_farm

"""
This class is used to define the linking manager which is responsible for generating, deleting and using linking codes.
"""

class LinkingManager():
    
    # Generates a random 15-character code consisting of uppercase letters and digits
    def random_code(self):
        characters = string.ascii_uppercase + string.digits
        linking_code = ''.join(random.choice(characters) for _ in range(15))

        # Check if the generated code already exists in the database
        if LinkingCode.objects.filter(code=linking_code).exists():
            # If it exists, recursively generate a new code
            return self.random_code()
        return linking_code 
    
     # Checks all linking codes in the database and deletes any that have expired
    def delete_expired_codes(self):
        LinkingCode.objects.filter(expires_at__lte=timezone.now()).delete()
    
    # Generates a new linking code for a given farm ID and saves it to the database
    def generate_code(self, farmID, expiry = False):
        self.delete_expired_codes()
        linking_code = self.random_code()
        if expiry: 
            new_code = LinkingCode.objects.create(code=linking_code, farm=farmID, expires_at=expiry)
        else:
            new_code = LinkingCode.objects.create(code=linking_code, farm=farmID)
        new_code.save()
        return linking_code       
    
    # Retrieves a linking code object from the database based on the provided code
    def get_code(self, code: string):
        try:
            linking_code = LinkingCode.objects.get(code=code)
            return linking_code
        except LinkingCode.DoesNotExist:
            return False
    # Deletes a linking code from the database based on the provided code
    def delete_code(self, code: string):
        codeInstance = self.get_code(code)
        if codeInstance != False:
            codeInstance.delete()
        else:
            return "Code does not exist"
        
    # Get the farm associated with a linking code
    def get_farm(self, code: string):
        codeInstance = self.get_code(code)
        if codeInstance != False:
            return codeInstance.farm
        else:
            return False

    # Uses a linking code to add a user to a farm if the code is valid and not expired
    def use_code(self, code: string, user):
        codeInstance = self.get_code(code)
        if codeInstance != False:
            if not codeInstance.is_expired():
                print("Code is not expired")
                user.farm.add(codeInstance.farm)
                user.currentFarm = codeInstance.farm
                user.save()
                codeInstance.delete()
                return True
            else:
                codeInstance.delete()
                return False
        else:
            return False

class FarmManager():
    def get_user_farms(self, user: UserProfile):
        """
        This function is used to retrieve the farms associated with a given user.
        """
        return user.farm.all()
    
    def get_user_active_farms(self, user: UserProfile):
        """
        This function is used to retrieve the active farms associated with a given user.
        """
        return user.farm.filter(user_farm__is_active=True)
    
    def get_user_farm_assignments(self, user: UserProfile):
        """
        This function is used to retrieve the farm assignments associated with a given user.
        """
        return user_farm.objects.filter(user_id=user.id)
    
    def get_user_current_farm(self, user: UserProfile):
        """
        This function is used to retrieve the current farm associated with a given user.
        """
        return user.currentFarm_id

    def set_user_current_farm(self, user: UserProfile, farm: FarmInfo):
        """
        This function is used to set the current farm associated with a given user.
        """
        user.currentFarm = farm
        user.save()
    
    def set_user_current_farm_by_id(self, user: UserProfile, farm_id: int):
        """
        This function is used to set the current farm associated with a given user by farm_id.
        """
        user.currentFarm_id = farm_id
        user.save()

    def get_user_farm_by_id(self, user: UserProfile, farm_id: int):
        """
        This function is used to retrieve the farm associated with a given user by farm_id.
        """
        return user.farm.get(id=farm_id)
    
    def remove_user_farm(self, user: UserProfile, farm: FarmInfo):
        """
        This function is used to remove the farm associated with a given user.
        """
        user.farm.remove(farm)
        user.save()
    
    def get_farm_users(self, farm: FarmInfo):
        """
        This function is used to retrieve the users associated with a given farm.
        """
        return farm.userprofile_set.all()
    
    def get_farm_users_by_farm_id(self, farm_id: int):
        """
        This function is used to retrieve the users associated with a given farm by farm_id.
        """
        return user_farm.objects.filter(farm_id=farm_id)
    



def joinFarm(request):
    linking_manager = LinkingManager()
    context = {
        "form" : forms.JoinFarmForm()
    }
    if request.method == "POST":
        form = forms.JoinFarmForm(request.POST)

        if form.is_valid():
            linking_code = form.cleaned_data["linking_code"]
            farm = linking_manager.get_farm(linking_code)
            linking_code_check = linking_manager.use_code(linking_code, request.user)
            if linking_code_check:
                #messages.success(request, "You have successfully joined {{farm_name}}. Welcome to the team!")
                return redirect('home', farm_id = farm.id)
            else:
                messages.error(request, "Invalid linking code. Please try again.")
        print(form.errors)
    return render(request, "FarmAcc/JoinFarm.html", context)


def newFarm(request):
    context = {
        "form" : forms.NewFarm()
    }
    if request.method == "POST":
        form = forms.NewFarm(request.POST, request.FILES)
        if form.is_valid():
            # current_user = UserProfile.objects.get(userID_id=request.user.id)
            current_user = request.user
            # Add new user to the Farm Owner Permission Group
            # farmOwnerGroup = SecurityGroup.objects.get(name='Farm Owner')
            # current_user.groups.add(farmOwnerGroup)
            # current_user.save()

            newId = form.save()
            farmInstance = FarmInfo.objects.get(id=newId.id)
            current_user.farm.add(farmInstance)
            current_user.currentFarm_id = farmInstance
            current_user.save()
            return redirect('home', farm_id = farmInstance.id)
        else:
            messages.error(request, "Invalid data. Please try again.")
            return render(request,  "FarmAcc/NewFarm.html", context)
    return render(request, "FarmAcc/NewFarm.html", context)

def chooseFarm(request):
    farmManager = FarmManager()
    context = {
        "farms" : farmManager.get_user_active_farms(request.user)
    }
    return render(request, "FarmAcc/ChooseFarm.html", context)





# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
    The Following Code Pertains viewing, updating and downloading Farm Files within the application.
"""

@login_required(login_url='login')
def fileView(request: HttpRequest):
    """
    The 'fileView' view handles the back-end functionality associated with rendering a list of farm related
    files. It retrieves a list of 'FileRecord's from the 'database' & 'media/File' locations and returns 
    a list to the 'farmFiles' html template. 
    
    The 'UploadDocument' form has been included to enable documents to be added via a modal form in 'farmFiles.html'.

    The variable 'today' is used to determine if a given FileRecord has exceeded their review date. 
    """
    # Handle 'POST' requests (when a file has been uploaded to the server)
    if request.method == "POST":
        uploadDocForm = UploadDocument(request.POST, request.FILES)
        if uploadDocForm.is_valid():
            file = uploadDocForm.save(commit=False)
            category_id = uploadDocForm.cleaned_data["fileCategory"]
            if category_id != "":
                file.fileCategory = category_id
            else:
                file.fileCategory = None
            file.save()
            return redirect('home', farm_id = request.user.currentFarm_id)
        fileCatForm = AddFileCategory(request.POST)
        if fileCatForm.is_valid():
            fileCatForm.save()
        else:
            fileCatForm = AddFileCategory()
            uploadDocForm = UploadDocument()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Handle 'Get' Requests
    fileCatForm = AddFileCategory()
    uploadDocForm = UploadDocument()
    fileList = FileRecord.objects.all().order_by('fileName')                                                  # < -- -- -- -- -- -- -- -- -- -- -- -- Will need to filter it on a tenant by tenant basis
    context = {
        "fileList": fileList,
        "uploadDocForm": uploadDocForm,
        "fileCatForm": fileCatForm,
        "today": date.today(),
    }
    return render(request, "FarmAcc/farmFiles.html", context)


@login_required(login_url='login')
def downloadFile(request : HttpRequest, file_id: int):
    """
    This view, given a file_id for a specific 'fileRecord' object, will download the file in
    the user's browser. 
    """
    # Retrieve the specific FileRecord Object
    file_to_download = FileRecord.objects.get(pk=file_id)
    file = file_to_download.file.open()
    response = FileResponse(file, as_attachment=True, filename=file_to_download.file.name)
    # Return a FileResponse object to the requesting browser
    return response


@login_required(login_url='login')
def deleteFile(request: HttpRequest, file_id: int):
    """
    This view, given a file_id, will delete the corresponding 'FileRecord' object from the database.
    """
    file = FileRecord.objects.get(id=file_id)
    file.delete()
    return HttpResponseRedirect(reverse('fileView')) 


@login_required(login_url='login')
def editFile(request: HttpRequest, file_id: int):
    """
    This view enables edit
    """
    # Retrieve the requested File_id
    file = FileRecord.objects.get(pk=file_id)
    # Pre-populate the form with information about the 'fileRecord'
    initial = {
        "fileName": file.fileName,
        "reviewDate": file.reviewDate,
        "file": file.file,
        "fileCategory": file.fileCategory,
     }  
    form = UploadDocument(initial=initial)     
    if request.method == "GET":
        redirectURL= request.META.get('HTTP_REFERER')
        request.session['http_referer'] = redirectURL
        
    # Handle 'POST' requests (when a 'fileRecord' has been updated)
    if request.method == "POST":
        form = UploadDocument(request.POST, request.FILES, instance=file)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.session['http_referer'])   
        else:
            form = UploadDocument()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Handle 'Get' Requests
    context = {
        "form": form,
    }
    return render(request, "FarmAcc/farmFileDetails.html", context)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -