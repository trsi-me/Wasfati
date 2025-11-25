from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from config import Config
from models import db, Patient, Drug, Visit, User, init_db
from utils import check_drug_interactions, suggest_prescription, format_prescription_text, validate_patient_data, validate_drug_data
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات
init_db(app)


# Decorator للتحقق من تسجيل الدخول
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            return redirect(url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')


@app.route('/patients')
@login_required
def patients_list():
    """عرض قائمة المرضى"""
    search = request.args.get('search', '')
    
    if search:
        patients = Patient.query.filter(
            (Patient.name.like(f'%{search}%')) | 
            (Patient.file_number.like(f'%{search}%'))
        ).all()
    else:
        patients = Patient.query.order_by(Patient.created_at.desc()).all()
    
    return render_template('patients_list.html', patients=patients, search=search)


@app.route('/patient/<int:patient_id>')
@login_required
def patient_view(patient_id):
    """عرض تفاصيل مريض"""
    patient = Patient.query.get_or_404(patient_id)
    visits = Visit.query.filter_by(patient_id=patient_id).order_by(Visit.visit_date.desc()).all()
    return render_template('patient_view.html', patient=patient, visits=visits)


@app.route('/patient/new', methods=['GET', 'POST'])
@login_required
def patient_new():
    """إضافة مريض جديد"""
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # التحقق من البيانات
        valid, errors = validate_patient_data(data)
        if not valid:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # التحقق من عدم تكرار رقم الملف
        existing = Patient.query.filter_by(file_number=data['file_number']).first()
        if existing:
            return jsonify({'success': False, 'errors': ['رقم الملف موجود مسبقاً']}), 400
        
        # إنشاء المريض
        patient = Patient(
            file_number=data['file_number'],
            name=data['name'],
            age=int(data['age']),
            gender=data['gender'],
            medical_history=data.get('medical_history', ''),
            contact_info=data.get('contact_info', '')
        )
        
        # الأدوية الحالية
        medications = request.form.getlist('current_medications[]')
        patient.set_current_medications([m for m in medications if m])
        
        # الحساسيات
        allergies = request.form.getlist('allergies[]')
        patient.set_allergies([a for a in allergies if a])
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({'success': True, 'patient_id': patient.id})
    
    return render_template('patient_edit.html', patient=None)


@app.route('/patient/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def patient_edit(patient_id):
    """تعديل بيانات مريض"""
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # التحقق من البيانات
        valid, errors = validate_patient_data(data)
        if not valid:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # التحقق من عدم تكرار رقم الملف
        if data['file_number'] != patient.file_number:
            existing = Patient.query.filter_by(file_number=data['file_number']).first()
            if existing:
                return jsonify({'success': False, 'errors': ['رقم الملف موجود مسبقاً']}), 400
        
        # تحديث البيانات
        patient.file_number = data['file_number']
        patient.name = data['name']
        patient.age = int(data['age'])
        patient.gender = data['gender']
        patient.medical_history = data.get('medical_history', '')
        patient.contact_info = data.get('contact_info', '')
        
        # الأدوية الحالية
        medications = request.form.getlist('current_medications[]')
        patient.set_current_medications([m for m in medications if m])
        
        # الحساسيات
        allergies = request.form.getlist('allergies[]')
        patient.set_allergies([a for a in allergies if a])
        
        db.session.commit()
        
        return jsonify({'success': True, 'patient_id': patient.id})
    
    return render_template('patient_edit.html', patient=patient)


@app.route('/patient/<int:patient_id>/prescribe', methods=['GET', 'POST'])
@login_required
def patient_prescribe(patient_id):
    """إنشاء وصفة طبية لمريض"""
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        data = request.get_json()
        
        # إنشاء زيارة جديدة
        visit = Visit(
            patient_id=patient_id,
            symptoms=data.get('symptoms', ''),
            diagnosis=data.get('diagnosis', ''),
            doctor_name=data.get('doctor_name', 'د. غير محدد'),
            notes=data.get('notes', '')
        )
        
        # حفظ الوصفة
        prescription = data.get('prescription', [])
        visit.set_prescription(prescription)
        
        db.session.add(visit)
        db.session.commit()
        
        return jsonify({'success': True, 'visit_id': visit.id})
    
    # GET: عرض صفحة الوصفة
    drugs = Drug.query.filter_by(available=True).all()
    return render_template('patient_prescribe.html', patient=patient, drugs=drugs)


@app.route('/api/suggest-prescription', methods=['POST'])
@login_required
def api_suggest_prescription():
    """API لاقتراح وصفة طبية"""
    data = request.get_json()
    
    patient_id = data.get('patient_id')
    symptoms = data.get('symptoms', '')
    diagnosis = data.get('diagnosis', '')
    
    patient = Patient.query.get_or_404(patient_id)
    available_drugs = Drug.query.filter_by(available=True).all()
    
    suggestions = suggest_prescription(symptoms, diagnosis, patient, available_drugs)
    
    return jsonify({'success': True, 'suggestions': suggestions})


@app.route('/api/check-interaction', methods=['POST'])
@login_required
def api_check_interaction():
    """API لفحص التداخلات الدوائية"""
    data = request.get_json()
    
    drug_id = data.get('drug_id')
    patient_id = data.get('patient_id')
    
    drug = Drug.query.get_or_404(drug_id)
    patient = Patient.query.get_or_404(patient_id)
    
    safety_check = check_drug_interactions(
        drug,
        patient.get_current_medications(),
        patient.get_allergies()
    )
    
    return jsonify({'success': True, 'safety': safety_check})


@app.route('/drugs')
@login_required
def drugs_list():
    """عرض قائمة الأدوية"""
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Drug.query
    
    if search:
        query = query.filter(Drug.name.like(f'%{search}%'))
    
    if category:
        query = query.filter_by(category=category)
    
    drugs = query.order_by(Drug.name).all()
    
    # الحصول على الفئات المتاحة
    categories = db.session.query(Drug.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('drugs_list.html', drugs=drugs, categories=categories, search=search, selected_category=category)


@app.route('/drug/<int:drug_id>')
@login_required
def drug_view(drug_id):
    """عرض تفاصيل دواء"""
    drug = Drug.query.get_or_404(drug_id)
    return render_template('drug_view.html', drug=drug)


@app.route('/drug/new', methods=['GET', 'POST'])
@login_required
def drug_new():
    """إضافة دواء جديد"""
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # التحقق من البيانات
        valid, errors = validate_drug_data(data)
        if not valid:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # إنشاء الدواء
        drug = Drug(
            name=data['name'],
            category=data['category'],
            description=data.get('description', ''),
            warnings=data.get('warnings', ''),
            available=data.get('available', 'true') == 'true'
        )
        
        # الجرعات
        dosages = request.form.getlist('dosages[]')
        drug.set_dosages([d for d in dosages if d])
        
        # التداخلات
        interactions = request.form.getlist('interactions[]')
        drug.set_interactions([i for i in interactions if i])
        
        # الموانع
        contraindications = request.form.getlist('contraindications[]')
        drug.set_contraindications([c for c in contraindications if c])
        
        db.session.add(drug)
        db.session.commit()
        
        return jsonify({'success': True, 'drug_id': drug.id})
    
    return render_template('drug_edit.html', drug=None)


@app.route('/drug/<int:drug_id>/edit', methods=['GET', 'POST'])
@login_required
def drug_edit(drug_id):
    """تعديل بيانات دواء"""
    drug = Drug.query.get_or_404(drug_id)
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # التحقق من البيانات
        valid, errors = validate_drug_data(data)
        if not valid:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # تحديث البيانات
        drug.name = data['name']
        drug.category = data['category']
        drug.description = data.get('description', '')
        drug.warnings = data.get('warnings', '')
        drug.available = data.get('available', 'true') == 'true'
        
        # الجرعات
        dosages = request.form.getlist('dosages[]')
        drug.set_dosages([d for d in dosages if d])
        
        # التداخلات
        interactions = request.form.getlist('interactions[]')
        drug.set_interactions([i for i in interactions if i])
        
        # الموانع
        contraindications = request.form.getlist('contraindications[]')
        drug.set_contraindications([c for c in contraindications if c])
        
        db.session.commit()
        
        return jsonify({'success': True, 'drug_id': drug.id})
    
    return render_template('drug_edit.html', drug=drug)


@app.route('/api/search-patients')
@login_required
def api_search_patients():
    """API للبحث عن المرضى"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'results': []})
    
    patients = Patient.query.filter(
        (Patient.name.like(f'%{query}%')) | 
        (Patient.file_number.like(f'%{query}%'))
    ).limit(10).all()
    
    results = [{'id': p.id, 'file_number': p.file_number, 'name': p.name} for p in patients]
    
    return jsonify({'results': results})


@app.route('/api/search-drugs')
@login_required
def api_search_drugs():
    """API للبحث عن الأدوية"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'results': []})
    
    drugs = Drug.query.filter(
        Drug.name.like(f'%{query}%')
    ).filter_by(available=True).limit(10).all()
    
    results = [{'id': d.id, 'name': d.name, 'category': d.category} for d in drugs]
    
    return jsonify({'results': results})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
