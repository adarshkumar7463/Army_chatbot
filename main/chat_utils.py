import difflib
import re
from thefuzz import fuzz
from main.models import Officer, Family, Education, Award
from django.db.models import Count, Q, Avg
from datetime import datetime, date
from haystack.query import SearchQuerySet

# ✅ Import export helpers
from .utils.exports import (
    export_officers,
    export_family,
    export_education,
    export_awards,
)

# Define keyword mappings (Hinglish/English)
KEYWORDS = {
            "full_name": ["full name", "name", "officer name", "officer ka naam", "pura naam"],
            "rank": ["rank", "Rank", "rank of officer"],
            "position": ["position", "posted", "tainaati", "posting", "kahan tainat"],
            "unit": ["unit", "battalion", "unit name", "unit ka naam", "battalion ka naam"],
            "date of birth": ["dob", "janmdin", "birth", "birthday", "date of birth", "janm tithi"],
            "enlistment date": ["enlistment date", "joining date", "enlistment tithi", "joining tithi", "date of enlistment", "date of joining"],
            "phone": ["phone", "contact", "mobile", "phone number", "mobile number", "phone no.", "mobile no.", "contact number", "phone contact", "mobile contact"],
            "email": ["email", "email id", "email address", "ईमेल", "ईमेल आईडी", "ईमेल पता"],
            "address": ["address", "pata", "address details", "pata details", "officer address", "officer pata"],
            "blood group": ["blood group", "blood type", "रक्त समूह", "रक्त प्रकार", "blood group of officer", "officer ka blood group"],
            "photo": ["photo", "image", "picture", "फोटो", "छवि", "officer photo", "officer image", "officer picture"],
            


# Educational details about the officer
            
            "degree": ["degree", "course"],
            "institution": ["institute", "institution","padhai", "university", "college", "organization"],
            "passing year": ["passing year","when did pass", "pass"],
            "grade": ["grade"],
            "educational details" : ["educational", "educational details", "full education details" , "education",  "padhai ki jankari", "shiksha ki jankari"],


# Family details about the officer

            "family details": ["family's","family details", "parivaar ki jankari", "family information", "parivaar ki soochna", "family info", "parivaar ka pata"],
            "father name": ["father's", "father", "pita", "papa","dad", "father's name", "father name" "papa ka naam"],
            "mother name": ["mother's", "mother", "mata", "maa","mom", "mother's name", "mother name", "maa ka naam",],

# Awards details about the officer

            "award": ["award", "medal", "awards", "awarded", "puraskar", "puraskaar", "award details", "puraskar ki jankari"],
            "reason": ["awardreason", "karn", "award reason", "puraskar ka karan", "award ka reason", "puraskar ka reason", "award reason details", "why awarded", "kyun diya gaya"],
            "award date": ["award date",  "puraskar ki tithi", "award date details", "puraskar ka din",  "kab diya gaya"],
            "award location": ["award location", "puraskar sthal", "award place", "puraskar ka sthal", "puraskar ka jagah", "award location details"],
            "achievement details": ["achievement details", "achievement", "achievements"],


# Basic details about the officer
            "army_id": ["army id", "army number", "officer id","officer number", "id", "pehchan sankhya"],
            "basic details": ["basic", "personal",  "officer details", "officer information"],
            "family": ["family", "parivaar", "family details"],
            "posted in" : ["posted in", "posting in", "unit", "location", "tainaath", "posted", "hai", "mein"]

}

ALL_MODELS = {
    'officer': Officer,
    'family': Family,
    'education': Education,
    'award': Award,
}

# -------------------- UTILS -------------------- #
def match_field(input_text):
    input_text = input_text.lower()
    for k, v in KEYWORDS.items():
        if k in input_text:
            return v
    # Fallback fuzzy
    matches = difflib.get_close_matches(input_text, KEYWORDS.keys(), n=1, cutoff=0.6)
    if matches:
        return KEYWORDS[matches[0]]
    return None

# def extract_target_officer(text):
#     # First try by army number
#     army_number_match = re.search(r'\b(?=.*\d)[A-Za-z0-9]{2,15}\b', text, re.IGNORECASE)
#     if army_number_match:
#         army_number = army_number_match.group()
#         try:
#             return Officer.objects.get(army_number=army_number)
#         except Officer.DoesNotExist:
#             pass

#     # Then by name using fuzzy matching
#     return find_similar_officers(text)


def extract_target_officer(text):
    # 1. Try army number (numeric or alphanumeric with at least one digit)
    army_number_match = re.search(r'\b[A-Za-z]*\d+[A-Za-z0-9]*\b', text, re.IGNORECASE)
    if army_number_match:
        army_number = army_number_match.group().upper().strip()
        print("DEBUG >>> Extracted:", army_number)

        try:
            officer = Officer.objects.get(army_number=army_number)
            print("DEBUG >>> Found officer:", officer.full_name)
            return officer
        except Officer.DoesNotExist:
            print("DEBUG >>> No officer with army_number:", army_number)

    # 2. Fallback: fuzzy by name
    return find_similar_officers(text)


def find_similar_officers(query):
    officers = Officer.objects.all()
    best_match = None
    highest_score = 0
    for officer in officers:
        score = fuzz.token_set_ratio(officer.full_name.lower(), query.lower())
        if score > highest_score:
            highest_score = score
            best_match = officer
    return best_match if highest_score >= 70 else None

def extract_location(text):
    known_locations = [
        "kashmir", "ladakh", "delhi", "punjab", "assam", "rajasthan",
        "jammu", "himachal", "sikkim", "nagaland", "manipur", "goa",
        "gujarat", "maharashtra", "kerala", "tamil nadu", "uttarakhand", 
        "punjab", "haryana regiment","1 Signal Group "
    ]
    for loc in known_locations:
        if loc.lower() in text.lower():
            return loc.capitalize()

    # Try extracting with regex
    match = re.search(r'in ([a-zA-Z\s]+)', text.lower())
    if match:
        return match.group(1).strip().capitalize()

    return None

def extract_award_name(query):
    awards = Award.objects.values_list('award_name', flat=True).distinct()
    for award in awards:
        if award.lower() in query.lower():
            return award
    return None

def process_query(query):
    # Original Haystack implementation
    query = query.lower()
    results = SearchQuerySet().filter(content=query)
    
    if not results:
        return "No matching data found. Try changing your question."
    
    response_lines = []
    for r in results[:5]:
        model = r.model_name.lower()
        if model == "officer":
            line = f"Officer: {r.full_name} {r.rank}, ID: {r.army_number}"
            if r.award:
                line += f", Award: {r.award_name}"
        elif model == "family":
            line = f"Family Member: {r.name}, Relation: {r.relation}, DOB: {r.dob}"
        elif model == "education":
            line = f"Education: {r.degree}, Institution: {r.institution}, passing Year: {r.year_of_passing}, Grade: {r.grade},"
        else:
            line = f"{model.title()} record found"
        response_lines.append(line)
    
    return "<br>".join(response_lines)

# ------------------ COMPLEX QUERY HANDLER ------------------ #
def handle_complex_query(query):
    """Handle queries requesting multiple fields with conditions"""
    query = query.lower()
    
    valid_fields = ['name', 'full_name', 'rank', 'unit', 'dob', 'date_of_birth', 
                    'phone', 'email', 'address', 'blood_group', 'enlistment_date']
    
    requested_fields = []
    for field in valid_fields:
        if field in query or KEYWORDS.get(field, field) in query:
            mapped_field = KEYWORDS.get(field, field)
            if mapped_field not in requested_fields:
                requested_fields.append(mapped_field)
    
    conditions = {}
    blood_group_match = re.search(r'group\s+([a-zA-Z+-\s]+)', query, re.IGNORECASE)
    if blood_group_match:
        blood_group = blood_group_match.group(1).strip().upper()
        conditions['blood_group'] = blood_group
    
    rank_match = re.search(r'(colonel|col|major|av|lieutenant|brigadier|general)', query, re.IGNORECASE)
    if rank_match:
        conditions['rank'] = rank_match.group(1).title()
    
    location = extract_location(query)
    if location:
        conditions['unit__icontains'] = location
    
    officers = Officer.objects.all()
    if conditions:
        officers = officers.filter(**conditions)
    
    if not officers:
        return "No officers found matching the criteria."
    
    response = []
    for officer in officers:
        officer_data = []
        for field in requested_fields:
            value = getattr(officer, field, 'N/A')
            if value:
                officer_data.append(f"{field.replace('_', ' ').title()}: {value}")
        response.append(f"Officer: {officer.full_name}\n" + "\n".join(officer_data))
    
    return "\n\n".join(response) if response else "No data found for the requested fields."

# ------------------ V2 PROCESSOR ------------------ #
def process_query_v2(query):
    query = query.lower()
    
    # detect export type
    export_type = None
    if "excel" in query:
        export_type = "excel"
    elif "word" in query:
        export_type = "word"
    elif "pdf" in query:
        export_type = "pdf"
    
    if re.search(r'(give me|show|list)\s+.*(blood group|rank|unit|position|address|enlistment_date|email|phone|award|degree|institution in\s+\w+)', query):
        return handle_complex_query(query)
    
    count_match = re.search(r'(how many|kitne|total|count|number)', query)
    if count_match:
        return handle_count_query(query)
    
    if re.search(r'(list|sabhi|all|give me|name)', query):
        return handle_bulk_query(query, export_type=export_type)
    
    officer = extract_target_officer(query)
    if officer:
        return handle_single_officer(query, officer, export_type=export_type)
    
    return process_query(query)



def handle_count_query(query):
    location = extract_location(query)
    if location:
        count = Officer.objects.filter(unit__icontains=location).count()
        return f"Total officers in {location}: {count}"
    
    rank_match = re.search(r'(col|colonel|brigadier|major|av|lieutenant|general)', query, re.IGNORECASE)
    if rank_match:
        rank = rank_match.group(1).title()
        count = Officer.objects.filter(rank__iexact=rank).count()
        return f"Total {rank}s: {count}"
    
    year_match = re.search(r'(after|before|since|in)\s*(\d{4})', query)
    if year_match:
        direction, year_str = year_match.groups()
        year = int(year_str)
        if direction == 'after':
            count = Officer.objects.filter(enlistment_date__year__gt=year).count()
            return f"Officers enlisted after {year}: {count}"
        elif direction == 'before':
            count = Officer.objects.filter(enlistment_date__year__lt=year).count()
            return f"Officers enlisted before {year}: {count}"
        else:
            count = Officer.objects.filter(enlistment_date__year__gte=year).count()
            return f"Officers enlisted in {year}: {count}"
    
    if 'award' in query:
        award_name = extract_award_name(query)
        if award_name:
            count = Award.objects.filter(award_name__icontains=award_name).count()
            return f"Officers with {award_name} award: {count}"
        else:
            count = Award.objects.count()
            return f"Total awards given: {count}"
    
    blood_match = re.search(r'\b(blood group|blood)\s*(A|B|AB|O)[+-]?\b', query, re.IGNORECASE)
    if blood_match:
        blood_group = blood_match.group(1).upper()
        count = Officer.objects.filter(blood_group=blood_group).count()
        return f"Officers with blood group {blood_group}: {count}"
    
    return "Could not determine count query. Please be more specific."





def handle_bulk_query(query, export_type=None):
    location = extract_location(query)
    if location:
        officers = Officer.objects.filter(unit__icontains=location)
        if not officers:
            return f"No officers found in {location}"
        
        if export_type:
            file_url = export_officers(officers, f"Officers in {location}", export_type)
            return _export_response(f"Officers in {location}", file_url, export_type)

        results = [f"{o.full_name} ({o.rank}) - {o.unit}" for o in officers]
        return f"Officers in {location}:\n" + "\n".join(results)
    
    rank_match = re.search(r'(colonel|brigadier|col|major|av|lieutenant|general)', query, re.IGNORECASE)
    if rank_match:
        rank = rank_match.group(1).title()
        officers = Officer.objects.filter(rank__iexact=rank)
        if not officers:
            return f"No {rank}s found"
        
        if export_type:
            file_url = export_officers(officers, f"{rank}s", export_type)
            return _export_response(f"{rank}s", file_url, export_type)

        results = [f"{o.full_name} - {o.unit}" for o in officers]
        return f"{rank}s:\n" + "\n".join(results)
    
    if 'award' in query:
        award_name = extract_award_name(query)
        if award_name:
            awards = Award.objects.filter(award_name__icontains=award_name).select_related('officer')
            if not awards:
                return f"No officers with {award_name} award found"
            
            if export_type:
                file_url = export_awards(awards, f"Awards: {award_name}", export_type)
                return _export_response(f"Awards: {award_name}", file_url, export_type)

            results = [f"{a.officer.full_name} - {a.award_name} ({a.date_awarded.year})" for a in awards]
            return f"Officers with {award_name} award:\n" + "\n".join(results)
        
        
    


    return "Could not determine bulk query. Please be more specific."





def handle_single_officer(query, officer, export_type=None):
    response = []
    
    if re.search(r'(basic|details|information|jankari|personal)', query):
        response.append(f"Army ID: {officer.army_number}")
        response.append(f"Name: {officer.full_name}")
        response.append(f"Rank: {officer.rank}")
        response.append(f"Unit: {officer.unit}")
        response.append(f"DOB: {officer.dob}")
        response.append(f"Blood Group: {officer.blood_group}")
        response.append(f"Enlistment Date: {officer.enlistment_date}")

        if officer.photo:
            response.append(f"Photo: {officer.photo.url}")
    
    if re.search(r'(contact|phone|mobile|email)', query):
        response.append(f"Phone: {officer.phone}")
        response.append(f"Email: {officer.email}")
        response.append(f"Address: {officer.address}")
    
    if re.search(r'(family|parivaar|father|mother|pita|mata)', query):
        family = Family.objects.filter(officer=officer)
        if family.exists():
            for member in family:
                response.append(f"{member.relation}: {member.name} (DOB: {member.dob}) ")
        else:
            response.append("No family records found")
    
    if re.search(r'(education|padhai|degree|shiksha)', query):
        educations = Education.objects.filter(officer=officer)
        if educations.exists():
            for edu in educations:
                response.append(f"Education: {edu.degree} from {edu.institution} ({edu.year_of_passing}) - Grade: {edu.grade}")
        else:
            response.append("No education records found")
    
    if re.search(r'(award|puraskar|medal)', query):
        awards = Award.objects.filter(officer=officer)
        if awards.exists():
            for award in awards:
                response.append(f"Award: {award.award_name} ({award.date_awarded}) for {award.reason}")
        else:
            response.append("No award records found")
    
    if export_type:
        if "family" in query:
            families = Family.objects.filter(officer=officer)
            file_url = export_family(families, f"Family of {officer.full_name}", export_type)
            return _export_response(f"Family of {officer.full_name}", file_url, export_type)
        elif "education" in query:
            educations = Education.objects.filter(officer=officer)
            file_url = export_education(educations, f"Education of {officer.full_name}", export_type)
            return _export_response(f"Education of {officer.full_name}", file_url, export_type)
        elif "award" in query:
            awards = Award.objects.filter(officer=officer)
            file_url = export_awards(awards, f"Awards of {officer.full_name}", export_type)
            return _export_response(f"Awards of {officer.full_name}", file_url, export_type)
        else:
            file_url = export_officers([officer], f"Officer {officer.full_name}", export_type)
            return _export_response(f"Officer {officer.full_name}", file_url, export_type)
    
    if not response:
        response.append(f"Name: {officer.full_name}")
        response.append(f"Rank: {officer.rank}")
        response.append(f"Unit: {officer.unit}")
        response.append(f"Army ID: {officer.army_number}")
    
    return "\n".join(response)

# ------------- Helper for formatted export response ------------- #
def _export_response(title, file_url, export_type):
    return f"""
    <div style="text-align:center; margin:15px; padding:10px; border:1px solid #ccc; border-radius:8px;">
        <h2>Army Record System</h2>
        <h4>{title}</h4>
        <a href="{file_url}" class="btn btn-primary" target="_blank">
            📂 Download {export_type.upper()} Report
        </a>
    </div>
    """
