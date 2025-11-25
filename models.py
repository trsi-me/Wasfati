from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    """نموذج المستخدم (الأدمن)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """تعيين كلمة المرور مع التشفير"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    """نموذج بيانات المريض"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    file_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # ذكر / أنثى
    current_medications = db.Column(db.Text)  # JSON list
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)  # JSON list
    contact_info = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # علاقة مع الزيارات
    visits = db.relationship('Visit', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def get_current_medications(self):
        """الحصول على قائمة الأدوية الحالية"""
        if self.current_medications:
            try:
                return json.loads(self.current_medications)
            except:
                return []
        return []
    
    def set_current_medications(self, medications_list):
        """تعيين قائمة الأدوية الحالية"""
        self.current_medications = json.dumps(medications_list, ensure_ascii=False)
    
    def get_allergies(self):
        """الحصول على قائمة الحساسيات"""
        if self.allergies:
            try:
                return json.loads(self.allergies)
            except:
                return []
        return []
    
    def set_allergies(self, allergies_list):
        """تعيين قائمة الحساسيات"""
        self.allergies = json.dumps(allergies_list, ensure_ascii=False)
    
    def to_dict(self):
        """تحويل البيانات إلى قاموس"""
        return {
            'id': self.id,
            'file_number': self.file_number,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'current_medications': self.get_current_medications(),
            'medical_history': self.medical_history,
            'allergies': self.get_allergies(),
            'contact_info': self.contact_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Drug(db.Model):
    """نموذج بيانات الدواء"""
    __tablename__ = 'drugs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    dosages = db.Column(db.Text)  # JSON list
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    interactions = db.Column(db.Text)  # JSON list of drug interactions
    contraindications = db.Column(db.Text)  # JSON list
    warnings = db.Column(db.Text)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_dosages(self):
        """الحصول على قائمة الجرعات"""
        if self.dosages:
            try:
                return json.loads(self.dosages)
            except:
                return []
        return []
    
    def set_dosages(self, dosages_list):
        """تعيين قائمة الجرعات"""
        self.dosages = json.dumps(dosages_list, ensure_ascii=False)
    
    def get_interactions(self):
        """الحصول على قائمة التداخلات الدوائية"""
        if self.interactions:
            try:
                return json.loads(self.interactions)
            except:
                return []
        return []
    
    def set_interactions(self, interactions_list):
        """تعيين قائمة التداخلات الدوائية"""
        self.interactions = json.dumps(interactions_list, ensure_ascii=False)
    
    def get_contraindications(self):
        """الحصول على قائمة الموانع"""
        if self.contraindications:
            try:
                return json.loads(self.contraindications)
            except:
                return []
        return []
    
    def set_contraindications(self, contraindications_list):
        """تعيين قائمة الموانع"""
        self.contraindications = json.dumps(contraindications_list, ensure_ascii=False)
    
    def to_dict(self):
        """تحويل البيانات إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'dosages': self.get_dosages(),
            'category': self.category,
            'description': self.description,
            'interactions': self.get_interactions(),
            'contraindications': self.get_contraindications(),
            'warnings': self.warnings,
            'available': self.available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Visit(db.Model):
    """نموذج زيارة المريض والوصفة الطبية"""
    __tablename__ = 'visits'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)  # JSON list of prescribed drugs
    doctor_name = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_prescription(self):
        """الحصول على قائمة الأدوية الموصوفة"""
        if self.prescription:
            try:
                return json.loads(self.prescription)
            except:
                return []
        return []
    
    def set_prescription(self, prescription_list):
        """تعيين قائمة الأدوية الموصوفة"""
        self.prescription = json.dumps(prescription_list, ensure_ascii=False)
    
    def to_dict(self):
        """تحويل البيانات إلى قاموس"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'symptoms': self.symptoms,
            'diagnosis': self.diagnosis,
            'prescription': self.get_prescription(),
            'doctor_name': self.doctor_name,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_db(app):
    """تهيئة قاعدة البيانات"""
    db.init_app(app)
    
    with app.app_context():
        # إنشاء مجلد instance إذا لم يكن موجوداً
        import os
        instance_path = os.path.join(app.root_path, 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        
        # إنشاء الجداول
        db.create_all()
        
        # إضافة بيانات تجريبية إذا كانت قاعدة البيانات فارغة
        if Drug.query.count() == 0:
            add_sample_data()


def add_sample_data():
    """إضافة بيانات تجريبية"""
    
    # أدوية تجريبية
    sample_drugs = [
        {
            'name': 'باراسيتامول 500 ملغ (تجريبي)',
            'dosages': ['500 ملغ', '1000 ملغ'],
            'category': 'مسكنات',
            'description': 'مسكن للألم وخافض للحرارة',
            'interactions': ['وارفارين', 'كاربامازيبين'],
            'contraindications': ['أمراض الكبد الشديدة', 'حساسية من الباراسيتامول'],
            'warnings': 'لا تتجاوز 4 غرام يومياً',
            'available': True
        },
        {
            'name': 'أموكسيسيلين 500 ملغ (تجريبي)',
            'dosages': ['250 ملغ', '500 ملغ', '1000 ملغ'],
            'category': 'مضادات حيوية',
            'description': 'مضاد حيوي واسع الطيف',
            'interactions': ['ميثوتريكسات', 'وارفارين'],
            'contraindications': ['حساسية من البنسلين', 'حساسية من السيفالوسبورينات'],
            'warnings': 'أكمل الدورة العلاجية كاملة',
            'available': True
        },
        {
            'name': 'أوميبرازول 20 ملغ (تجريبي)',
            'dosages': ['10 ملغ', '20 ملغ', '40 ملغ'],
            'category': 'أدوية الجهاز الهضمي',
            'description': 'مثبط لمضخة البروتون لعلاج الحموضة',
            'interactions': ['كلوبيدوغريل', 'ديازيبام'],
            'contraindications': ['حساسية من الأوميبرازول'],
            'warnings': 'يؤخذ قبل الطعام بنصف ساعة',
            'available': True
        },
        {
            'name': 'ميتفورمين 500 ملغ (تجريبي)',
            'dosages': ['500 ملغ', '850 ملغ', '1000 ملغ'],
            'category': 'أدوية السكري',
            'description': 'دواء لعلاج السكري من النوع الثاني',
            'interactions': ['كحول', 'مدرات البول'],
            'contraindications': ['أمراض الكلى الشديدة', 'حماض كيتوني'],
            'warnings': 'تحذير: قد يسبب حماض لبني نادراً',
            'available': True
        },
        {
            'name': 'أملوديبين 5 ملغ (تجريبي)',
            'dosages': ['5 ملغ', '10 ملغ'],
            'category': 'أدوية القلب والضغط',
            'description': 'خافض لضغط الدم',
            'interactions': ['سيمفاستاتين', 'ديلتيازيم'],
            'contraindications': ['انخفاض شديد في الضغط', 'صدمة قلبية'],
            'warnings': 'قد يسبب تورم في الكاحلين',
            'available': True
        }
    ]
    
    for drug_data in sample_drugs:
        drug = Drug(
            name=drug_data['name'],
            category=drug_data['category'],
            description=drug_data['description'],
            warnings=drug_data['warnings'],
            available=drug_data['available']
        )
        drug.set_dosages(drug_data['dosages'])
        drug.set_interactions(drug_data['interactions'])
        drug.set_contraindications(drug_data['contraindications'])
        db.session.add(drug)
    
    # مرضى تجريبيون
    sample_patients = [
        {
            'file_number': 'P001',
            'name': 'أحمد محمد (تجريبي)',
            'age': 45,
            'gender': 'ذكر',
            'current_medications': ['أملوديبين 5 ملغ', 'ميتفورمين 500 ملغ'],
            'medical_history': 'ضغط دم مرتفع، سكري نوع 2',
            'allergies': ['بنسلين'],
            'contact_info': '0501234567'
        },
        {
            'file_number': 'P002',
            'name': 'فاطمة علي (تجريبي)',
            'age': 32,
            'gender': 'أنثى',
            'current_medications': [],
            'medical_history': 'لا يوجد',
            'allergies': [],
            'contact_info': '0507654321'
        }
    ]
    
    for patient_data in sample_patients:
        patient = Patient(
            file_number=patient_data['file_number'],
            name=patient_data['name'],
            age=patient_data['age'],
            gender=patient_data['gender'],
            medical_history=patient_data['medical_history'],
            contact_info=patient_data['contact_info']
        )
        patient.set_current_medications(patient_data['current_medications'])
        patient.set_allergies(patient_data['allergies'])
        db.session.add(patient)
    
    # إضافة مستخدم افتراضي (admin)
    if User.query.count() == 0:
        admin = User(username='admin', full_name='المسؤول')
        admin.set_password('admin123')
        db.session.add(admin)
    
    db.session.commit()
