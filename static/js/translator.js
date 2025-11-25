// نظام الترجمة والاتجاه (RTL/LTR)
class Translator {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'ar';
        this.translations = {};
        this.loadTranslations();
    }

    async loadTranslations() {
        try {
            const response = await fetch('/static/js/translations.json');
            this.translations = await response.json();
            this.applyLanguage(this.currentLang);
        } catch (error) {
            console.error('Error loading translations:', error);
        }
    }

    applyLanguage(lang) {
        this.currentLang = lang;
        localStorage.setItem('language', lang);
        
        // تحديث اتجاه الصفحة
        const html = document.documentElement;
        const body = document.body;
        
        if (lang === 'ar') {
            html.setAttribute('lang', 'ar');
            html.setAttribute('dir', 'rtl');
            body.classList.add('rtl');
            body.classList.remove('ltr');
        } else {
            html.setAttribute('lang', 'en');
            html.setAttribute('dir', 'ltr');
            body.classList.add('ltr');
            body.classList.remove('rtl');
        }
        
        // ترجمة جميع العناصر
        this.translatePage();
        
        // تحديث زر اللغة
        this.updateLanguageButton();
    }

    translatePage() {
        // ترجمة العناصر بـ data-translate
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            const translation = this.getTranslation(key);
            
            if (translation) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    if (element.hasAttribute('placeholder')) {
                        element.setAttribute('placeholder', translation);
                    } else {
                        element.value = translation;
                    }
                } else {
                    element.textContent = translation;
                }
            }
        });
        
        // ترجمة العناصر بـ data-translate-html
        document.querySelectorAll('[data-translate-html]').forEach(element => {
            const key = element.getAttribute('data-translate-html');
            const translation = this.getTranslation(key);
            
            if (translation) {
                element.innerHTML = translation;
            }
        });
        
        // ترجمة العناصر بـ data-translate-title
        document.querySelectorAll('[data-translate-title]').forEach(element => {
            const key = element.getAttribute('data-translate-title');
            const translation = this.getTranslation(key);
            
            if (translation) {
                element.setAttribute('title', translation);
            }
        });
        
        // ترجمة المحتوى الديناميكي
        translateDynamicContent();
    }

    getTranslation(key) {
        const keys = key.split('.');
        let translation = this.translations[this.currentLang];
        
        for (const k of keys) {
            if (translation && translation[k]) {
                translation = translation[k];
            } else {
                return null;
            }
        }
        
        return translation;
    }

    translate(key) {
        return this.getTranslation(key) || key;
    }

    toggleLanguage() {
        const newLang = this.currentLang === 'ar' ? 'en' : 'ar';
        this.applyLanguage(newLang);
    }

    updateLanguageButton() {
        const langButton = document.getElementById('lang-toggle');
        if (langButton) {
            if (this.currentLang === 'ar') {
                langButton.innerHTML = '<i class="fa fa-language"></i> English';
            } else {
                langButton.innerHTML = '<i class="fa fa-language"></i> العربية';
            }
        }
    }

    getCurrentLang() {
        return this.currentLang;
    }

    // ترجمة الجندر الديناميكي
    translateGender(gender) {
        const genderMap = {
            'ar': {
                'ذكر': 'ذكر',
                'أنثى': 'أنثى',
                'Male': 'ذكر',
                'Female': 'أنثى'
            },
            'en': {
                'ذكر': 'Male',
                'أنثى': 'Female',
                'Male': 'Male',
                'Female': 'Female'
            }
        };
        
        return genderMap[this.currentLang][gender] || gender;
    }

    // فحص إذا كان النص يحتوي على خليط من العربية والإنجليزية (أسماء أشخاص)
    isMixedText(text) {
        if (!text) return false;
        const hasArabic = /[\u0600-\u06FF]/.test(text);
        const hasEnglish = /[a-zA-Z]/.test(text);
        return hasArabic && hasEnglish;
    }
    
    // فحص إذا كان النص يبدو كاسم شخص
    isPersonName(text) {
        if (!text) return false;
        // إذا كان النص قصير ولا يحتوي على أرقام أو وحدات طبية
        const hasNumbers = /\d/.test(text);
        const hasMedicalUnits = /\b(mg|ملغ|mcg|مكغ|µg|ug|g|غ|kg|كغ|ml|مل|l|ل|IU|U|tablet|قرص|capsule|كبسولة|syrup|شراب|injection|حقنة|cream|كريم|ointment|مرهم|drops|قطرة|spray|بخاخ|puff|بخة|dose|جرعة|sachet|كيس|vial|قارورة|ampoule|أمبولة|suppository|تحميلة|patch|لصقة)\b/i.test(text);
        return !hasNumbers && !hasMedicalUnits && text.length < 50;
    }
    
    // ترجمة الوحدات الطبية (ملغ، غرام، إلخ)
    translateMedicalUnits(text) {
        if (!text) return text;
        
        // لا تترجم النصوص المختلطة التي تبدو كأسماء أشخاص
        if (this.isMixedText(text) && this.isPersonName(text)) {
            return text;
        }
        
        const unitsMap = {
            'ar': {
                // الوزن
                'mg': 'ملغ',
                'mcg': 'مكغ',
                'µg': 'مكغ',
                'ug': 'مكغ',
                'g': 'غ',
                'kg': 'كغ',
                
                // الحجم
                'ml': 'مل',
                'l': 'ل',
                
                // الوحدات الدولية
                'IU': 'وحدة دولية',
                'U': 'وحدة',
                'units': 'وحدات',
                
                // الأشكال الصيدلانية
                'tablet': 'قرص',
                'tablets': 'أقراص',
                'capsule': 'كبسولة',
                'capsules': 'كبسولات',
                'syrup': 'شراب',
                'injection': 'حقنة',
                'cream': 'كريم',
                'ointment': 'مرهم',
                'drops': 'قطرة',
                'spray': 'بخاخ',
                'inhaler': 'بخاخ',
                'puff': 'بخة',
                'puffs': 'بخات',
                'dose': 'جرعة',
                'doses': 'جرعات',
                'sachet': 'كيس',
                'sachets': 'أكياس',
                'vial': 'قارورة',
                'vials': 'قوارير',
                'ampoule': 'أمبولة',
                'ampoules': 'أمبولات',
                'suppository': 'تحميلة',
                'suppositories': 'تحاميل',
                'patch': 'لصقة',
                'patches': 'لصقات'
            },
            'en': {
                // الوزن
                'ملغ': 'mg',
                'مكغ': 'mcg',
                'غ': 'g',
                'كغ': 'kg',
                
                // الحجم
                'مل': 'ml',
                'ل': 'l',
                
                // الوحدات الدولية
                'وحدة دولية': 'IU',
                'وحدة': 'U',
                'وحدات': 'units',
                
                // الأشكال الصيدلانية
                'قرص': 'tablet',
                'أقراص': 'tablets',
                'كبسولة': 'capsule',
                'كبسولات': 'capsules',
                'شراب': 'syrup',
                'حقنة': 'injection',
                'كريم': 'cream',
                'مرهم': 'ointment',
                'قطرة': 'drops',
                'بخاخ': 'spray',
                'بخة': 'puff',
                'بخات': 'puffs',
                'جرعة': 'dose',
                'جرعات': 'doses',
                'كيس': 'sachet',
                'أكياس': 'sachets',
                'قارورة': 'vial',
                'قوارير': 'vials',
                'أمبولة': 'ampoule',
                'أمبولات': 'ampoules',
                'تحميلة': 'suppository',
                'تحاميل': 'suppositories',
                'لصقة': 'patch',
                'لصقات': 'patches'
            }
        };
        
        let translated = text;
        const units = unitsMap[this.currentLang];
        
        for (const [key, value] of Object.entries(units)) {
            const regex = new RegExp('\\b' + key + '\\b', 'gi');
            translated = translated.replace(regex, value);
        }
        
        return translated;
    }

    // ترجمة أسماء الأدوية (جميع الأدوية الموجودة في النظام)
    translateCommonDrugNames(drugName) {
        if (!drugName) return drugName;
        
        // لا تترجم النصوص المختلطة التي تبدو كأسماء أشخاص
        if (this.isMixedText(drugName) && this.isPersonName(drugName)) {
            return drugName;
        }
        
        const drugNamesMap = {
            'ar': {
                // الأدوية الموجودة في النظام
                'Paracetamol': 'باراسيتامول',
                'Amoxicillin': 'أموكسيسيلين',
                'Omeprazole': 'أوميبرازول',
                'Metformin': 'ميتفورمين',
                'Amlodipine': 'أملوديبين',
                
                // أدوية إضافية شائعة
                'Ibuprofen': 'إيبوبروفين',
                'Aspirin': 'أسبرين',
                'Vitamin D': 'فيتامين د',
                'Vitamin C': 'فيتامين سي',
                'Azithromycin': 'أزيثروميسين',
                'Ciprofloxacin': 'سيبروفلوكساسين',
                'Cephalexin': 'سيفالكسين',
                'Clarithromycin': 'كلاريثروميسين',
                'Doxycycline': 'دوكسيسيكلين',
                'Atorvastatin': 'أتورفاستاتين',
                'Simvastatin': 'سيمفاستاتين',
                'Losartan': 'لوسارتان',
                'Enalapril': 'إنالابريل',
                'Bisoprolol': 'بيسوبرولول',
                'Carvedilol': 'كارفيديلول',
                'Furosemide': 'فوروسيميد',
                'Hydrochlorothiazide': 'هيدروكلوروثيازيد',
                'Warfarin': 'وارفارين',
                'Clopidogrel': 'كلوبيدوغريل',
                'Insulin': 'إنسولين',
                'Glimepiride': 'غليميبيريد',
                'Gliclazide': 'غليكلازيد',
                'Levothyroxine': 'ليفوثيروكسين',
                'Prednisolone': 'بريدنيزولون',
                'Dexamethasone': 'ديكساميثازون',
                'Salbutamol': 'سالبوتامول',
                'Montelukast': 'مونتيلوكاست',
                'Cetirizine': 'سيتريزين',
                'Loratadine': 'لوراتادين',
                'Ranitidine': 'رانيتيدين',
                'Pantoprazole': 'بانتوبرازول',
                'Esomeprazole': 'إيزوميبرازول',
                'Metoclopramide': 'ميتوكلوبراميد',
                'Domperidone': 'دومبيريدون',
                'Diclofenac': 'ديكلوفيناك',
                'Naproxen': 'نابروكسين',
                'Tramadol': 'ترامادول',
                'Codeine': 'كودايين',
                'Morphine': 'مورفين',
                'Gabapentin': 'غابابنتين',
                'Pregabalin': 'بريغابالين',
                'Amitriptyline': 'أميتريبتيلين',
                'Sertraline': 'سيرترالين',
                'Fluoxetine': 'فلوكسيتين',
                'Alprazolam': 'ألبرازولام',
                'Diazepam': 'ديازيبام',
                'Zolpidem': 'زولبيديم'
            },
            'en': {
                // الأدوية الموجودة في النظام
                'باراسيتامول': 'Paracetamol',
                'أموكسيسيلين': 'Amoxicillin',
                'أوميبرازول': 'Omeprazole',
                'ميتفورمين': 'Metformin',
                'أملوديبين': 'Amlodipine',
                
                // أدوية إضافية شائعة
                'إيبوبروفين': 'Ibuprofen',
                'أسبرين': 'Aspirin',
                'فيتامين د': 'Vitamin D',
                'فيتامين سي': 'Vitamin C',
                'أزيثروميسين': 'Azithromycin',
                'سيبروفلوكساسين': 'Ciprofloxacin',
                'سيفالكسين': 'Cephalexin',
                'كلاريثروميسين': 'Clarithromycin',
                'دوكسيسيكلين': 'Doxycycline',
                'أتورفاستاتين': 'Atorvastatin',
                'سيمفاستاتين': 'Simvastatin',
                'لوسارتان': 'Losartan',
                'إنالابريل': 'Enalapril',
                'بيسوبرولول': 'Bisoprolol',
                'كارفيديلول': 'Carvedilol',
                'فوروسيميد': 'Furosemide',
                'هيدروكلوروثيازيد': 'Hydrochlorothiazide',
                'وارفارين': 'Warfarin',
                'كلوبيدوغريل': 'Clopidogrel',
                'إنسولين': 'Insulin',
                'غليميبيريد': 'Glimepiride',
                'غليكلازيد': 'Gliclazide',
                'ليفوثيروكسين': 'Levothyroxine',
                'بريدنيزولون': 'Prednisolone',
                'ديكساميثازون': 'Dexamethasone',
                'سالبوتامول': 'Salbutamol',
                'مونتيلوكاست': 'Montelukast',
                'سيتريزين': 'Cetirizine',
                'لوراتادين': 'Loratadine',
                'رانيتيدين': 'Ranitidine',
                'بانتوبرازول': 'Pantoprazole',
                'إيزوميبرازول': 'Esomeprazole',
                'ميتوكلوبراميد': 'Metoclopramide',
                'دومبيريدون': 'Domperidone',
                'ديكلوفيناك': 'Diclofenac',
                'نابروكسين': 'Naproxen',
                'ترامادول': 'Tramadol',
                'كودايين': 'Codeine',
                'مورفين': 'Morphine',
                'غابابنتين': 'Gabapentin',
                'بريغابالين': 'Pregabalin',
                'أميتريبتيلين': 'Amitriptyline',
                'سيرترالين': 'Sertraline',
                'فلوكسيتين': 'Fluoxetine',
                'ألبرازولام': 'Alprazolam',
                'ديازيبام': 'Diazepam',
                'زولبيديم': 'Zolpidem'
            }
        };
        
        // محاولة الترجمة المباشرة
        let translated = drugNamesMap[this.currentLang][drugName];
        if (translated) return translated;
        
        // محاولة الترجمة بعد إزالة الجرعة والنص التجريبي
        const cleanName = drugName.replace(/\s*\d+\s*(mg|ملغ|g|غ|ml|مل).*$/i, '')
                                  .replace(/\s*\(تجريبي\)$/i, '')
                                  .trim();
        translated = drugNamesMap[this.currentLang][cleanName];
        
        return translated || drugName;
    }

    // ترجمة الفئات الدوائية (Categories)
    translateCategory(category) {
        if (!category) return category;
        
        // لا تترجم النصوص المختلطة التي تبدو كأسماء أشخاص
        if (this.isMixedText(category) && this.isPersonName(category)) {
            return category;
        }
        
        const categoryMap = {
            'ar': {
                // الفئات الموجودة في النظام
                'Analgesics': 'مسكنات',
                'Painkillers': 'مسكنات',
                'Pain Relief': 'مسكنات',
                'Antibiotics': 'مضادات حيوية',
                'Anti-inflammatory': 'مضادات التهاب',
                'Gastrointestinal': 'أدوية الجهاز الهضمي',
                'Digestive System': 'أدوية الجهاز الهضمي',
                'Diabetes': 'أدوية السكري',
                'Antidiabetic': 'أدوية السكري',
                'Cardiovascular': 'أدوية القلب والضغط',
                'Heart & Blood Pressure': 'أدوية القلب والضغط',
                'Cardiac': 'أدوية القلب والضغط',
                'Antihypertensive': 'خافضات الضغط',
                'Respiratory': 'أدوية الجهاز التنفسي',
                'Respiratory System': 'أدوية الجهاز التنفسي',
                'Allergy': 'أدوية الحساسية',
                'Antihistamines': 'مضادات الهيستامين',
                'Corticosteroids': 'كورتيزونات',
                'Steroids': 'كورتيزونات',
                'Neurological': 'أدوية الأعصاب',
                'Nervous System': 'أدوية الأعصاب',
                'Psychiatric': 'أدوية نفسية',
                'Antidepressants': 'مضادات الاكتئاب',
                'Anxiolytics': 'مضادات القلق',
                'Sedatives': 'مهدئات',
                'Endocrine': 'أدوية الغدد الصماء',
                'Hormones': 'هرمونات',
                'Thyroid': 'أدوية الغدة الدرقية',
                'Vitamins': 'فيتامينات',
                'Supplements': 'مكملات غذائية',
                'Anticoagulants': 'مضادات التخثر',
                'Blood Thinners': 'مميعات الدم',
                'Diuretics': 'مدرات البول',
                'Antacids': 'مضادات الحموضة',
                'Proton Pump Inhibitors': 'مثبطات مضخة البروتون',
                'H2 Blockers': 'مثبطات H2',
                'Bronchodilators': 'موسعات الشعب',
                'Statins': 'ستاتينات',
                'Beta Blockers': 'حاصرات بيتا',
                'ACE Inhibitors': 'مثبطات الإنزيم المحول',
                'ARBs': 'حاصرات مستقبلات الأنجيوتنسين',
                'Calcium Channel Blockers': 'حاصرات قنوات الكالسيوم'
            },
            'en': {
                // الفئات الموجودة في النظام
                'مسكنات': 'Analgesics',
                'مضادات حيوية': 'Antibiotics',
                'مضادات التهاب': 'Anti-inflammatory',
                'أدوية الجهاز الهضمي': 'Gastrointestinal',
                'أدوية السكري': 'Diabetes',
                'أدوية القلب والضغط': 'Cardiovascular',
                'خافضات الضغط': 'Antihypertensive',
                'أدوية الجهاز التنفسي': 'Respiratory',
                'أدوية الحساسية': 'Allergy',
                'مضادات الهيستامين': 'Antihistamines',
                'كورتيزونات': 'Corticosteroids',
                'أدوية الأعصاب': 'Neurological',
                'أدوية نفسية': 'Psychiatric',
                'مضادات الاكتئاب': 'Antidepressants',
                'مضادات القلق': 'Anxiolytics',
                'مهدئات': 'Sedatives',
                'أدوية الغدد الصماء': 'Endocrine',
                'هرمونات': 'Hormones',
                'أدوية الغدة الدرقية': 'Thyroid',
                'فيتامينات': 'Vitamins',
                'مكملات غذائية': 'Supplements',
                'مضادات التخثر': 'Anticoagulants',
                'مميعات الدم': 'Blood Thinners',
                'مدرات البول': 'Diuretics',
                'مضادات الحموضة': 'Antacids',
                'مثبطات مضخة البروتون': 'Proton Pump Inhibitors',
                'مثبطات H2': 'H2 Blockers',
                'موسعات الشعب': 'Bronchodilators',
                'ستاتينات': 'Statins',
                'حاصرات بيتا': 'Beta Blockers',
                'مثبطات الإنزيم المحول': 'ACE Inhibitors',
                'حاصرات مستقبلات الأنجيوتنسين': 'ARBs',
                'حاصرات قنوات الكالسيوم': 'Calcium Channel Blockers'
            }
        };
        
        return categoryMap[this.currentLang][category] || category;
    }
}

// إنشاء instance عام
const translator = new Translator();

// ترجمة الجندر في الجداول عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    // الانتظار قليلاً حتى يتم تحميل الترجمات
    setTimeout(() => {
        translateDynamicContent();
    }, 100);
});

// دالة لترجمة المحتوى الديناميكي
function translateDynamicContent() {
    // ترجمة الجندر في الجداول
    document.querySelectorAll('td').forEach(cell => {
        const text = cell.textContent.trim();
        if (text === 'ذكر' || text === 'أنثى' || text === 'Male' || text === 'Female') {
            cell.textContent = translator.translateGender(text);
        }
    });
    
    // ترجمة أسماء الأدوية الكاملة (اسم + جرعة)
    document.querySelectorAll('td strong, .drug-name, .medication-item, td').forEach(element => {
        let text = element.textContent.trim();
        
        // ترجمة اسم الدواء
        const translatedDrug = translator.translateCommonDrugNames(text);
        if (translatedDrug !== text) {
            text = translatedDrug;
        }
        
        // ترجمة الوحدات الطبية
        text = translator.translateMedicalUnits(text);
        
        // تحديث النص إذا تغير
        if (text !== element.textContent.trim()) {
            element.textContent = text;
        }
    });
    
    // ترجمة الفئات (Categories)
    document.querySelectorAll('.badge-info, td .badge, .category-badge').forEach(element => {
        const category = element.textContent.trim();
        const translated = translator.translateCategory(category);
        if (translated !== category) {
            element.textContent = translated;
        }
    });
    
    // ترجمة الجرعات في صفحات التفاصيل
    document.querySelectorAll('.drug-detail-value, .dosage-item').forEach(element => {
        let text = element.textContent.trim();
        text = translator.translateMedicalUnits(text);
        if (text !== element.textContent.trim()) {
            element.textContent = text;
        }
    });
}

// تصدير للاستخدام في ملفات أخرى
if (typeof window !== 'undefined') {
    window.translator = translator;
}
