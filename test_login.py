"""اختبار تسجيل الدخول"""
from app import app
from models import db, User

with app.app_context():
    # البحث عن المستخدم
    user = User.query.filter_by(username='admin').first()
    
    if user:
        print(f"تم العثور على المستخدم: {user.username}")
        print(f"الاسم الكامل: {user.full_name}")
        print(f"نشط: {user.is_active}")
        
        # اختبار كلمة المرور
        if user.check_password(''):
            print("\n✓ كلمة المرور صحيحة!")
        else:
            print("\n✗ كلمة المرور غير صحيحة!")
    else:
        print("لم يتم العثور على المستخدم admin")
        print("\nجميع المستخدمين في قاعدة البيانات:")
        for u in User.query.all():
            print(f"  - {u.username}")
