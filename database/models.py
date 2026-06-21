from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='client')
    province = db.Column(db.String(80))
    municipality = db.Column(db.String(80))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    language = db.Column(db.String(10), default='en')
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

    def serialize(self):
        return {'id': self.id, 'email': self.email, 'first_name': self.first_name,
                'last_name': self.last_name, 'phone': self.phone, 'role': self.role,
                'province': self.province, 'municipality': self.municipality,
                'language': self.language, 'verified': self.verified,
                'created_at': self.created_at.isoformat() if self.created_at else None}


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    icon = db.Column(db.String(10))
    description = db.Column(db.String(300))

    def serialize(self):
        return {'id': self.id, 'name': self.name, 'icon': self.icon,
                'description': self.description, 'count': Professional.query.filter_by(category_id=self.id).count()}


class Professional(db.Model):
    __tablename__ = 'professionals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    specialty = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text)
    experience = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    online_price = db.Column(db.Float)
    house_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='available')
    verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)
    patients_count = db.Column(db.Integer, default=0)
    bookings_count = db.Column(db.Integer, default=0)
    has_video = db.Column(db.Boolean, default=True)
    has_voice = db.Column(db.Boolean, default=True)
    has_chat = db.Column(db.Boolean, default=True)
    has_house = db.Column(db.Boolean, default=False)
    has_group = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(300))
    business = db.Column(db.String(200))
    plan = db.Column(db.String(20), default='free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', uselist=False, backref='professional')
    services = db.relationship('Service', backref='pro', lazy=True, cascade='all,delete-orphan')
    portfolio = db.relationship('Portfolio', backref='pro', lazy=True, cascade='all,delete-orphan')

    def category_name(self):
        return db.session.get(Category, self.category_id).name if db.session.get(Category, self.category_id) else ''

    def serialize(self):
        cat_name = self.category_name()
        return {'id': self.id, 'user_id': self.user_id,
                'name': f"{self.user.first_name} {self.user.last_name}",
                'initials': self.user.first_name[0] + self.user.last_name[0],
                'category': cat_name, 'category_id': self.category_id,
                'specialty': self.specialty, 'bio': self.bio,
                'experience': self.experience, 'price': self.price,
                'online_price': self.online_price, 'house_price': self.house_price,
                'status': self.status, 'verified': self.verified,
                'rating': round(self.rating, 1), 'reviews_count': self.reviews_count,
                'patients_count': self.patients_count, 'bookings_count': self.bookings_count,
                'has_video': self.has_video, 'has_voice': self.has_voice,
                'has_chat': self.has_chat, 'has_house': self.has_house,
                'has_group': self.has_group, 'latitude': self.latitude,
                'longitude': self.longitude, 'address': self.address,
                'business': self.business, 'plan': self.plan,
                'services': [s.serialize() for s in self.services],
                'portfolio': [p.serialize() for p in self.portfolio]}


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    pro_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, default=30)

    def serialize(self):
        return {'id': self.id, 'name': self.name, 'description': self.description,
                'price': self.price, 'duration': self.duration}


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pro_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    type = db.Column(db.String(20), nullable=False)
    consult = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(5), nullable=False)
    duration = db.Column(db.Integer, default=30)
    price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    family = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('User', backref='bookings')
    service = db.relationship('Service', backref='bookings')

    def pro_name(self):
        p = db.session.get(Professional, self.pro_id)
        if p and p.user: return p.user.first_name + ' ' + p.user.last_name
        return ''

    def serialize(self):
        return {'id': self.id, 'client_id': self.client_id, 'pro_id': self.pro_id,
                'pro_name': self.pro_name(), 'service_name': self.service.name if self.service else None,
                'type': self.type, 'consult': self.consult, 'status': self.status,
                'date': self.date.isoformat() if self.date else None, 'time': self.time,
                'duration': self.duration, 'price': self.price, 'notes': self.notes,
                'family': self.family,
                'created_at': self.created_at.isoformat() if self.created_at else None}


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), unique=True, nullable=False)
    pro_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {'id': self.id, 'rating': self.rating, 'comment': self.comment,
                'created_at': self.created_at.isoformat() if self.created_at else None}


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {'id': self.id, 'sender_id': self.sender_id, 'receiver_id': self.receiver_id,
                'content': self.content, 'read': self.read,
                'created_at': self.created_at.isoformat() if self.created_at else None}


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50))
    url = db.Column(db.String(500))
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {'id': self.id, 'name': self.name, 'type': self.type,
                'url': self.url, 'size': self.size,
                'created_at': self.created_at.isoformat() if self.created_at else None}


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(30), unique=True, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pro_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {'id': self.id, 'number': self.number, 'subtotal': self.subtotal,
                'fee': self.fee, 'total': self.total, 'status': self.status,
                'created_at': self.created_at.isoformat() if self.created_at else None}


class Emergency(db.Model):
    __tablename__ = 'emergency'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    phone = db.Column(db.String(20), nullable=False)
    available_24h = db.Column(db.Boolean, default=True)

    def serialize(self):
        return {'id': self.id, 'name': self.name, 'category': self.category,
                'phone': self.phone, 'available_24h': self.available_24h}


class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True)
    pro_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20))
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {'id': self.id, 'title': self.title, 'description': self.description,
                'type': self.type, 'url': self.url,
                'created_at': self.created_at.isoformat() if self.created_at else None}


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {'id': self.id, 'title': self.title, 'message': self.message,
                'type': self.type, 'read': self.read,
                'created_at': self.created_at.isoformat() if self.created_at else None}