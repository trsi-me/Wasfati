"""
وظائف مساعدة لفحص التداخلات الدوائية والموانع
"""

def check_drug_interactions(drug, patient_medications, patient_allergies):
    """
    فحص التداخلات الدوائية والموانع
    
    Args:
        drug: كائن الدواء المراد فحصه
        patient_medications: قائمة الأدوية الحالية للمريض
        patient_allergies: قائمة الحساسيات للمريض
    
    Returns:
        dict: {
            'safe': bool,
            'warnings': list,
            'severity': str  # 'none', 'low', 'medium', 'high'
        }
    """
    
    warnings = []
    severity = 'none'
    
    # فحص الحساسية
    drug_name_lower = drug.name.lower()
    for allergy in patient_allergies:
        allergy_lower = allergy.lower()
        if allergy_lower in drug_name_lower or drug_name_lower in allergy_lower:
            warnings.append(f'تحذير خطير: المريض لديه حساسية من {allergy}')
            severity = 'high'
    
    # فحص الموانع مع الحساسيات
    contraindications = drug.get_contraindications()
    for contraindication in contraindications:
        contraindication_lower = contraindication.lower()
        for allergy in patient_allergies:
            allergy_lower = allergy.lower()
            if allergy_lower in contraindication_lower or contraindication_lower in allergy_lower:
                warnings.append(f'تحذير: مانع استخدام - {contraindication}')
                if severity != 'high':
                    severity = 'high'
    
    # فحص التداخلات مع الأدوية الحالية
    interactions = drug.get_interactions()
    for interaction in interactions:
        interaction_lower = interaction.lower()
        for med in patient_medications:
            med_lower = med.lower()
            if interaction_lower in med_lower or med_lower in interaction_lower:
                warnings.append(f'تحذير: تداخل دوائي محتمل مع {med}')
                if severity == 'none':
                    severity = 'medium'
                elif severity == 'low':
                    severity = 'medium'
    
    # فحص التكرار (نفس الدواء موجود)
    for med in patient_medications:
        med_lower = med.lower()
        # استخراج اسم الدواء الأساسي (قبل الجرعة)
        drug_base_name = drug.name.split()[0].lower()
        med_base_name = med.split()[0].lower()
        
        if drug_base_name == med_base_name or drug_base_name in med_lower or med_base_name in drug_name_lower:
            warnings.append(f'تحذير: المريض يتناول بالفعل دواء مشابه - {med}')
            if severity == 'none':
                severity = 'low'
    
    safe = severity not in ['high']
    
    return {
        'safe': safe,
        'warnings': warnings,
        'severity': severity
    }


def suggest_prescription(symptoms, diagnosis, patient, available_drugs):
    """
    اقتراح وصفة طبية بناءً على الأعراض والتشخيص
    
    Args:
        symptoms: الأعراض
        diagnosis: التشخيص
        patient: كائن المريض
        available_drugs: قائمة الأدوية المتاحة
    
    Returns:
        list: قائمة الأدوية المقترحة مع معلومات السلامة
    """
    
    suggestions = []
    patient_medications = patient.get_current_medications()
    patient_allergies = patient.get_allergies()
    
    # تحليل بسيط للأعراض والتشخيص لاقتراح فئات الأدوية
    symptoms_lower = (symptoms or '').lower()
    diagnosis_lower = (diagnosis or '').lower()
    
    # خريطة الكلمات المفتاحية للفئات
    category_keywords = {
        'مسكنات': ['ألم', 'صداع', 'وجع', 'حرارة', 'سخونة'],
        'مضادات حيوية': ['التهاب', 'عدوى', 'بكتيريا', 'صديد'],
        'أدوية الجهاز الهضمي': ['حموضة', 'معدة', 'قرحة', 'حرقة', 'غثيان'],
        'أدوية السكري': ['سكر', 'سكري', 'جلوكوز'],
        'أدوية القلب والضغط': ['ضغط', 'قلب', 'ضغط دم']
    }
    
    # تحديد الفئات المناسبة
    relevant_categories = []
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in symptoms_lower or keyword in diagnosis_lower:
                if category not in relevant_categories:
                    relevant_categories.append(category)
                break
    
    # إذا لم يتم العثور على فئات محددة، اقترح من جميع الفئات
    if not relevant_categories:
        relevant_categories = list(category_keywords.keys())
    
    # فلترة الأدوية حسب الفئات المناسبة
    for drug in available_drugs:
        if not drug.available:
            continue
        
        # فحص إذا كان الدواء من الفئات المناسبة
        if drug.category not in relevant_categories:
            continue
        
        # فحص التداخلات والموانع
        safety_check = check_drug_interactions(drug, patient_medications, patient_allergies)
        
        # إضافة الدواء للاقتراحات
        suggestion = {
            'drug': drug.to_dict(),
            'safety': safety_check,
            'recommended_dosage': drug.get_dosages()[0] if drug.get_dosages() else 'حسب إرشادات الطبيب',
            'duration': 'حسب الحالة',
            'instructions': 'يؤخذ حسب إرشادات الطبيب'
        }
        
        suggestions.append(suggestion)
    
    # ترتيب الاقتراحات حسب السلامة
    severity_order = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
    suggestions.sort(key=lambda x: severity_order.get(x['safety']['severity'], 4))
    
    return suggestions


def format_prescription_text(prescription_items):
    """
    تنسيق نص الوصفة الطبية
    
    Args:
        prescription_items: قائمة عناصر الوصفة
    
    Returns:
        str: نص الوصفة منسق
    """
    
    if not prescription_items:
        return 'لا توجد أدوية موصوفة'
    
    text_lines = []
    for i, item in enumerate(prescription_items, 1):
        drug_name = item.get('drug_name', 'غير محدد')
        dosage = item.get('dosage', 'غير محدد')
        duration = item.get('duration', 'غير محدد')
        instructions = item.get('instructions', 'حسب إرشادات الطبيب')
        
        text_lines.append(f"{i}. {drug_name}")
        text_lines.append(f"   الجرعة: {dosage}")
        text_lines.append(f"   المدة: {duration}")
        text_lines.append(f"   التعليمات: {instructions}")
        text_lines.append("")
    
    return '\n'.join(text_lines)


def validate_patient_data(data):
    """
    التحقق من صحة بيانات المريض
    
    Args:
        data: قاموس بيانات المريض
    
    Returns:
        tuple: (bool, list) - (صحيح أم لا، قائمة الأخطاء)
    """
    
    errors = []
    
    # التحقق من الحقول المطلوبة
    required_fields = ['file_number', 'name', 'age', 'gender']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'الحقل {field} مطلوب')
    
    # التحقق من العمر
    age = data.get('age')
    if age:
        try:
            age = int(age)
            if age < 0 or age > 150:
                errors.append('العمر غير صحيح')
        except ValueError:
            errors.append('العمر يجب أن يكون رقماً')
    
    # التحقق من الجنس
    gender = data.get('gender')
    if gender and gender not in ['ذكر', 'أنثى']:
        errors.append('الجنس يجب أن يكون ذكر أو أنثى')
    
    return len(errors) == 0, errors


def validate_drug_data(data):
    """
    التحقق من صحة بيانات الدواء
    
    Args:
        data: قاموس بيانات الدواء
    
    Returns:
        tuple: (bool, list) - (صحيح أم لا، قائمة الأخطاء)
    """
    
    errors = []
    
    # التحقق من الحقول المطلوبة
    required_fields = ['name', 'category']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'الحقل {field} مطلوب')
    
    return len(errors) == 0, errors
