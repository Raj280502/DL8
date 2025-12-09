# brain/views.py
from django.http import JsonResponse
from .mongodb import brain_collection

def add_brain_data(request):
    data = {
        "name": "Patient A",
        "age": 45,
        "condition": "Multiple Sclerosis"
    }
    result = brain_collection.insert_one(data)
    return JsonResponse({"inserted_id": str(result.inserted_id)})

def list_brain_data(request):
    data = list(brain_collection.find({}, {"_id": 0}))  # Exclude _id
    return JsonResponse({"data": data})
