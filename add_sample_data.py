"""سكربت لإضافة بيانات تجريبية كثيرة"""
from app import app
from models import db, Patient, Drug
import random

# أسماء عربية
first_names_male = ['محمد', 'أحمد', 'علي', 'حسن', 'حسين', 'عمر', 'خالد', 'سعيد', 'عبدالله', 'إبراهيم', 'يوسف', 'عبدالرحمن', 'فيصل', 'سلطان', 'ماجد', 'طارق', 'وليد', 'سامي', 'ناصر', 'فهد']
first_names_female = ['فاطمة', 'عائشة', 'خديجة', 'مريم', 'زينب', 'سارة', 'نورة', 'هند', 'ريم', 'لينا', 'دانة', 'جود', 'رهف', 'شهد', 'أمل', 'منى', 'سلمى', 'ليلى', 'هيا', 'نوف']
last_names = ['العتيبي', 'الدوسري', 'الشمري', 'القحطاني', 'الغامدي', 'الزهراني', 'العمري', 'الحربي', 'المطيري', 'العنزي', 'السهلي', 'الجهني', 'البلوي', 'الرشيدي', 'السبيعي', 'الشهري']

# أدوية شاملة
drugs_data = [
    {'name': 'باراسيتامول 500 ملغ', 'category': 'مسكنات', 'dosages': ['500 ملغ', '1000 ملغ'], 'interactions': ['وارفارين'], 'contraindications': ['أمراض الكبد'], 'warnings': 'لا تتجاوز 4 غرام يومياً'},
    {'name': 'إيبوبروفين 400 ملغ', 'category': 'مسكنات', 'dosages': ['200 ملغ', '400 ملغ'], 'interactions': ['أسبرين', 'وارفارين'], 'contraindications': ['قرحة المعدة'], 'warnings': 'يؤخذ مع الطعام'},
    {'name': 'أموكسيسيلين 500 ملغ', 'category': 'مضادات حيوية', 'dosages': ['250 ملغ', '500 ملغ'], 'interactions': ['ميثوتريكسات'], 'contraindications': ['حساسية البنسلين'], 'warnings': 'أكمل الدورة كاملة'},
    {'name': 'أزيثروميسين 500 ملغ', 'category': 'مضادات حيوية', 'dosages': ['250 ملغ', '500 ملغ'], 'interactions': ['وارفارين'], 'contraindications': ['أمراض الكبد'], 'warnings': 'قد يسبب اضطرابات قلبية'},
    {'name': 'أوميبرازول 20 ملغ', 'category': 'أدوية الجهاز الهضمي', 'dosages': ['10 ملغ', '20 ملغ', '40 ملغ'], 'interactions': ['كلوبيدوغريل'], 'contraindications': [], 'warnings': 'يؤخذ قبل الطعام'},
    {'name': 'ميتفورمين 500 ملغ', 'category': 'أدوية السكري', 'dosages': ['500 ملغ', '850 ملغ', '1000 ملغ'], 'interactions': ['كحول'], 'contraindications': ['أمراض الكلى'], 'warnings': 'يؤخذ مع الطعام'},
    {'name': 'أملوديبين 5 ملغ', 'category': 'أدوية القلب والضغط', 'dosages': ['5 ملغ', '10 ملغ'], 'interactions': ['سيمفاستاتين'], 'contraindications': ['انخفاض الضغط'], 'warnings': 'قد يسبب تورم الكاحلين'},
    {'name': 'إنالابريل 10 ملغ', 'category': 'أدوية القلب والضغط', 'dosages': ['5 ملغ', '10 ملغ', '20 ملغ'], 'interactions': ['مدرات البول'], 'contraindications': ['الحمل'], 'warnings': 'قد يسبب سعال جاف'},
    {'name': 'أتورفاستاتين 20 ملغ', 'category': 'أدوية الكولسترول', 'dosages': ['10 ملغ', '20 ملغ', '40 ملغ'], 'interactions': ['جريب فروت'], 'contraindications': ['أمراض الكبد'], 'warnings': 'قد يسبب ألم عضلي'},
    {'name': 'سالبوتامول بخاخ', 'category': 'أدوية الجهاز التنفسي', 'dosages': ['100 مكغ/بخة'], 'interactions': ['حاصرات بيتا'], 'contraindications': [], 'warnings': 'للاستخدام عند الحاجة'},
    {'name': 'سيتريزين 10 ملغ', 'category': 'مضادات الحساسية', 'dosages': ['5 ملغ', '10 ملغ'], 'interactions': ['كحول'], 'contraindications': [], 'warnings': 'قد يسبب نعاس'},
    {'name': 'أسبرين 100 ملغ', 'category': 'مضادات تجلط', 'dosages': ['75 ملغ', '100 ملغ'], 'interactions': ['وارفارين'], 'contraindications': ['قرحة المعدة'], 'warnings': 'قد يزيد خطر النزيف'},
]

medical_conditions = ['ضغط دم مرتفع', 'سكري نوع 2', 'ارتفاع الكولسترول', 'الربو', 'حساسية موسمية']
common_allergies = ['بنسلين', 'سلفا', 'أسبرين', 'إيبوبروفين']

def add_drugs():
    print("جاري إضافة الأدوية...")
    added = 0
    for drug_data in drugs_data:
        if Drug.query.filter_by(name=drug_data['name']).first():
            continue
        drug = Drug(name=drug_data['name'], category=drug_data['category'], warnings=drug_data['warnings'], available=True)
        drug.set_dosages(drug_data['dosages'])
        drug.set_interactions(drug_data['interactions'])
        drug.set_contraindications(drug_data['contraindications'])
        db.session.add(drug)
        added += 1
    db.session.commit()
    print(f"تم إضافة {added} دواء")

def add_patients(count=100):
    print(f"جاري إضافة {count} مريض...")
    added = 0
    for i in range(count):
        gender = random.choice(['ذكر', 'أنثى'])
        first_name = random.choice(first_names_male if gender == 'ذكر' else first_names_female)
        full_name = f"{first_name} {random.choice(last_names)}"
        file_number = f"P{1000 + i:04d}"
        
        if Patient.query.filter_by(file_number=file_number).first():
            continue
        
        age = random.randint(18, 85)
        has_conditions = random.random() < 0.6
        conditions = random.sample(medical_conditions, random.randint(1, 3)) if has_conditions else []
        has_allergies = random.random() < 0.3
        allergies = random.sample(common_allergies, random.randint(1, 2)) if has_allergies else []
        has_meds = random.random() < 0.5
        current_meds = [random.choice([d['name'] for d in drugs_data]) for _ in range(random.randint(1, 3))] if has_meds else []
        
        patient = Patient(
            file_number=file_number,
            name=full_name,
            age=age,
            gender=gender,
            medical_history=', '.join(conditions) if conditions else 'لا يوجد',
            contact_info=f"05{random.randint(10000000, 99999999)}"
        )
        patient.set_current_medications(current_meds)
        patient.set_allergies(allergies)
        db.session.add(patient)
        added += 1
        
        if (i + 1) % 50 == 0:
            db.session.commit()
            print(f"تم إضافة {i + 1} مريض...")
    
    db.session.commit()
    print(f"تم إضافة {added} مريض بنجاح")

if __name__ == '__main__':
    with app.app_context():
        print("=== بدء إضافة البيانات التجريبية ===\n")
        add_drugs()
        print()
        add_patients(150)
        print("\n=== اكتملت العملية بنجاح ===")
