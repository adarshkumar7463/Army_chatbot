from haystack import indexes
from main.models import Officer, Education, Family, Award

class OfficerIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    army_number = indexes.CharField(model_attr='army_number')
    full_name = indexes.CharField(model_attr='full_name')
    rank = indexes.CharField(model_attr='rank')
    position = indexes.CharField(model_attr='position')
    unit = indexes.CharField(model_attr='unit')
    phone = indexes.CharField(model_attr='phone')
    email = indexes.CharField(model_attr='email')
    
    def get_model(self):
        return Officer
    
    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class EducationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    degree = indexes.CharField(model_attr='degree')
    institution = indexes.CharField(model_attr='institution')
    year_of_passing = indexes.IntegerField(model_attr='year_of_passing')
    grade = indexes.CharField(model_attr='grade')
    
    def get_model(self):
        return Education
    
    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class FamilyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    relation = indexes.CharField(model_attr='relation')
    occupation = indexes.CharField(model_attr='occupation')
    
    def get_model(self):
        return Family
    
    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class AwardIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    award_name = indexes.CharField(model_attr='award_name')
    reason = indexes.CharField(model_attr='reason')
    location = indexes.CharField(model_attr='location')
    
    def get_model(self):
        return Award
    
    def index_queryset(self, using=None):
        return self.get_model().objects.all()