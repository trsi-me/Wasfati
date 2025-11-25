"""إنشاء مستخدم الأدمن"""
from app import app
from models import db, User

with app.app_context():
    # التحقق من وجود المستخدم
    existing_user = User.query.filter_by(username='admin').first()
    
    if existing_user:
        print("المستخدم admin موجود بالفعل")
        print("تحديث كلمة المرور...")
        existing_user.set_password('admin123')
        db.session.commit()
        print("تم تحديث كلمة المرور بنجاح!")
    else:
        print("إنشاء مستخدم admin جديد...")
        admin = User(
            username='admin',
            full_name='المسؤول',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("تم إنشاء المستخدم بنجاح!")
    
    print("\nبيانات تسجيل الدخول:")
    print("اسم المستخدم: admin")
    print("كلمة المرور: admin123")
