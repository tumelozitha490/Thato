"""
ExpertConnect Africa — Production API Server
"""
import os, random, string, json
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename
from sqlalchemy import or_

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import db, User, Category, Professional, Service, Booking, Review, Message, Document, Invoice, Emergency, Portfolio, Notification

app = Flask(__name__, static_folder='../static', template_folder='../templates')

app.config.update(
    SECRET_KEY=os.environ.get('SECRET', 'eca_prod_2025'),
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance/expertconnect.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    JWT_SECRET_KEY=os.environ.get('JWT_SECRET', 'jwt_eca_2025'),
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=7),
    UPLOAD_FOLDER=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'),
    MAX_CONTENT_LENGTH=16*1024*1024
)

CORS(app)
jwt = JWTManager(app)
db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)

# ===== HELPERS =====
def gen_invoice():
    return f"ECA{datetime.now().strftime('%Y%m%d')}{''.join(random.choices(string.digits, k=5))}"

def recalc_rating(pro_id):
    reviews = Review.query.filter_by(pro_id=pro_id).all()
    if reviews:
        avg = sum(r.rating for r in reviews) / len(reviews)
        pro = db.session.get(Professional, pro_id)
        if pro:
            pro.rating, pro.reviews_count = round(avg, 1), len(reviews)
            db.session.commit()

# ===== SEED =====
def seed():
    if Category.query.first():
        return
    categories = [
        ('Healthcare', '🩺', 'Doctors, dentists, psychologists, nurses'),
        ('Legal Services', '⚖️', 'Lawyers, notaries, consultants'),
        ('Education', '📚', 'Tutors, coaches, mentors'),
        ('Business Services', '💼', 'Accountants, tax, financial'),
        ('Home Services', '🏠', 'Electricians, plumbers, handymen'),
        ('Technology', '💻', 'Developers, IT support, designers'),
        ('Fitness & Wellness', '💪', 'Trainers, dietitians, physios'),
        ('Financial Advisory', '📈', 'Investment, retirement, estate'),
    ]
    for n, i, d in categories:
        db.session.add(Category(name=n, icon=i, description=d))
    db.session.flush()

    pros = [
        ('amina@demo.com','Amina','Osei','Healthcare','General Practitioner',
         'Experienced GP with 12 years in family medicine.',350,300,500,4.9,127,500,850,'Sandton, Johannesburg','Osei Medical',
         [('General Consultation','In-person checkup',350,30),('Video Consultation','Online consultation',300,30)]),
        ('bongani@demo.com','Bongani','Ndlovu','Legal Services','Corporate Lawyer',
         'Corporate law specialist with 15 years experience.',500,450,700,4.8,89,300,600,'Cape Town CBD','Ndlovu & Associates',
         [('Legal Consultation','1-hour consultation',500,60),('Contract Review','Review and advice',800,60)]),
        ('sarah@demo.com','Sarah','Mensah','Education','Mathematics Tutor',
         'Math educator making complex concepts accessible.',250,200,350,4.9,203,150,1200,'Pretoria East','Mensah Math Academy',
         [('1-on-1 Tutoring','60-minute session',250,60),('Exam Prep','Intensive preparation',400,120)]),
        ('ngozi@demo.com','Ngozi','Okonkwo','Healthcare','Psychologist',
         'Clinical psychologist specializing in CBT.',500,450,700,4.9,112,350,900,'Rosebank, Johannesburg','MindWell Psychology',
         [('Therapy Session','50-minute session',500,50),('Online Therapy','Video call session',450,50)]),
        ('peter@demo.com','Peter','Adeyemi','Business Services','Tax Consultant',
         'Tax consultant helping businesses optimize positions.',450,400,650,4.8,156,600,1100,'Durban CBD','Adeyemi Tax Advisory',
         [('Tax Consultation','1-hour consultation',450,60),('Tax Return','Individual filing',800,120)]),
        ('lerato@demo.com','Lerato','Dlamini','Fitness & Wellness','Personal Trainer',
         'Certified trainer for holistic wellness.',300,250,400,4.9,178,200,1500,'Umhlanga, Durban','FitLife Durban',
         [('Personal Training','1-hour session',300,60),('Online Coaching','Monthly program',1500,30)]),
        ('tendai@demo.com','Tendai','Murapa','Technology','Software Developer',
         "Full-stack developer building Africa's digital future.",600,600,800,4.7,64,80,200,'Midrand, Johannesburg','TechAfrik Solutions',
         [('Web Development','Custom website',5000,480),('Tech Consultation','1-hour consult',600,60)]),
        ('thabo@demo.com','Thabo','Molefe','Home Services','Electrician',
         'Licensed electrician with 11 years experience.',350,200,350,4.6,73,250,600,'Bloemfontein','Molefe Electrical',
         [('Electrical Inspection','Full property check',350,60),('Solar Setup','Panel installation',5000,480)]),
    ]
    for email, fn, ln, cat_name, spec, bio, pr, opr, hpr, rt, rv, pt, bk, addr, bus, svcs in pros:
        cat = Category.query.filter_by(name=cat_name).first()
        user = User(email=email, first_name=fn, last_name=ln,
                    phone=f"+27{random.randint(70,84)}{random.randint(1000000,9999999)}",
                    role='professional', verified=True)
        user.set_password('demo123')
        db.session.add(user)
        db.session.flush()
        prof = Professional(user_id=user.id, category_id=cat.id, specialty=spec, bio=bio,
                           price=pr, online_price=opr, house_price=hpr, rating=rt,
                           reviews_count=rv, patients_count=pt, bookings_count=bk,
         address=addr, business=bus, verified=True, experience=random.randint(5,15),
                           status='available', has_video=True, has_voice=True, has_chat=True, has_house=True)
        db.session.add(prof)
        db.session.flush()
        for sn, sd, sp, sdur in svcs:
            db.session.add(Service(pro_id=prof.id, name=sn, description=sd, price=sp, duration=sdur))

    for name, cat, phone in [('Netcare 911','ambulance','082 911'),('ER24','ambulance','084 124'),
                              ('SAPS','police','10111'),('Fire & Rescue','fire','10177'),
                              ('GBV Helpline','counselling','0800 428 428'),
                              ('Suicide Helpline','counselling','0800 567 567')]:
        db.session.add(Emergency(name=name, category=cat, phone=phone, available_24h=True))

    db.session.commit()
    print('✓ Database ready')

# ===== FRONTEND =====
@app.route('/')
def index():
    return send_from_directory('../templates', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    dirs = {'css': '../static/css', 'js': '../static/js', 'uploads': '../uploads'}
    for prefix, directory in dirs.items():
        if path.startswith(prefix):
            try:
                return send_from_directory(directory, path.replace(prefix + '/', ''))
            except:
                pass
    return send_from_directory('../templates', 'index.html')

# ===== AUTH =====
@app.route('/api/auth/register', methods=['POST'])
def register():
    d = request.json
    if not all(d.get(f) for f in ['email','password','first_name','last_name']):
        return jsonify(error='Missing required fields'), 400
    if User.query.filter_by(email=d['email']).first():
        return jsonify(error='Email already registered'), 409
    user = User(email=d['email'], first_name=d['first_name'], last_name=d['last_name'],
                phone=d.get('phone'), role=d.get('role','client'), province=d.get('province'))
    user.set_password(d['password'])
    db.session.add(user)
    db.session.flush()
    if user.role == 'professional' and d.get('category_id'):
        prof = Professional(user_id=user.id, category_id=d['category_id'],
                           specialty=d.get('specialty',''), price=d.get('price',0),
                           address=d.get('address'), business=d.get('business'))
        db.session.add(prof)
    db.session.add(Notification(user_id=user.id, title='Welcome!', message='Account created successfully.', type='system'))
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify(token=token, user=user.serialize()), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    d = request.json
    user = User.query.filter_by(email=d.get('email','')).first()
    if not user or not user.check_password(d.get('password','')):
        return jsonify(error='Invalid credentials'), 401
    token = create_access_token(identity=str(user.id))
    return jsonify(token=token, user=user.serialize())

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify(error='Not found'), 404
    data = user.serialize()
    if user.role == 'professional':
        prof = Professional.query.filter_by(user_id=user.id).first()
        if prof:
            data['professional'] = prof.serialize()
    data['unread'] = Notification.query.filter_by(user_id=user.id, read=False).count()
    return jsonify(data)

# ===== DATA =====
@app.route('/api/categories')
def get_categories():
    return jsonify([c.serialize() for c in Category.query.all()])

@app.route('/api/professionals')
def get_professionals():
    q = Professional.query
    cat = request.args.get('category_id')
    if cat: q = q.filter_by(category_id=int(cat))
    s = request.args.get('search','').lower()
    if s:
        q = q.join(User).filter(or_(User.first_name.ilike(f'%{s}%'), User.last_name.ilike(f'%{s}%'),
                                     Professional.specialty.ilike(f'%{s}%'), Professional.business.ilike(f'%{s}%')))
    sort = request.args.get('sort')
    if sort == 'rating': q = q.order_by(Professional.rating.desc())
    elif sort == 'price_low': q = q.order_by(Professional.price.asc())
    elif sort == 'price_high': q = q.order_by(Professional.price.desc())
    else: q = q.order_by(Professional.verified.desc(), Professional.rating.desc())
    return jsonify([p.serialize() for p in q.all()])

@app.route('/api/professionals/<int:id>')
def get_professional(id):
    pro = db.session.get(Professional, id)
    if not pro: return jsonify(error='Not found'), 404
    data = pro.serialize()
    data['reviews'] = [r.serialize() for r in Review.query.filter_by(pro_id=id).order_by(Review.created_at.desc()).limit(10).all()]
    return jsonify(data)

@app.route('/api/search')
def search():
    q = request.args.get('q','').lower()
    results = {'professionals': []}
    if q:
        pros = Professional.query.join(User).filter(or_(User.first_name.ilike(f'%{q}%'), User.last_name.ilike(f'%{q}%'),
            Professional.specialty.ilike(f'%{q}%'), Professional.bio.ilike(f'%{q}%'))).limit(10).all()
        results['professionals'] = [p.serialize() for p in pros]
    return jsonify(results)

# ===== BOOKINGS =====
@app.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    user = db.session.get(User, int(get_jwt_identity()))
    if user.role == 'professional':
        prof = Professional.query.filter_by(user_id=user.id).first()
        q = Booking.query.filter_by(pro_id=prof.id) if prof else Booking.query.filter_by(pro_id=0)
    else:
        q = Booking.query.filter_by(client_id=user.id)
    s = request.args.get('status')
    if s: q = q.filter_by(status=s)
    return jsonify([b.serialize() for b in q.order_by(Booking.date.desc()).all()])

@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    uid = int(get_jwt_identity())
    d = request.json
    pro = db.session.get(Professional, d.get('professional_id'))
    if not pro: return jsonify(error='Not found'), 404
    svc = db.session.get(Service, d.get('service_id')) if d.get('service_id') else None
    price = svc.price if svc else pro.price
    if d.get('type') == 'online': price = pro.online_price or price
    elif d.get('type') == 'house': price = pro.house_price or price * 1.5
    b = Booking(client_id=uid, pro_id=pro.id, service_id=svc.id if svc else None,
                type=d.get('type','online'), consult=d.get('consult','video'), status='pending', price=price,
                date=datetime.strptime(d['date'],'%Y-%m-%d').date(), time=d.get('time','09:00'),
                duration=d.get('duration',30), notes=d.get('notes'), family=d.get('family'))
    db.session.add(b)
    pro.bookings_count = (pro.bookings_count or 0) + 1
    pro.patients_count = (pro.patients_count or 0) + 1
    db.session.add(Notification(user_id=pro.user_id, title='New booking!', message=f'Booking for {d["date"]}', type='booking'))
    db.session.flush()
    inv = Invoice(number=gen_invoice(), booking_id=b.id, client_id=uid, pro_id=pro.id, subtotal=price, fee=round(price*0.1,2), total=price)
    db.session.add(inv)
    db.session.commit()
    return jsonify(booking=b.serialize(), invoice=inv.serialize()), 201

@app.route('/api/bookings/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_booking(id):
    d = request.json
    b = db.session.get(Booking, id)
    if not b: return jsonify(error='Not found'), 404
    b.status = d['status']
    db.session.add(Notification(user_id=b.client_id, title=f'Booking {d["status"]}!', message=f'Status updated to {d["status"]}', type='booking'))
    db.session.commit()
    return jsonify(b.serialize())

# ===== REVIEWS =====
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    pid = request.args.get('professional_id')
    q = Review.query
    if pid: q = q.filter_by(pro_id=int(pid))
    return jsonify([r.serialize() for r in q.order_by(Review.created_at.desc()).limit(50).all()])

@app.route('/api/reviews', methods=['POST'])
@jwt_required()
def create_review():
    uid = int(get_jwt_identity())
    d = request.json
    b = db.session.get(Booking, d.get('booking_id'))
    if not b or b.client_id != uid: return jsonify(error='Invalid'), 400
    if Review.query.filter_by(booking_id=b.id).first(): return jsonify(error='Already reviewed'), 409
    r = Review(booking_id=b.id, pro_id=b.pro_id, client_id=uid, rating=d['rating'], comment=d.get('comment'))
    db.session.add(r)
    db.session.commit()
    recalc_rating(b.pro_id)
    return jsonify(r.serialize()), 201

# ===== MESSAGES =====
@app.route('/api/messages/<int:other>', methods=['GET'])
@jwt_required()
def get_messages(other):
    uid = int(get_jwt_identity())
    msgs = Message.query.filter(or_(Message.sender_id==uid, Message.receiver_id==uid)).order_by(Message.created_at.asc()).limit(100).all()
    return jsonify([m.serialize() for m in msgs])

@app.route('/api/messages/<int:other>', methods=['POST'])
@jwt_required()
def send_message(other):
    uid = int(get_jwt_identity())
    d = request.json
    m = Message(sender_id=uid, receiver_id=other, content=d['message'])
    db.session.add(m)
    db.session.commit()
    return jsonify(m.serialize()), 201

# ===== DOCUMENTS =====
@app.route('/api/documents', methods=['GET'])
@jwt_required()
def get_docs():
    uid = int(get_jwt_identity())
    return jsonify([d.serialize() for d in Document.query.filter_by(user_id=uid).order_by(Document.created_at.desc()).all()])

@app.route('/api/documents', methods=['POST'])
@jwt_required()
def upload_doc():
    uid = int(get_jwt_identity())
    if 'file' not in request.files: return jsonify(error='No file'), 400
    f = request.files['file']
    fn = secure_filename(f"{uid}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
    d = Document(user_id=uid, name=f.filename, type=request.form.get('type','other'), url=fn, size=0)
    db.session.add(d)
    db.session.commit()
    return jsonify(d.serialize()), 201

# ===== INVOICES =====
@app.route('/api/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    uid = int(get_jwt_identity())
    user = db.session.get(User, uid)
    if user.role == 'professional':
        prof = Professional.query.filter_by(user_id=uid).first()
        invs = Invoice.query.filter_by(pro_id=prof.id).order_by(Invoice.created_at.desc()).all() if prof else []
    else:
        invs = Invoice.query.filter_by(client_id=uid).order_by(Invoice.created_at.desc()).all()
    return jsonify([i.serialize() for i in invs])

# ===== EMERGENCY =====
@app.route('/api/emergency')
def get_emergency():
    q = Emergency.query
    c = request.args.get('category')
    if c: q = q.filter_by(category=c)
    return jsonify([e.serialize() for e in q.all()])

# ===== NOTIFICATIONS =====
@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    uid = int(get_jwt_identity())
    return jsonify([n.serialize() for n in Notification.query.filter_by(user_id=uid).order_by(Notification.created_at.desc()).limit(50).all()])

@app.route('/api/notifications/read', methods=['PUT'])
@jwt_required()
def mark_read():
    uid = int(get_jwt_identity())
    Notification.query.filter_by(user_id=uid, read=False).update({'read': True})
    db.session.commit()
    return jsonify(success=True)

# ===== AI ASSISTANT =====
@app.route('/api/ai/assist', methods=['POST'])
@jwt_required()
def ai_assist():
    msg = request.json.get('message','').lower()
    kw = {
        'anxious|anxiety|stress|depress|depression|therapy|counsel|mental|sad|worried|psycholog': 'Psychologist',
        'headache|fever|pain|sick|cold|flu|doctor|gp|checkup|medical': 'General Practitioner',
        'tooth|dental|teeth|gum|mouth|braces': 'Dentist',
        'law|lawyer|legal|sue|court|contract|divorce|custody': 'Corporate Lawyer',
        'tax|account|audit|financial|money|invest|bookkeep': 'Tax Consultant',
        'tutor|math|science|english|study|exam|school|university': 'Mathematics Tutor',
        'fit|gym|exercise|weight|diet|nutrition|train|workout': 'Personal Trainer',
        'electric|wiring|solar|power|light|switch|plug': 'Electrician',
        'code|website|app|software|tech|it|programming|developer': 'Software Developer',
        'career|job|resume|cv|interview': 'Career Coach',
    }
    for keys, cat_name in kw.items():
        if any(k in msg for k in keys.split('|')):
            cat = Category.query.filter(Category.name.ilike(f'%{cat_name}%')).first()
            if cat:
                pros = Professional.query.filter_by(category_id=cat.id, status='available').order_by(Professional.rating.desc()).limit(3).all()
                if pros:
                    return jsonify(response=f"I found {len(pros)} {cat_name} professionals available.",
                                 suggestion=cat_name, professionals=[dict(id=p.id, name=p.user.first_name+' '+p.user.last_name,
                                 specialty=p.specialty, rating=p.rating, price=p.price, status=p.status) for p in pros])
    return jsonify(response="Tell me what you need (e.g., 'toothache', 'legal advice', 'anxious').",
                   suggestion=None, professionals=[])

# ===== INIT =====
with app.app_context():
    db.create_all()
    seed()

if __name__ == '__main__':
    print(f"""
    ╔══════════════════════════════════╗
    ║  ExpertConnect Africa            ║
    ║  http://localhost:5001           ║
    ║  Demo: amina@demo.com / demo123  ║
    ╚══════════════════════════════════╝
    """)
    app.run(debug=True, port=5001, host='0.0.0.0')