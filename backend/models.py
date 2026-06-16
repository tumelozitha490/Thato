"""
ExpertConnect Africa - Database Models
SQLAlchemy models for the complete platform.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Province(db.Model):
    __tablename__ = 'provinces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    municipalities = db.relationship('Municipality', backref='province', lazy=True)


class Municipality(db.Model):
    __tablename__ = 'municipalities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='client')  # client, professional, admin
    avatar_url = db.Column(db.String(500))
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'))
    municipality_id = db.Column(db.Integer, db.ForeignKey('municipalities.id'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    preferred_language = db.Column(db.String(10), default='en')
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    id_document_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    province = db.relationship('Province', backref='users')
    municipality = db.relationship('Municipality', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role,
            'avatar_url': self.avatar_url,
            'province_id': self.province_id,
            'municipality_id': self.municipality_id,
            'province': self.province.name if self.province else None,
            'municipality': self.municipality.name if self.municipality else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'preferred_language': self.preferred_language,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    name_en = db.Column(db.String(100))
    name_zu = db.Column(db.String(100))
    name_st = db.Column(db.String(100))
    name_tn = db.Column(db.String(100))
    name_xh = db.Column(db.String(100))
    name_af = db.Column(db.String(100))
    icon = db.Column(db.String(10))
    description = db.Column(db.String(500))
    professionals = db.relationship('ProfessionalProfile', backref='category', lazy=True)


class ProfessionalProfile(db.Model):
    __tablename__ = 'professional_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    specialty = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text)
    tagline = db.Column(db.String(300))
    experience_years = db.Column(db.Integer)
    consultation_price = db.Column(db.Float, nullable=False)
    online_consultation_price = db.Column(db.Float)
    house_call_price = db.Column(db.Float)
    group_consultation_price = db.Column(db.Float)
    availability_status = db.Column(db.String(20), default='available')  # available, busy, offline, on_leave
    is_verified = db.Column(db.Boolean, default=False)
    verification_document_url = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    total_patients = db.Column(db.Integer, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    offers_video = db.Column(db.Boolean, default=True)
    offers_voice = db.Column(db.Boolean, default=True)
    offers_chat = db.Column(db.Boolean, default=True)
    offers_house_call = db.Column(db.Boolean, default=False)
    offers_group = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(300))
    business_name = db.Column(db.String(200))
    website = db.Column(db.String(300))
    subscription_plan = db.Column(db.String(20), default='starter')  # starter, professional, enterprise
    subscription_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='professional_profile')
    services = db.relationship('Service', backref='professional', lazy=True, cascade='all, delete-orphan')
    availability_slots = db.relationship('AvailabilitySlot', backref='professional', lazy=True, cascade='all, delete-orphan')
    portfolio_items = db.relationship('PortfolioItem', backref='professional', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': f"{self.user.first_name} {self.user.last_name}" if self.user else None,
            'user_avatar': self.user.avatar_url if self.user else None,
            'category': self.category.name if self.category else None,
            'category_id': self.category_id,
            'specialty': self.specialty,
            'bio': self.bio,
            'tagline': self.tagline,
            'experience_years': self.experience_years,
            'consultation_price': self.consultation_price,
            'online_consultation_price': self.online_consultation_price,
            'house_call_price': self.house_call_price,
            'group_consultation_price': self.group_consultation_price,
            'availability_status': self.availability_status,
            'is_verified': self.is_verified,
            'rating': self.rating,
            'review_count': self.review_count,
            'total_patients': self.total_patients,
            'total_bookings': self.total_bookings,
            'offers_video': self.offers_video,
            'offers_voice': self.offers_voice,
            'offers_chat': self.offers_chat,
            'offers_house_call': self.offers_house_call,
            'offers_group': self.offers_group,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'business_name': self.business_name,
            'website': self.website,
            'subscription_plan': self.subscription_plan,
            'services': [s.to_dict() for s in self.services],
            'portfolio': [p.to_dict() for p in self.portfolio_items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_profiles.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration_minutes': self.duration_minutes,
            'is_active': self.is_active,
        }


class AvailabilitySlot(db.Model):
    __tablename__ = 'availability_slots'
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_profiles.id'), nullable=False)
    day_of_week = db.Column(db.Integer)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.String(5))  # "09:00"
    end_time = db.Column(db.String(5))  # "17:00"
    is_recurring = db.Column(db.Boolean, default=True)
    specific_date = db.Column(db.Date)  # For non-recurring slots
    is_available = db.Column(db.Boolean, default=True)


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_profiles.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    booking_type = db.Column(db.String(20), nullable=False)  # online, in_person, house_call, group
    consultation_type = db.Column(db.String(20))  # video, voice, chat
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(5), nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    total_price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    cancellation_reason = db.Column(db.String(300))
    family_member_name = db.Column(db.String(200))  # For family bookings
    reminder_sent = db.Column(db.Boolean, default=False)
    invoice_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = db.relationship('User', backref='bookings')
    professional = db.relationship('ProfessionalProfile', backref='bookings')
    service = db.relationship('Service', backref='bookings')
    review = db.relationship('Review', backref='booking', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_name': f"{self.client.first_name} {self.client.last_name}" if self.client else None,
            'professional_id': self.professional_id,
            'professional_name': self.professional.user.first_name + ' ' + self.professional.user.last_name if self.professional and self.professional.user else None,
            'specialty': self.professional.specialty if self.professional else None,
            'service_name': self.service.name if self.service else None,
            'booking_type': self.booking_type,
            'consultation_type': self.consultation_type,
            'status': self.status,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time,
            'duration_minutes': self.duration_minutes,
            'total_price': self.total_price,
            'notes': self.notes,
            'family_member_name': self.family_member_name,
            'invoice_generated': self.invoice_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_profiles.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('User', backref='reviews_given')
    professional = db.relationship('ProfessionalProfile', backref='reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'client_name': f"{self.client.first_name} {self.client.last_name[0]}." if self.client else None,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='messages_sent')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='messages_received')

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    name = db.Column(db.String(200), nullable=False)
    doc_type = db.Column(db.String(50))  # id, medical_record, certificate, contract, other
    file_url = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='documents')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'doc_type': self.doc_type,
            'file_url': self.file_url,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
        }


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_profiles.id'), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    platform_fee = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    booking = db.relationship('Booking', backref='invoice')
    client = db.relationship('User', backref='invoices')
    professional = db.relationship('ProfessionalProfile', backref='invoices')

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'subtotal': self.subtotal,
            'platform_fee': self.platform_fee,
            'total': self.total,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # doctor, ambulance, security, fire, police
    phone = db.Column(db.String(20), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(300))
    is_24hr = db.Column(db.Boolean, default=True)

    province = db.relationship('Province', backref='emergency_contacts')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'phone': self.phone,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'is_24hr': self.is_24hr,
        }


class LoyaltyPoint(db.Model):
    __tablename__ = 'loyalty_points'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    total_earned = db.Column(db.Integer, default=0)
    total_redeemed = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref='loyalty')

    def to_dict(self):
        return {
            'id': self.id,
            'points': self.points,
            'total_earned': self.total_earned,
            'total_redeemed': self.total_redeemed,
        }


class PortfolioItem(db.Model):
    __tablename__ = 'portfolio_items'
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    media_type = db.Column(db.String(20))  # image, video, document
    media_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'media_type': self.media_type,
            'media_url': self.media_url,
            'thumbnail_url': self.thumbnail_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notif_type = db.Column(db.String(50))  # booking, reminder, system, promotion
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notif_type': self.notif_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }