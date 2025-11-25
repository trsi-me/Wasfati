import os

# مسار المشروع الأساسي
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """إعدادات التطبيق الأساسية"""
    
    # مفتاح سري للجلسات
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wasfati-secret-key-2024-medical-prescription'
    
    # مسار قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'wasfati.db')
    
    # تعطيل تتبع التعديلات لتحسين الأداء
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # حجم الصفحة للعرض
    ITEMS_PER_PAGE = 20
    
    # إعدادات التحميل
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # المسارات الثابتة
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
