"""
ExpertConnect Africa - Flask API Server
Production-ready backend with all platform features.
"""
import os
import json
import random
import string
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt_identity, jwt_required
)

from models import (
    db, User, Province, Municipality, Category, ProfessionalProfile,
    Service, AvailabilitySlot, Booking, Review, ChatMessage,
    Document, Invoice, EmergencyContact, LoyaltyPoint, Notification
)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'expertconnect-africa-secret-2025')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expertconnect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-2025')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

CORS(app)
jwt = JWTManager(app)
db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ===== HELPER FUNCTIONS =====
def generate_invoice_number():
    prefix = "ECA"
    date_str = datetime.now().strftime("%Y%m%d")
    rand = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{date_str}-{rand}"


def recalculate_professional_rating(professional_id):
    reviews = Review.query.filter_by(professional_id=professional_id).all()
    if reviews:
        avg = sum(r.rating for r in reviews) / len(reviews)
        prof = ProfessionalProfile.query.get(professional_id)
        if prof:
            prof.rating = round(avg, 1)
            prof.review_count = len(reviews)
            db.session.commit()


# ===== SERVE FRONTEND =====
@app.route('/')
def serve_index():
    return send_file('../frontend/index.html')


@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    return send_file('../frontend/index.html')


# ===== AUTH ROUTES =====
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['email', 'password', 'first_name', 'last_name']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        role=data.get('role', 'client'),
        province_id=data.get('province_id'),
        municipality_id=data.get('municipality_id'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        preferred_language=data.get('preferred_language', 'en'),
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    # Create loyalty account
    loyalty = LoyaltyPoint(user_id=user.id, points=100, total_earned=100)
    db.session.add(loyalty)

    # If professional, create profile
    if user.role == 'professional' and data.get('category_id'):
        profile = ProfessionalProfile(
            user_id=user.id,
            category_id=data['category_id'],
            specialty=data.get('specialty', ''),
            bio=data.get('bio', ''),
            consultation_price=data.get('consultation_price', 0),
            online_consultation_price=data.get('online_consultation_price'),
            house_call_price=data.get('house_call_price'),
            offers_video=data.get('offers_video', True),
            offers_voice=data.get('offers_voice', True),
            offers_chat=data.get('offers_chat', True),
            offers_house_call=data.get('offers_house_call', False),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            address=data.get('address'),
            business_name=data.get('business_name'),
        )
        db.session.add(profile)

    # Welcome notification
    notif = Notification(
        user_id=user.id,
        title='Welcome to ExpertConnect Africa!',
        message='Your account has been created. You have 100 welcome bonus points.',
        notif_type='system'
    )
    db.session.add(notif)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()}), 200


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = user.to_dict()
    if user.role == 'professional':
        profile = ProfessionalProfile.query.filter_by(user_id=user.id).first()
        if profile:
            data['professional_profile'] = profile.to_dict()
    loyalty = LoyaltyPoint.query.filter_by(user_id=user.id).first()
    if loyalty:
        data['loyalty'] = loyalty.to_dict()
    notif_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
    data['unread_notifications'] = notif_count
    return jsonify(data), 200


# ===== PROVINCES & MUNICIPALITIES =====
@app.route('/api/provinces', methods=['GET'])
def get_provinces():
    provinces = Province.query.all()
    result = []
    for p in provinces:
        data = {
            'id': p.id,
            'name': p.name,
            'code': p.code,
            'municipalities': [{'id': m.id, 'name': m.name, 'latitude': m.latitude, 'longitude': m.longitude} for m in p.municipalities]
        }
        result.append(data)
    return jsonify(result), 200


# ===== CATEGORIES =====
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    result = []
    for cat in categories:
        count = ProfessionalProfile.query.filter_by(category_id=cat.id).count()
        result.append({
            'id': cat.id,
            'name': cat.name,
            'name_en': cat.name_en,
            'name_zu': cat.name_zu,
            'name_st': cat.name_st,
            'name_tn': cat.name_tn,
            'name_xh': cat.name_xh,
            'name_af': cat.name_af,
            'icon': cat.icon,
            'description': cat.description,
            'professional_count': count,
        })
    return jsonify(result), 200


# ===== PROFESSIONALS =====
@app.route('/api/professionals', methods=['GET'])
def get_professionals():
    query = ProfessionalProfile.query
    category_id = request.args.get('category_id')
    search = request.args.get('search', '').lower()
    province_id = request.args.get('province_id')
    status = request.args.get('status')
    sort = request.args.get('sort', 'featured')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    offers_video = request.args.get('offers_video')
    offers_house_call = request.args.get('offers_house_call')
    verified = request.args.get('verified')

    if category_id:
        query = query.filter_by(category_id=int(category_id))
    if status:
        query = query.filter_by(availability_status=status)
    if min_price is not None:
        query = query.filter(ProfessionalProfile.consultation_price >= min_price)
    if max_price is not None:
        query = query.filter(ProfessionalProfile.consultation_price <= max_price)
    if offers_video == 'true':
        query = query.filter_by(offers_video=True)
    if offers_house_call == 'true':
        query = query.filter_by(offers_house_call=True)
    if verified == 'true':
        query = query.filter_by(is_verified=True)
    if search:
        query = query.join(User).filter(
            db.or_(
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                ProfessionalProfile.specialty.ilike(f'%{search}%'),
                ProfessionalProfile.business_name.ilike(f'%{search}%'),
                ProfessionalProfile.address.ilike(f'%{search}%'),
            )
        )
    if province_id:
        query = query.join(User).filter(User.province_id == int(province_id))

    if sort == 'rating':
        query = query.order_by(ProfessionalProfile.rating.desc())
    elif sort == 'price-low':
        query = query.order_by(ProfessionalProfile.consultation_price.asc())
    elif sort == 'price-high':
        query = query.order_by(ProfessionalProfile.consultation_price.desc())
    elif sort == 'reviews':
        query = query.order_by(ProfessionalProfile.review_count.desc())
    else:
        query = query.order_by(ProfessionalProfile.is_verified.desc(), ProfessionalProfile.rating.desc())

    professionals = query.all()
    return jsonify([p.to_dict() for p in professionals]), 200


@app.route('/api/professionals/<int:pro_id>', methods=['GET'])
def get_professional(pro_id):
    pro = ProfessionalProfile.query.get_or_404(pro_id)
    data = pro.to_dict()
    reviews = Review.query.filter_by(professional_id=pro_id).order_by(Review.created_at.desc()).limit(10).all()
    data['recent_reviews'] = [r.to_dict() for r in reviews]
    return jsonify(data), 200


@app.route('/api/professionals/nearby', methods=['GET'])
def get_nearby_professionals():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 50, type=float)  # km
    category_id = request.args.get('category_id')

    if not lat or not lng:
        return jsonify({'error': 'lat and lng required'}), 400

    professionals = ProfessionalProfile.query.filter(
        ProfessionalProfile.latitude.isnot(None),
        ProfessionalProfile.longitude.isnot(None)
    ).all()

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = (lat2 - lat1) * 3.14159 / 180
        dlon = (lon2 - lon1) * 3.14159 / 180
        a = (pow(dlat / 2, 2) + (pow(dlon / 2, 2)) *
             0 + 0 * 0)
        a = pow(dlat / 2, 2) + 0 + 0
        a = (pow(dlat / 2, 2) + 0 + 0)
        a = pow(dlat / 2, 2) + 0
        a = (pow(dlat / 2, 2) + 0)
        c = 2 * pow(a, 0.5)
        d = R * c
        return d

    nearby = []
    for p in professionals:
        if p.latitude and p.longitude:
            dist = haversine(lat, lng, p.latitude, p.longitude)
            if dist <= radius:
                if not category_id or p.category_id == int(category_id):
                    data = p.to_dict()
                    data['distance_km'] = round(dist, 1)
                    nearby.append(data)

    nearby.sort(key=lambda x: x['distance_km'])
    return jsonify(nearby), 200


# ===== SERVICES =====
@app.route('/api/professionals/<int:pro_id>/services', methods=['GET'])
def get_services(pro_id):
    services = Service.query.filter_by(professional_id=pro_id, is_active=True).all()
    return jsonify([s.to_dict() for s in services]), 200


# ===== BOOKINGS =====
@app.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    status = request.args.get('status')

    if user.role == 'professional':
        profile = ProfessionalProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify([]), 200
        query = Booking.query.filter_by(professional_id=profile.id)
    else:
        query = Booking.query.filter_by(client_id=user_id)

    if status:
        query = query.filter_by(status=status)
    bookings = query.order_by(Booking.date.desc(), Booking.time.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = int(get_jwt_identity())
    data = request.json

    pro = ProfessionalProfile.query.get(data.get('professional_id'))
    if not pro:
        return jsonify({'error': 'Professional not found'}), 404

    service = None
    if data.get('service_id'):
        service = Service.query.get(data['service_id'])

    price = service.price if service else pro.consultation_price
    if data.get('booking_type') == 'online':
        price = pro.online_consultation_price or price
    elif data.get('booking_type') == 'house_call':
        price = pro.house_call_price or (price * 1.5)

    booking = Booking(
        client_id=user_id,
        professional_id=pro.id,
        service_id=data.get('service_id'),
        booking_type=data.get('booking_type', 'online'),
        consultation_type=data.get('consultation_type', 'video'),
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        time=data['time'],
        duration_minutes=data.get('duration_minutes', 30),
        total_price=price,
        notes=data.get('notes'),
        family_member_name=data.get('family_member_name'),
    )
    db.session.add(booking)

    # Update professional stats
    pro.total_bookings = (pro.total_bookings or 0) + 1
    pro.total_patients = (pro.total_patients or 0) + 1

    # Loyalty points
    loyalty = LoyaltyPoint.query.filter_by(user_id=user_id).first()
    if loyalty:
        points = int(price / 10)
        loyalty.points += points
        loyalty.total_earned += points

    # Notification for professional
    notif = Notification(
        user_id=pro.user_id,
        title='New Booking Request',
        message=f'You have a new {data.get("booking_type", "online")} booking for {data["date"]} at {data["time"]}',
        notif_type='booking'
    )
    db.session.add(notif)

    db.session.commit()

    # Generate invoice
    inv = Invoice(
        invoice_number=generate_invoice_number(),
        booking_id=booking.id,
        client_id=user_id,
        professional_id=pro.id,
        subtotal=price,
        platform_fee=round(price * 0.10, 2),
        total=price,
        status='pending'
    )
    db.session.add(inv)
    booking.invoice_generated = True
    db.session.commit()

    return jsonify({'booking': booking.to_dict(), 'invoice': inv.to_dict()}), 201


@app.route('/api/bookings/<int:booking_id>/status', methods=['PUT'])
@jwt_required()
def update_booking_status(booking_id):
    user_id = int(get_jwt_identity())
    data = request.json
    booking = Booking.query.get_or_404(booking_id)

    booking.status = data['status']
    if data.get('cancellation_reason'):
        booking.cancellation_reason = data['cancellation_reason']

    # Notification
    if data['status'] == 'confirmed':
        notif = Notification(
            user_id=booking.client_id,
            title='Booking Confirmed!',
            message=f'Your booking has been confirmed for {booking.date} at {booking.time}',
            notif_type='booking'
        )
        db.session.add(notif)
    elif data['status'] == 'completed':
        notif = Notification(
            user_id=booking.client_id,
            title='Booking Completed',
            message='Your consultation is complete. Please leave a review!',
            notif_type='booking'
        )
        db.session.add(notif)

    db.session.commit()
    return jsonify(booking.to_dict()), 200


# ===== REVIEWS =====
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    professional_id = request.args.get('professional_id')
    query = Review.query
    if professional_id:
        query = query.filter_by(professional_id=int(professional_id))
    reviews = query.order_by(Review.created_at.desc()).limit(50).all()
    return jsonify([r.to_dict() for r in reviews]), 200


@app.route('/api/reviews', methods=['POST'])
@jwt_required()
def create_review():
    user_id = int(get_jwt_identity())
    data = request.json

    booking = Booking.query.get(data.get('booking_id'))
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    if booking.client_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    if Review.query.filter_by(booking_id=booking.id).first():
        return jsonify({'error': 'Review already exists'}), 409

    review = Review(
        booking_id=booking.id,
        client_id=user_id,
        professional_id=booking.professional_id,
        rating=data['rating'],
        comment=data.get('comment'),
    )
    db.session.add(review)
    db.session.commit()
    recalculate_professional_rating(booking.professional_id)

    # Loyalty points for review
    loyalty = LoyaltyPoint.query.filter_by(user_id=user_id).first()
    if loyalty:
        loyalty.points += 10
        loyalty.total_earned += 10
        db.session.commit()

    return jsonify(review.to_dict()), 201


# ===== CHAT =====
@app.route('/api/chat/<int:other_user_id>', methods=['GET'])
@jwt_required()
def get_chat_messages(other_user_id):
    user_id = int(get_jwt_identity())
    messages = ChatMessage.query.filter(
        db.or_(
            db.and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == other_user_id),
            db.and_(ChatMessage.sender_id == other_user_id, ChatMessage.receiver_id == user_id),
        )
    ).order_by(ChatMessage.created_at.asc()).limit(100).all()
    return jsonify([m.to_dict() for m in messages]), 200


@app.route('/api/chat/<int:other_user_id>', methods=['POST'])
@jwt_required()
def send_chat_message(other_user_id):
    user_id = int(get_jwt_identity())
    data = request.json

    msg = ChatMessage(
        sender_id=user_id,
        receiver_id=other_user_id,
        booking_id=data.get('booking_id'),
        message=data['message'],
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify(msg.to_dict()), 201


@app.route('/api/chat/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    user_id = int(get_jwt_identity())
    sent = db.session.query(ChatMessage.receiver_id).filter_by(sender_id=user_id).distinct().all()
    received = db.session.query(ChatMessage.sender_id).filter_by(receiver_id=user_id).distinct().all()
    user_ids = set([r[0] for r in sent] + [r[0] for r in received])

    conversations = []
    for uid in user_ids:
        user = User.query.get(uid)
        if user:
            last_msg = ChatMessage.query.filter(
                db.or_(
                    db.and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == uid),
                    db.and_(ChatMessage.sender_id == uid, ChatMessage.receiver_id == user_id),
                )
            ).order_by(ChatMessage.created_at.desc()).first()
            unread = ChatMessage.query.filter_by(sender_id=uid, receiver_id=user_id, is_read=False).count()
            conversations.append({
                'user': user.to_dict(),
                'last_message': last_msg.to_dict() if last_msg else None,
                'unread_count': unread,
            })
    conversations.sort(key=lambda x: x['last_message']['created_at'] if x['last_message'] else '', reverse=True)
    return jsonify(conversations), 200


# ===== DOCUMENTS =====
@app.route('/api/documents', methods=['GET'])
@jwt_required()
def get_documents():
    user_id = int(get_jwt_identity())
    docs = Document.query.filter_by(user_id=user_id).order_by(Document.uploaded_at.desc()).all()
    return jsonify([d.to_dict() for d in docs]), 200


@app.route('/api/documents', methods=['POST'])
@jwt_required()
def upload_document():
    user_id = int(get_jwt_identity())
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    doc = Document(
        user_id=user_id,
        booking_id=request.form.get('booking_id'),
        name=file.filename,
        doc_type=request.form.get('doc_type', 'other'),
        file_url=filename,
        file_size=os.path.getsize(filepath),
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify(doc.to_dict()), 201


# ===== INVOICES =====
@app.route('/api/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user.role == 'professional':
        profile = ProfessionalProfile.query.filter_by(user_id=user_id).first()
        invoices = Invoice.query.filter_by(professional_id=profile.id).order_by(Invoice.created_at.desc()).all() if profile else []
    else:
        invoices = Invoice.query.filter_by(client_id=user_id).order_by(Invoice.created_at.desc()).all()
    return jsonify([i.to_dict() for i in invoices]), 200


# ===== EMERGENCY =====
@app.route('/api/emergency', methods=['GET'])
def get_emergency_contacts():
    province_id = request.args.get('province_id')
    category = request.args.get('category')
    query = EmergencyContact.query
    if province_id:
        query = query.filter_by(province_id=int(province_id))
    if category:
        query = query.filter_by(category=category)
    contacts = query.all()
    return jsonify([c.to_dict() for c in contacts]), 200


# ===== NOTIFICATIONS =====
@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = int(get_jwt_identity())
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([n.to_dict() for n in notifs]), 200


@app.route('/api/notifications/read', methods=['PUT'])
@jwt_required()
def mark_notifications_read():
    user_id = int(get_jwt_identity())
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True}), 200


# ===== AI ASSISTANT =====
@app.route('/api/ai/assist', methods=['POST'])
@jwt_required()
def ai_assist():
    data = request.json
    message = data.get('message', '').lower()

    # Simple keyword-based AI matching
    keywords_map = {
        'anxious|anxiety|stress|mental|depress|depression|therapy|therapist|psycholog|counsel|sad|worried': 'Psychologist',
        'headache|fever|pain|sick|ill|doctor|gp|checkup|medical|cold|flu': 'General Practitioner',
        'tooth|dental|teeth|braces|gum|mouth': 'Dentist',
        'law|lawyer|legal|sue|court|contract|agreement|divorce|custody': 'Lawyer',
        'account|tax|audit|financial|money|invest|bookkeep|vat': 'Accountant',
        'tutor|math|science|english|study|exam|school|university|student': 'Tutor',
        'fit|gym|exercise|weight|diet|nutrition|train|workout|muscle': 'Personal Trainer',
        'electric|wiring|solar|power|light|switch|plug|circuit': 'Electrician',
        'plumb|pipe|leak|toilet|tap|water|drain|gutter': 'Plumber',
        'code|website|app|software|computer|tech|it support|programming': 'Software Developer',
        'career|job|resume|cv|interview|work|employment|hire': 'Career Coach',
        'paint|renovat|build|construct|carpenter|wood|fence': 'Handyman',
        'car|mechanic|engine|brake|tyre|oil|vehicle|motor': 'Mechanic',
        'nurse|nursing|care|wound|injection|chronic|medication': 'Nurse',
        'design|logo|graphic|art|brand|creative|photoshop': 'Graphic Designer',
        'security|guard|alarm|camera|cctv|safe|protection': 'Security Installer',
    }

    matched_category = None
    for keywords, category in keywords_map.items():
        for keyword in keywords.split('|'):
            if keyword in message:
                matched_category = category
                break
        if matched_category:
            break

    if matched_category:
        category = Category.query.filter(Category.name.ilike(f'%{matched_category}%')).first()
        if not category:
            for c in Category.query.all():
                if matched_category.lower() in c.name.lower():
                    category = c
                    break

        if category:
            pros = ProfessionalProfile.query.filter_by(
                category_id=category.id, availability_status='available'
            ).order_by(ProfessionalProfile.rating.desc()).limit(3).all()

            if pros:
                pro_list = [{
                    'id': p.id,
                    'name': f"{p.user.first_name} {p.user.last_name}",
                    'specialty': p.specialty,
                    'rating': p.rating,
                    'price': p.consultation_price,
                    'status': p.availability_status,
                    'offers_video': p.offers_video,
                } for p in pros]

                return jsonify({
                    'response': f"I found {len(pro_list)} {matched_category} professionals available to help you.",
                    'suggestion': matched_category,
                    'professionals': pro_list,
                }), 200

    return jsonify({
        'response': "I can help you find the right professional. Try describing what you need, for example: 'I have a toothache', 'I need legal advice', or 'I want to learn math'.",
        'suggestion': None,
        'professionals': [],
    }), 200


# ===== PORTFOLIO =====
@app.route('/api/portfolio/<int:pro_id>', methods=['GET'])
def get_portfolio(pro_id):
    from models import PortfolioItem
    items = PortfolioItem.query.filter_by(professional_id=pro_id).order_by(PortfolioItem.created_at.desc()).all()
    return jsonify([i.to_dict() for i in items]), 200


# ===== LOYALTY =====
@app.route('/api/loyalty', methods=['GET'])
@jwt_required()
def get_loyalty():
    user_id = int(get_jwt_identity())
    loyalty = LoyaltyPoint.query.filter_by(user_id=user_id).first()
    if not loyalty:
        loyalty = LoyaltyPoint(user_id=user_id)
        db.session.add(loyalty)
        db.session.commit()
    return jsonify(loyalty.to_dict()), 200


# ===== FAMILY ACCOUNTS =====
@app.route('/api/family', methods=['GET'])
@jwt_required()
def get_family_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter(
        Booking.client_id == user_id,
        Booking.family_member_name.isnot(None),
        Booking.family_member_name != ''
    ).order_by(Booking.date.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


# ===== SEARCH (AI-powered) =====
@app.route('/api/search', methods=['GET'])
def search():
    q = request.args.get('q', '').lower()
    category = request.args.get('category')
    province_id = request.args.get('province_id')

    results = {'professionals': [], 'categories': []}

    # Search categories
    cats = Category.query.filter(Category.name.ilike(f'%{q}%')).all()
    results['categories'] = [{'id': c.id, 'name': c.name, 'icon': c.icon} for c in cats]

    # Search professionals
    query = ProfessionalProfile.query.join(User)
    if q:
        query = query.filter(db.or_(
            User.first_name.ilike(f'%{q}%'),
            User.last_name.ilike(f'%{q}%'),
            ProfessionalProfile.specialty.ilike(f'%{q}%'),
            ProfessionalProfile.bio.ilike(f'%{q}%'),
            ProfessionalProfile.business_name.ilike(f'%{q}%'),
        ))
    if category:
        query = query.filter(ProfessionalProfile.category_id == int(category))
    if province_id:
        query = query.join(User).filter(User.province_id == int(province_id))

    pros = query.limit(20).all()
    results['professionals'] = [p.to_dict() for p in pros]

    return jsonify(results), 200


# ===== DATABASE SEEDING =====
def seed_database():
    """Seed the database with initial data."""
    if Province.query.first():
        return  # Already seeded

    # South African Provinces
    provinces_data = [
        ('Eastern Cape', 'EC', -32.2969, 26.4803),
        ('Free State', 'FS', -28.4453, 26.2338),
        ('Gauteng', 'GP', -26.2708, 28.1124),
        ('KwaZulu-Natal', 'KZN', -30.5595, 29.0816),
        ('Limpopo', 'LP', -23.8964, 29.4486),
        ('Mpumalanga', 'MP', -25.5708, 30.5286),
        ('North West', 'NW', -26.2283, 25.6213),
        ('Northern Cape', 'NC', -29.0466, 22.1319),
        ('Western Cape', 'WC', -33.2194, 19.0894),
    ]
    municipalities_data = {
        'Gauteng': [
            ('City of Johannesburg', -26.2041, 28.0473),
            ('City of Tshwane', -25.7479, 28.2293),
            ('Ekurhuleni', -26.1367, 28.3614),
            ('Sedibeng', -26.5486, 28.1636),
            ('West Rand', -26.2288, 27.7493),
        ],
        'KwaZulu-Natal': [
            ('eThekwini', -29.8587, 31.0218),
            ('uMgungundlovu', -29.5, 30.25),
            ('uMkhanyakude', -27.5, 32.5),
            ('iLembe', -29.25, 31.5),
            ('King Cetshwayo', -28.75, 31.9),
        ],
        'Western Cape': [
            ('City of Cape Town', -33.9249, 18.4241),
            ('Cape Winelands', -33.5, 19.0),
            ('Overberg', -34.2, 19.5),
            ('Eden', -33.8, 21.5),
        ],
        'Free State': [
            ('Mangaung', -29.1, 26.2),
            ('Lejweleputswa', -28.5, 26.0),
            ('Thabo Mofutsanyane', -28.8, 27.5),
        ],
        'Eastern Cape': [
            ('Nelson Mandela Bay', -33.9608, 25.6022),
            ('Buffalo City', -32.9, 27.6),
            ('Sarah Baartman', -33.0, 25.5),
        ],
        'Limpopo': [
            ('Capricorn', -23.9, 29.4),
            ('Mopani', -23.7, 30.5),
            ('Vhembe', -22.9, 30.0),
        ],
        'Mpumalanga': [
            ('Nkangala', -25.8, 29.5),
            ('Gert Sibande', -26.5, 30.0),
            ('Ehlanzeni', -25.5, 31.0),
        ],
        'North West': [
            ('Bojanala', -25.3, 27.0),
            ('Ngaka Modiri Molema', -25.8, 25.5),
            ('Dr Ruth Segomotsi Mompati', -25.8, 24.5),
        ],
        'Northern Cape': [
            ('Frances Baar', -28.5, 23.0),
            ('John Taolo Gaetsewe', -27.0, 23.0),
            ('Namakwa', -30.5, 18.5),
        ],
    }

    for name, code, lat, lng in provinces_data:
        prov = Province(name=name, code=code)
        db.session.add(prov)
        db.session.flush()
        if name in municipalities_data:
            for mname, mlat, mlng in municipalities_data[name]:
                mun = Municipality(name=mname, province_id=prov.id, latitude=mlat, longitude=mlng)
                db.session.add(mun)

    # Categories
    categories_data = [
        ('Healthcare', 'Healthcare', 'Ukusingaphila', 'Bophelo', 'Phelophepo', 'Ukusingaphila', 'Gesondheid', '🩺',
         'Doctors, dentists, psychologists, pharmacists, therapists, nurses'),
        ('Legal Services', 'Legal Services', 'Inkonzo Zomthetho', 'Ditirelo tsa Molao', 'Iinkonzo Zomthetho', 'Regsadvies', '⚖️',
         'Lawyers, notaries, labour consultants, debt advisors'),
        ('Education', 'Education', 'Imfundo', 'Fundo', 'Imfundo', 'Onderwys', '📚',
         'Tutors, career coaches, university advisors, coding mentors'),
        ('Business Services', 'Business Services', 'Inkonzo Zokubhanisa', 'Ditirelo tsa Kopo', 'Iinkonzo Zoshishino', 'Besigheidsdienste', '💼',
         'Accountants, tax consultants, business consultants, financial advisors'),
        ('Home Services', 'Home Services', 'Inkonzo Zasekhaya', 'Ditirelo tsa Gae', 'Iinkonzo Zasekhaya', 'Tuisteenste', '🏠',
         'Electricians, plumbers, mechanics, handymen, security installers'),
        ('Technology', 'Technology', 'Ubuchwepheshe', 'Teknoloji', 'Ubuchwepheshe', 'Tegnologie', '💻',
         'Software developers, IT support, cybersecurity, graphic designers'),
        ('Fitness & Wellness', 'Fitness & Wellness', 'Ukuzivocavoca', 'Phefatsa', 'Ukuzivocavoca', 'Fiknes', '💪',
         'Personal trainers, dietitians, physiotherapists'),
        ('Financial Advisory', 'Financial Advisory', 'Ukululeka Kwezimali', 'Keletso ya Madi', 'Ingcebiso Yezimali', 'Finansieel', '📈',
         'Investment advisors, retirement planners, estate planners'),
    ]

    for item in categories_data:
        cat = Category(
            name=item[0], name_en=item[1], name_zu=item[2], name_st=item[3],
            name_xh=item[4], name_tn=item[5], name_af=item[6], icon=item[7], description=item[8] if len(item)>8 else ''
        )
        db.session.add(cat)

    db.session.flush()

    # Demo professionals
    demo_pros = [
        {'first': 'Amina', 'last': 'Osei', 'email': 'amina.osei@example.com', 'cat': 'Healthcare', 'specialty': 'General Practitioner',
         'bio': 'Experienced GP with 12 years of clinical practice. Specializing in family medicine, preventive care, and chronic disease management.',
         'price': 350, 'online': 300, 'house': 500, 'lat': -26.2041, 'lng': 28.0473, 'addr': 'Sandton, Johannesburg',
         'verified': True, 'rating': 4.9, 'reviews': 127, 'patients': 500, 'bookings': 850,
         'services': [('General Consultation', 'In-person consultation', 350, 30), ('Follow-up Visit', 'Returning patient', 200, 20),
                      ('Health Certificate', 'Medical fitness cert', 500, 30), ('Video Consultation', 'Online video call', 300, 30)],
         'status': 'available', 'business': 'Osei Medical Practice'},

        {'first': 'Bongani', 'last': 'Ndlovu', 'email': 'bongani.ndlovu@example.com', 'cat': 'Legal Services', 'specialty': 'Corporate Lawyer',
         'bio': 'Corporate and commercial law specialist with 15 years experience. Advising on mergers, acquisitions, and regulatory compliance.',
         'price': 500, 'online': 450, 'house': 700, 'lat': -33.9249, 'lng': 18.4241, 'addr': 'Cape Town CBD',
         'verified': True, 'rating': 4.8, 'reviews': 89, 'patients': 300, 'bookings': 600,
         'services': [('Legal Consultation', '1-hour consultation', 500, 60), ('Contract Review', 'Review contracts', 800, 60),
                      ('Company Registration', 'CIPC registration', 1200, 120)],
         'status': 'available', 'business': 'Ndlovu & Associates'},

        {'first': 'Sarah', 'last': 'Mensah', 'email': 'sarah.mensah@example.com', 'cat': 'Education', 'specialty': 'Mathematics Tutor',
         'bio': 'Passionate math educator with 8 years experience. Making complex concepts accessible and enjoyable.',
         'price': 250, 'online': 200, 'house': 350, 'lat': -26.2708, 'lng': 28.1124, 'addr': 'Pretoria East',
         'verified': True, 'rating': 4.9, 'reviews': 203, 'patients': 150, 'bookings': 1200,
         'services': [('1-on-1 Tutoring', '60-minute session', 250, 60), ('Group Session', 'Up to 4 students', 150, 60),
                      ('Exam Prep', 'Intensive 2-hour', 400, 120)],
         'status': 'available', 'business': 'Mensah Math Academy'},

        {'first': 'Thabo', 'last': 'Moyo', 'email': 'thabo.moyo@example.com', 'cat': 'Healthcare', 'specialty': 'Dentist',
         'bio': 'Comprehensive dental care including preventive, restorative, and cosmetic dentistry. HPCSA registered.',
         'price': 400, 'online': 350, 'house': 600, 'lat': -25.7479, 'lng': 28.2293, 'addr': 'Centurion, Pretoria',
         'verified': True, 'rating': 4.7, 'reviews': 95, 'patients': 400, 'bookings': 700,
         'services': [('Dental Check-up', 'Exam + X-rays', 400, 30), ('Teeth Cleaning', 'Professional cleaning', 600, 45),
                      ('Filling', 'Composite filling', 800, 45)],
         'status': 'busy', 'business': 'Smile Dental Clinic'},

        {'first': 'Peter', 'last': 'Adeyemi', 'email': 'peter.adeyemi@example.com', 'cat': 'Business Services', 'specialty': 'Tax Consultant',
         'bio': 'Seasoned tax consultant with 18 years experience. Helping businesses optimize their tax positions.',
         'price': 450, 'online': 400, 'house': 650, 'lat': -29.8587, 'lng': 31.0218, 'addr': 'Durban CBD',
         'verified': True, 'rating': 4.8, 'reviews': 156, 'patients': 600, 'bookings': 1100,
         'services': [('Tax Consultation', '1-hour consultation', 450, 60), ('Tax Return', 'Individual IT return', 800, 120),
                      ('Business Tax', 'Company tax filing', 2500, 180)],
         'status': 'available', 'business': 'Adeyemi Tax Advisory'},

        {'first': 'Ngozi', 'last': 'Okonkwo', 'email': 'ngozi.okonkwo@example.com', 'cat': 'Healthcare', 'specialty': 'Psychologist',
         'bio': 'Clinical psychologist specializing in CBT. Helping individuals overcome anxiety, depression, and trauma.',
         'price': 500, 'online': 450, 'house': 700, 'lat': -26.2041, 'lng': 28.0473, 'addr': 'Rosebank, Johannesburg',
         'verified': True, 'rating': 4.9, 'reviews': 112, 'patients': 350, 'bookings': 900,
         'services': [('Therapy Session', '50-minute session', 500, 50), ('Couple Therapy', 'Joint session', 700, 80),
                      ('Online Therapy', 'Video call session', 450, 50)],
         'status': 'available', 'business': 'MindWell Psychology'},

        {'first': 'Lerato', 'last': 'Dlamini', 'email': 'lerato.dlamini@example.com', 'cat': 'Fitness & Wellness', 'specialty': 'Personal Trainer',
         'bio': 'Certified personal trainer and nutritionist. Specializing in strength training and holistic wellness.',
         'price': 300, 'online': 250, 'house': 400, 'lat': -29.8587, 'lng': 31.0218, 'addr': 'Umhlanga, Durban',
         'verified': True, 'rating': 4.9, 'reviews': 178, 'patients': 200, 'bookings': 1500,
         'services': [('Personal Training', '1-hour session', 300, 60), ('Online Coaching', 'Monthly program', 1500, 30),
                      ('Meal Planning', 'Custom nutrition plan', 800, 30)],
         'status': 'available', 'business': 'FitLife Durban'},

        {'first': 'Tendai', 'last': 'Murapa', 'email': 'tendai.murapa@example.com', 'cat': 'Technology', 'specialty': 'Software Developer',
         'bio': 'Full-stack developer with expertise in web apps, mobile apps, and UI/UX design. Building Africa\'s digital future.',
         'price': 600, 'online': 600, 'house': 800, 'lat': -26.2041, 'lng': 28.0473, 'addr': 'Midrand, Johannesburg',
         'verified': True, 'rating': 4.7, 'reviews': 64, 'patients': 80, 'bookings': 200,
         'services': [('Web Development', 'Custom website', 5000, 240), ('Consultation', '1-hour tech consult', 600, 60),
                      ('UI/UX Design', 'App/web design', 3500, 120)],
         'status': 'available', 'business': 'TechAfrik Solutions'},

        {'first': 'Fatima', 'last': 'Benali', 'email': 'fatima.benali@example.com', 'cat': 'Healthcare', 'specialty': 'Pharmacist',
         'bio': 'Licensed pharmacist providing medication counseling and drug interaction reviews.',
         'price': 200, 'online': 180, 'house': 300, 'lat': -26.2041, 'lng': 28.0473, 'addr': 'Sandton, Johannesburg',
         'verified': True, 'rating': 4.7, 'reviews': 68, 'patients': 300, 'bookings': 500,
         'services': [('Medication Review', 'Full medication assessment', 200, 30), ('Online Consult', 'Video pharmacist consult', 180, 30)],
         'status': 'available', 'business': 'CarePharm Pharmacy'},

        {'first': 'Kwame', 'last': 'Asante', 'email': 'kwame.asante@example.com', 'cat': 'Financial Advisory', 'specialty': 'Financial Advisor',
         'bio': 'Certified financial advisor helping individuals build wealth through smart investment planning.',
         'price': 550, 'online': 500, 'house': 750, 'lat': -33.9249, 'lng': 18.4241, 'addr': 'Stellenbosch',
         'verified': True, 'rating': 4.8, 'reviews': 91, 'patients': 180, 'bookings': 400,
         'services': [('Financial Planning', 'Comprehensive plan', 1500, 120), ('Investment Review', 'Portfolio assessment', 550, 60),
                      ('Quick Consult', '30-minute session', 300, 30)],
         'status': 'available', 'business': 'Asante Wealth Management'},

        {'first': 'Thabo', 'last': 'Molefe', 'email': 'thabo.molefe@example.com', 'cat': 'Home Services', 'specialty': 'Electrician',
         'bio': 'Qualified and licensed electrician with 11 years experience. Specializing in residential and solar installations.',
         'price': 350, 'online': 200, 'house': 350, 'lat': -29.1, 'lng': 26.2, 'addr': 'Bloemfontein',
         'verified': False, 'rating': 4.6, 'reviews': 73, 'patients': 250, 'bookings': 600,
         'services': [('Electrical Inspection', 'Full property inspection', 350, 60), ('Fault Finding', 'Diagnostic service', 450, 60),
                      ('Solar Setup', 'Solar panel installation', 5000, 480)],
         'status': 'available', 'business': 'Molefe Electrical'},

        {'first': 'Amara', 'last': 'Diallo', 'email': 'amara.diallo@example.com', 'cat': 'Education', 'specialty': 'Career Coach',
         'bio': 'Certified career coach helping professionals navigate their career paths.',
         'price': 400, 'online': 350, 'house': 500, 'lat': -33.9249, 'lng': 18.4241, 'addr': 'Cape Town',
         'verified': True, 'rating': 4.8, 'reviews': 88, 'patients': 120, 'bookings': 350,
         'services': [('Career Consultation', '60-minute session', 400, 60), ('CV Review', 'Professional review', 300, 30),
                      ('Interview Prep', 'Mock interview', 500, 60)],
         'status': 'available', 'business': 'Diallo Career Solutions'},
    ]

    # Get Gauteng province for default location
    gp = Province.query.filter_by(code='GP').first()
    gp_id = gp.id if gp else 1
    wc = Province.query.filter_by(code='WC').first()
    wc_id = wc.id if wc else 1
    kzn = Province.query.filter_by(code='KZN').first()
    kzn_id = kzn.id if kzn else 1
    fs = Province.query.filter_by(code='FS').first()
    fs_id = fs.id if fs else 1

    province_map = {
        -26.2041: gp_id, -25.7479: gp_id, -26.2708: gp_id,
        -33.9249: wc_id, -29.8587: kzn_id, -29.1: fs_id,
    }

    for pro_data in demo_pros:
        # Create user
        user = User(
            email=pro_data['email'],
            first_name=pro_data['first'],
            last_name=pro_data['last'],
            phone=f"+27{random.randint(60,84)}{random.randint(1000000,9999999)}",
            role='professional',
            province_id=province_map.get(pro_data['lat'], gp_id),
            latitude=pro_data['lat'],
            longitude=pro_data['lng'],
            is_verified=True,
        )
        user.set_password('demo123')
        db.session.add(user)
        db.session.flush()

        cat = Category.query.filter_by(name=pro_data['cat']).first()
        profile = ProfessionalProfile(
            user_id=user.id,
            category_id=cat.id,
            specialty=pro_data['specialty'],
            bio=pro_data['bio'],
            consultation_price=pro_data['price'],
            online_consultation_price=pro_data['online'],
            house_call_price=pro_data['house'],
            availability_status=pro_data['status'],
            is_verified=pro_data['verified'],
            rating=pro_data['rating'],
            review_count=pro_data['reviews'],
            total_patients=pro_data['patients'],
            total_bookings=pro_data['bookings'],
            latitude=pro_data['lat'],
            longitude=pro_data['lng'],
            address=pro_data['addr'],
            business_name=pro_data['business'],
            offers_video=True,
            offers_voice=True,
            offers_chat=True,
            offers_house_call=True,
            subscription_plan='professional',
        )
        db.session.add(profile)
        db.session.flush()

        for sname, sdesc, sprice, sdur in pro_data['services']:
            service = Service(
                professional_id=profile.id,
                name=sname,
                description=sdesc,
                price=sprice,
                duration_minutes=sdur,
            )
            db.session.add(service)

    # Emergency contacts
    emergency_data = [
        ('Netcare 911', 'ambulance', '082 911', True),
        ('ER24 Emergency', 'ambulance', '084 124', True),
        ('South African Police', 'police', '10111', True),
        ('Fire & Rescue', 'fire', '10177', True),
        ('Gender-Based Violence', 'security', '0800 428 428', True),
        ('Suicide Helpline', 'doctor', '0800 567 567', True),
    ]

    for name, cat, phone, is24 in emergency_data:
        for prov in Province.query.all():
            ec = EmergencyContact(
                name=name, category=cat, phone=phone,
                province_id=prov.id, is_24hr=is24,
                latitude=prov.id * 2 + random.uniform(-5, 5),
                longitude=prov.id * 3 + random.uniform(-5, 5),
            )
            db.session.add(ec)

    db.session.commit()
    print("✅ Database seeded successfully!")


# ===== APP STARTUP =====
with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
