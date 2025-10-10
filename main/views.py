# views.py
from tkinter import Image
from django.shortcuts import render, redirect
import pytesseract
from .models import Officer, Education, Family, Award
from .forms import OfficerForm, EducationForm, FamilyForm, AwardForm
from django.contrib import messages
from django.http import HttpResponse, JsonResponse  
import haystack              
from haystack.query import SearchQuerySet 
from django.conf import settings
from .ocr_utils import extract_fields, preprocess_image
import logging
import os
import uuid
from django.views.decorators.csrf import csrf_exempt
import re
from .chat_utils import extract_location, process_query_v2
from thefuzz import fuzz, process

# Configure logger
logger = logging.getLogger(__name__)

def home(request):
    context = {
        'officer_count': Officer.objects.count(),
        'award_count': Award.objects.count(),
        'education_count': Education.objects.count(),
    }
    return render(request, 'main/home.html', context)

def create_officer(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registered successfully!')
            return redirect('success')
    else:
        form = OfficerForm()
    return render(request, 'main/officer_form.html', {'form': form})

def add_education(request, army_number):
    try:
        officer = Officer.objects.get(army_number=army_number)
    except Officer.DoesNotExist:
        messages.error(request, 'Officer not found!')
        return redirect('home')
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.officer = officer
            education.save()
            messages.success(request, 'Education Registered successfully!')
            return redirect('success')
    else:
        form = EducationForm()
    
    return render(request, 'main/education_form.html', {
        'form': form,
        'officer': officer
    })

def add_family(request, army_number):
    try:
        officer = Officer.objects.get(army_number=army_number)
    except Officer.DoesNotExist:
        messages.error(request, 'Officer not found!')
        return redirect('home')
    
    if request.method == 'POST':
        form = FamilyForm(request.POST)
        if form.is_valid():
            family = form.save(commit=False)
            family.officer = officer
            family.save()
            messages.success(request, 'Family Registered successfully!')
            return redirect('success')
    else:
        form = FamilyForm()
    
    return render(request, 'main/family_form.html', {
        'form': form,
        'officer': officer
    })

def add_award(request, army_number):
    try:
        officer = Officer.objects.get(army_number=army_number)
    except Officer.DoesNotExist:
        messages.error(request, 'Officer not found!')
        return redirect('home')
    
    if request.method == 'POST':
        form = AwardForm(request.POST)
        if form.is_valid():
            award = form.save(commit=False)
            award.officer = officer
            award.save()
            messages.success(request, 'Award Registered successfully!')
            return redirect('success')
    else:
        form = AwardForm()
    
    return render(request, 'main/award_form.html', {
        'form': form,
        'officer': officer
    })

def success(request):
    return render(request, 'main/success.html')

def chat_api(request):
    query = request.GET.get('q', '').strip()
    
    if query:
        # First search across all models (you can limit if needed)
        results = SearchQuerySet().filter(content=query)
        
        if results:
            # Just take the first result for simplicity
            match = results[0].object
            
            if hasattr(match, 'full_name') and hasattr(match, 'rank'):
                # Officer result
                response_text = f"Name: {match.full_name}, Rank: {match.rank}, Unit: {getattr(match, 'unit', 'N/A')}"
            elif hasattr(match, 'degree'):
                response_text = f"Degree: {match.degree} - Officer: {match.officer.full_name}"
            elif hasattr(match, 'relation'):
                response_text = f"Relation: {match.relation} - Officer: {match.officer.full_name}"
            elif hasattr(match, 'award_name'):
                response_text = f"Award: {match.award_name} - Officer: {match.officer.full_name}"
            else:
                response_text = "Result found, but format is unknown."
        else:
            response_text = "❌ No results found in database."
    else:
        response_text = "❗ Please enter a query."

    return JsonResponse({'response': response_text})

def officer_registration(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            officer = form.save()
            return redirect('success')
        else:
            logger.error(f"Form errors: {form.errors}")
    else:
        form = OfficerForm()
    return render(request, 'main/officer_form.html', {'form': form})

def extract_officer_data(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            file = request.FILES['photo']
            extracted_data = extract_fields(file)
            
            # Handle case where extraction fails completely
            if extracted_data is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to extract any data from document'
                })
                
            # Handle errors in extraction
            if 'error' in extracted_data:
                return JsonResponse({
                    'success': False,
                    'error': extracted_data['error']
                })
                
            return JsonResponse({
                'success': True,
                'data': extracted_data
            })
                
        except Exception as e:
            logger.exception("OCR processing error")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({
        'success': False,
        'error': 'No file provided'
    })

def test_ocr(request):
    if request.method == 'POST' and request.FILES.get('test_image'):
        try:
            image = Image.open(request.FILES['test_image'])
            
            # Save original image
            original_path = os.path.join(settings.MEDIA_ROOT, 'test_original.png')
            image.save(original_path)
            
            # Process image
            processed = preprocess_image(image)
            
            # Save processed image
            processed_path = os.path.join(settings.MEDIA_ROOT, 'test_processed.png')
            Image.fromarray(processed).save(processed_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed, lang='eng')
            
            return render(request, 'test_ocr.html', {
                'original': os.path.join(settings.MEDIA_URL, 'test_original.png'),
                'processed': os.path.join(settings.MEDIA_URL, 'test_processed.png'),
                'text': text
            })
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")
    return render(request, 'test_ocr.html')

@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        user_input = request.POST.get("message", "").strip()
        if not user_input:
            return JsonResponse({"response": "Please enter a valid query."})
        
        try:
            response = process_query_v2(user_input)
        except Exception as e:
            logger.error(f"Query processing error: {str(e)}")
            response = "Error processing your request. Please try again."
        
        return JsonResponse({"response": response})
    
    return JsonResponse({"response": "Please enter a valid query."})



from django.http import FileResponse, Http404
import os
from django.conf import settings

def download_export(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, "exports", filename)
    if not os.path.exists(file_path):
        raise Http404("File not found")

    ext = os.path.splitext(filename)[1]
    content_type = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".csv": "text/csv",
    }.get(ext, "application/octet-stream")

    response = FileResponse(open(file_path, "rb"), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response