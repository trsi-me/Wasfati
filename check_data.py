"""التحقق من البيانات في قاعدة البيانات"""
from app import app
from models import db, Patient, Drug

with app.app_context():
    patients_count = Patient.query.count()
    drugs_count = Drug.query.count()
    
    print(f"\n=== احصائيات قاعدة البيانات ===")
    print(f"   عدد المرضى: {patients_count}")
    print(f"   عدد الأدوية: {drugs_count}")
    
    print(f"\n=== امثلة من المرضى ===")
    for patient in Patient.query.limit(5).all():
        print(f"   - {patient.file_number}: {patient.name} ({patient.age} سنة، {patient.gender})")
    
    print(f"\n=== امثلة من الأدوية ===")
    for drug in Drug.query.limit(5).all():
        print(f"   - {drug.name} ({drug.category})")
    
    print(f"\n=== النظام جاهز للاستخدام ===\n")
