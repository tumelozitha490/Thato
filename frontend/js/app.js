/**
 * ExpertConnect Africa - Frontend Application
 * Production-ready super app with all features.
 */

const API = 'http://localhost:5001/api';
const translations = {
  en: { nav_home:'Home',nav_browse:'Browse Pros',nav_ai:'🤖 AI Assistant',nav_emergency:'🚨 Emergency',nav_login:'Log In',nav_signup:'Sign Up',hero_title:'Book <span class="highlight">Trusted Experts</span> Across Africa',hero_subtitle:'One super app to find, talk to, hire, and pay trusted professionals. Online consultations, video calls, voice calls, or in-person visits.',cat_title:'Find the Right Professional',cat_subtitle:'Browse across 8 major categories with thousands of verified experts.',how_title:'How It Works' },
  zu: { nav_home:'Ikhasi',nav_browse:'Buka Ogcweti',nav_ai:'🤖 Usizo lwe-AI',nav_emergency:'🚨 Esheshayo',nav_login:'Ngena',nav_signup:'Bhalisa',hero_title:'Bhuka <span class="highlight">Ochwepheshe abathembekile</span> eNingizimu Afrika',hero_subtitle:'Uhlelo olukodwa ukuthola, ukhulume, uqashe, futhi ukhokhe ochwepheshe abathembekile.',cat_title:'Thola iNchwepheshe efanele',cat_subtitle:'Buka kumakhathiguru angu-8 anobuningi bochwepheshe abaqinisekisiwe.',how_title:'Kusebenza kanjani' },
  st: { nav_home:'Leqephe',nav_browse:'Bala Batjhebehi',nav_ai:'🤖 Thuso ya AI',nav_emergency:'🚨 T急iso',nav_login:'Kena',nav_signup:'Ngwala',hero_title:'Buka <span class="highlight">Batjhebehi ba Botlhabelo</span> Afrika Borwa',cat_title:'Fumana Batjhebehi ba Lokwena',how_title:'E sebetsa jwang' },
  tn: { nav_home:'Tsebe',nav_browse:'Batla Badireksi',nav_ai:'🤖 Thulaganyo ya AI',nav_emergency:'🚨 T急iso',nav_login:'Tsenya',nav_signup:'Ngwala',hero_title:'Buka <span class="highlight">Badireksi ba Tsholofelo</span> Afrika',cat_title:'Fumana Badireksi ba Lokwena',how_title:'E direga jang' },
  xh: { nav_home:'Ikhasi',nav_browse:'Jonga Abaphambili',nav_ai:'🤖 Uncedo lwe-AI',nav_emergency:'🚨 Ngxamiseko',nav_login:'Ngena',nav_signup:'Bhalisa',hero_title:'Bhuka <span class="highlight">Oososayinisi abathembekileyo</span> eMzantsi Afrika',cat_title:'Fumana iNkosana efanelekileyo',how_title:'Iyasebenza njani' },
  af: { nav_home:'Tuis',nav_browse:'Soek Professionals',nav_ai:'🤖 AI Assistent',nav_emergency:'🚨 Noodgeval',nav_login:'Teken In',nav_signup:'Registreer',hero_title:'Boek <span class="highlight">Vertroude Kenners</span> regoor Afrika',cat_title:'Vind die Regte Professionele',how_title:'Hoe Dit Werk' },
};

const App = {
  user: null,
  token: localStorage.getItem('eca_token'),
  categories: [],
  professionals: [],
  provinces: [],
  selectedPro: null,
  currentLang: localStorage.getItem('eca_lang') || 'en',

  // ===== INIT =====
  async init() {
    this.setupScrollNav();
    await this.loadCategories();
    await this.loadProvinces();
    await this.loadProfessionals();
    this.renderFeatured();
    this.renderEmergency();
    this.populateSignupSelects();
    this.setDefaultDate();
    this.setLanguage(this.currentLang);
    if (this.token) await this.loadUser();
  },

  // ===== API HELPERS =====
  async api(endpoint, opts = {}) {
    const headers = { 'Content-Type': 'application/json', ...opts.headers };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
    try {
      const res = await fetch(`${API}${endpoint}`, { ...opts, headers });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Request failed');
      return data;
    } catch (e) {
      console.error('API Error:', e);
      throw e;
    }
  },

  // ===== AUTH =====
  async loadUser() {
    try {
      this.user = await this.api('/auth/me');
      this.updateAuthUI();
    } catch { this.token = null; localStorage.removeItem('eca_token'); }
  },

  async login() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPass').value;
    if (!email || !password) return this.toast('Please fill in all fields','⚠️');
    try {
      const data = await this.api('/auth/login', { method:'POST', body:JSON.stringify({email,password}) });
      this.token = data.token; this.user = data.user;
      localStorage.setItem('eca_token', this.token);
      this.closeModal('loginModal');
      this.updateAuthUI();
      this.toast(`Welcome back, ${data.user.first_name}! 🎉`);
    } catch(e) { this.toast(e.message,'❌'); }
  },

  async signup() {
    const body = {
      email: document.getElementById('signupEmail').value,
      password: document.getElementById('signupPass').value,
      first_name: document.getElementById('signupFirst').value,
      last_name: document.getElementById('signupLast').value,
      phone: document.getElementById('signupPhone').value,
      role: document.getElementById('signupRole').value,
      province_id: document.getElementById('signupProvince').value || null,
      municipality_id: document.getElementById('signupMunicipality').value || null,
    };
    if (!body.email || !body.password || !body.first_name || !body.last_name) return this.toast('Please fill in all fields','⚠️');
    if (body.role === 'professional') {
      body.category_id = document.getElementById('signupCategory').value || null;
      body.specialty = document.getElementById('signupSpecialty').value;
      body.business_name = document.getElementById('signupBusiness').value;
      body.consultation_price = parseFloat(document.getElementById('signupPrice').value) || 0;
    }
    try {
      const data = await this.api('/auth/register', { method:'POST', body:JSON.stringify(body) });
      this.token = data.token; this.user = data.user;
      localStorage.setItem('eca_token', this.token);
      this.closeModal('signupModal');
      this.updateAuthUI();
      this.toast(`Welcome to ExpertConnect, ${body.first_name}! 🎉`);
    } catch(e) { this.toast(e.message,'❌'); }
  },

  logout() {
    this.user = null; this.token = null;
    localStorage.removeItem('eca_token');
    this.updateAuthUI();
    this.navigate('home');
    this.toast('Logged out successfully');
  },

  updateAuthUI() {
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const avatar = document.getElementById('navAvatar');
    if (this.user) {
      loginBtn.style.display = 'none'; signupBtn.style.display = 'none';
      avatar.style.display = 'flex';
      document.getElementById('avatarInitial').textContent = this.user.first_name.charAt(0);
    } else {
      loginBtn.style.display = ''; signupBtn.style.display = ''; avatar.style.display = 'none';
    }
  },

  toggleProFields() {
    document.getElementById('proFields').style.display = document.getElementById('signupRole').value === 'professional' ? 'block' : 'none';
  },

  // ===== DATA LOADING =====
  async loadCategories() {
    try { this.categories = await this.api('/categories'); this.renderCategories(); } catch(e) { console.error(e); }
  },

  async loadProvinces() {
    try { this.provinces = await this.api('/provinces'); this.populateProvinceSelects(); } catch(e) { console.error(e); }
  },

  async loadProfessionals() {
    try { this.professionals = await this.api('/professionals'); } catch(e) { console.error(e); }
  },

  // ===== RENDERING =====
  renderCategories() {
    const grid = document.getElementById('categoryGrid');
    const heroCat = document.getElementById('heroCategory');
    const browseCat = document.getElementById('browseCategory');
    if (!grid) return;
    grid.innerHTML = this.categories.map(c => `<div class="category-card" onclick="App.browseCategory(${c.id})"><div class="category-icon"><span>${c.icon}</span></div><h3>${c.name}</h3><p>${c.professional_count} experts</p></div>`).join('');
    const opts = this.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    if (heroCat) heroCat.innerHTML = '<option value="">All Categories</option>' + opts;
    if (browseCat) browseCat.innerHTML = '<option value="">All Categories</option>' + opts;
    this.renderFilterChips();
  },

  renderFilterChips() {
    const el = document.getElementById('filterChips');
    if (!el) return;
    el.innerHTML = `<button class="filter-chip active" onclick="App.setFilterChip(this,'')">All</button>` + this.categories.map(c => `<button class="filter-chip" onclick="App.setFilterChip(this,${c.id})">${c.icon} ${c.name}</button>`).join('');
  },

  setFilterChip(el, catId) {
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('browseCategory').value = catId;
    this.filterPros();
  },

  populateProvinceSelects() {
    const hero = document.getElementById('signupProvince');
    const browse = document.getElementById('browseProvince');
    const opts = this.provinces.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    if (hero) hero.innerHTML = '<option value="">Select province</option>' + opts;
    if (browse) browse.innerHTML = '<option value="">All Provinces</option>' + opts;
  },

  loadMunicipalities() {
    const provId = document.getElementById('signupProvince').value;
    const munSelect = document.getElementById('signupMunicipality');
    const prov = this.provinces.find(p => p.id == provId);
    munSelect.innerHTML = '<option value="">Select municipality</option>' + (prov ? prov.municipalities.map(m => `<option value="${m.id}">${m.name}</option>`).join('') : '');
  },

  populateSignupSelects() {
    const catSelect = document.getElementById('signupCategory');
    if (catSelect) catSelect.innerHTML = '<option value="">Select category</option>' + this.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  },

  renderFeatured() {
    const grid = document.getElementById('featuredGrid');
    if (!grid) return;
    grid.innerHTML = this.professionals.slice(0, 6).map(p => this.proCard(p)).join('');
  },

  renderBrowse(pros) {
    const grid = document.getElementById('browseGrid');
    const count = document.getElementById('browseCount');
    if (!grid) return;
    grid.innerHTML = pros.length ? pros.map(p => this.proCard(p)).join('') : '<div style="grid-column:1/-1;text-align:center;padding:60px;"><div style="font-size:3rem;margin-bottom:12px;">🔍</div><h3>No professionals found</h3><p style="color:var(--text-light);">Try adjusting your filters.</p></div>';
    if (count) count.innerHTML = `Showing <strong>${pros.length}</strong> professional${pros.length!==1?'s':''}`;
  },

  proCard(p) {
    const cat = (p.category || '').toLowerCase().replace(/\s*&\s*\w+/g,'').replace(' ','');
    const statusMap = {available:'🟢 Available',busy:'🟡 Busy',offline:'⚫ Offline',on_leave:'🟠 On Leave'};
    const statusClass = `status-${p.availability_status}`;
    const initial = p.user_name ? p.user_name.split(' ').map(n=>n[0]).join('') : '??';
    return `<div class="pro-card" onclick="App.viewProfile(${p.id})">
      <div class="pro-card-top"><div class="pro-avatar ${cat}">${initial}</div><div class="pro-info"><h3>${p.user_name||'Professional'}</h3><div class="spec">${p.specialty}</div><div class="loc">📍 ${p.address||'Africa'}</div></div></div>
      <div class="pro-card-mid"><div class="pro-rating"><span class="stars">${this.stars(p.rating)}</span><span class="rating-num">${p.rating}</span><span class="rating-count">(${p.review_count} reviews)</span><span class="${statusClass}">${statusMap[p.availability_status]||''}</span></div>
      <div class="pro-tags">${(p.tags||[]).map(t=>`<span class="pro-tag">${t}</span>`).join('')}${p.is_verified?'<span class="pro-tag" style="background:#E8F5E9;color:#2E7D32;">✅ Verified</span>':''}${p.offers_video?'<span class="pro-tag">📹</span>':''}${p.offers_house_call?'<span class="pro-tag">🏠</span>':''}</div>
      <div class="pro-price">R${p.consultation_price} <small>per session</small></div></div>
      <div class="pro-card-bot"><button class="btn btn-outline btn-sm" onclick="event.stopPropagation();App.viewProfile(${p.id})">Profile</button><button class="btn btn-primary btn-sm" onclick="event.stopPropagation();App.quickBook(${p.id})">Book Now</button></div></div>`;
  },

  stars(r) { const f=Math.floor(r); return '★'.repeat(f)+'☆'.repeat(5-f); },

  filterPros() {
    const q = (document.getElementById('browseSearch')?.value||'').toLowerCase();
    const catId = document.getElementById('browseCategory')?.value;
    const provId = document.getElementById('browseProvince')?.value;
    const sort = document.getElementById('browseSort')?.value;
    const video = document.getElementById('filterVideo')?.checked;
    const house = document.getElementById('filterHouseCall')?.checked;
    const verified = document.getElementById('filterVerified')?.checked;
    let filtered = this.professionals.filter(p => {
      if (q && !`${p.user_name} ${p.specialty} ${p.address} ${p.business_name}`.toLowerCase().includes(q)) return false;
      if (catId && p.category_id != catId) return false;
      if (video && !p.offers_video) return false;
      if (house && !p.offers_house_call) return false;
      if (verified && !p.is_verified) return false;
      return true;
    });
    if (sort==='rating') filtered.sort((a,b)=>b.rating-a.rating);
    else if (sort==='price-low') filtered.sort((a,b)=>a.consultation_price-b.consultation_price);
    else if (sort==='price-high') filtered.sort((a,b)=>b.consultation_price-a.consultation_price);
    else if (sort==='reviews') filtered.sort((a,b)=>b.review_count-a.review_count);
    this.renderBrowse(filtered);
  },

  browseCategory(catId) {
    this.navigate('browse');
    setTimeout(() => { document.getElementById('browseCategory').value = catId; this.filterPros(); }, 100);
  },

  heroSearch() {
    const q = document.getElementById('heroSearch').value;
    const cat = document.getElementById('heroCategory').value;
    this.navigate('browse');
    setTimeout(() => {
      document.getElementById('browseSearch').value = q;
      if (cat) document.getElementById('browseCategory').value = cat;
      this.filterPros();
    }, 100);
  },

  // ===== PROFILE =====
  async viewProfile(id) {
    try {
      const pro = await this.api(`/professionals/${id}`);
      this.selectedPro = pro;
      const initial = pro.user_name ? pro.user_name.split(' ').map(n=>n[0]).join('') : '??';
      const cat = (pro.category||'').toLowerCase().replace(/\s*&\s*\w+/g,'').replace(' ','');
      document.getElementById('profileAvatar').textContent = initial;
      document.getElementById('profileAvatar').className = `profile-avatar-lg pro-avatar ${cat}`;
      document.getElementById('profileName').textContent = pro.user_name;
      document.getElementById('profileSpec').textContent = pro.specialty;
      document.getElementById('profileLoc').textContent = `📍 ${pro.address||'Africa'}`;
      document.getElementById('profileBio').textContent = pro.bio;
      const statusMap = {available:'🟢 Available',busy:'🟡 Busy',offline:'⚫ Offline',on_leave:'🟠 On Leave'};
      document.getElementById('profileBadges').innerHTML = `${pro.is_verified?'<span class="profile-badge">✅ Verified</span>':''}<span class="profile-badge">${statusMap[pro.availability_status]||''}</span>${pro.offers_video?'<span class="profile-badge">📹 Video</span>':''}${pro.offers_voice?'<span class="profile-badge">📞 Voice</span>':''}${pro.offers_chat?'<span class="profile-badge">💬 Chat</span>':''}${pro.offers_house_call?'<span class="profile-badge">🏠 House Call</span>':''}`;
      document.getElementById('profileStats').innerHTML = `<div class="profile-stat"><div class="num">${pro.rating}★</div><div class="lbl">Rating</div></div><div class="profile-stat"><div class="num">${pro.review_count}</div><div class="lbl">Reviews</div></div><div class="profile-stat"><div class="num">${pro.total_patients}+</div><div class="lbl">Patients</div></div><div class="profile-stat"><div class="num">${pro.experience_years||0} yrs</div><div class="lbl">Experience</div></div>`;
      document.getElementById('profileServices').innerHTML = (pro.services||[]).map(s=>`<div class="service-item"><div><h4>${s.name}</h4><p>${s.description||''}</p></div><div class="price">R${s.price}</div></div>`).join('');
      document.getElementById('profileReviews').innerHTML = (pro.recent_reviews||[]).map(r=>`<div class="review-card"><div class="review-header"><div class="review-author"><div class="review-avatar">${r.client_name||'U'}</div><div><h4>${r.client_name||'User'}</h4><p>${r.created_at?new Date(r.created_at).toLocaleDateString():''}</p></div></div><span class="stars">${this.stars(r.rating)}</span></div><p class="review-text">${r.comment||''}</p></div>`).join('') || '<p style="color:var(--text-light);">No reviews yet.</p>';
      const svcSelect = document.getElementById('bookingService');
      svcSelect.innerHTML = (pro.services||[]).map((s,i)=>`<option value="${s.id}">${s.name} — R${s.price}</option>`).join('') || `<option value="">General Consultation — R${pro.consultation_price}</option>`;
      this.navigate('profile');
    } catch(e) { this.toast('Failed to load profile','❌'); }
  },

  quickBook(id) { this.viewProfile(id); setTimeout(()=>this.showModal('bookingModal'),300); },

  // ===== BOOKING =====
  setDefaultDate() {
    const d = new Date(); d.setDate(d.getDate()+1);
    const el = document.getElementById('bookingDate');
    if (el) { el.min = d.toISOString().split('T')[0]; el.value = d.toISOString().split('T')[0]; }
  },

  async confirmBooking() {
    if (!this.user) { this.closeModal('bookingModal'); this.showModal('loginModal'); this.toast('Please log in first','🔒'); return; }
    const p = this.selectedPro;
    if (!p) { this.closeModal('bookingModal'); this.toast('Please select a professional','⚠️'); return; }
    const svc = document.getElementById('bookingService');
    const svcId = svc?.value;
    const svcOpt = svc?.options[svc.selectedIndex];
    const priceMatch = svcOpt?.textContent?.match(/R(\d+)/);
    const price = priceMatch ? parseInt(priceMatch[1]) : p.consultation_price;
    const body = {
      professional_id: p.id,
      service_id: svcId || null,
      booking_type: document.getElementById('bookingType')?.value || 'online',
      consultation_type: document.getElementById('consultType')?.value || 'video',
      date: document.getElementById('bookingDate')?.value,
      time: document.getElementById('bookingTime')?.value || '10:00',
      notes: document.getElementById('bookingNotes')?.value || '',
      family_member_name: document.getElementById('bookingFamily')?.value || null,
    };
    if (!body.date) return this.toast('Please select a date','⚠️');
    try {
      const data = await this.api('/bookings', { method:'POST', body:JSON.stringify(body) });
      this.closeModal('bookingModal');
      this.toast(`Booking confirmed! Invoice: ${data.invoice?.invoice_number} 📧`);
    } catch(e) { this.toast(e.message,'❌'); }
  },

  selectConsultType(el, type) {
    document.querySelectorAll('.consult-type').forEach(c=>c.classList.remove('active'));
    el.classList.add('active');
  },

  selectSlot(el) {
    document.querySelectorAll('.hero-slot').forEach(s=>s.classList.remove('active'));
    el.classList.add('active');
  },

  // ===== AI ASSISTANT =====
  async sendAiMessage() {
    const input = document.getElementById('aiInput');
    const msg = input.value.trim();
    if (!msg) return;
    const container = document.getElementById('aiMessages');
    container.innerHTML += `<div class="ai-msg user">${this.escape(msg)}</div>`;
    input.value = '';
    container.scrollTop = container.scrollHeight;
    try {
      const data = await this.api('/ai/assist', { method:'POST', body:JSON.stringify({message:msg}) });
      let html = `<div class="ai-msg bot">${data.response}`;
      if (data.professionals?.length) {
        html += data.professionals.map(p => `<div class="pro-suggestion" onclick="App.viewProfile(${p.id})"><h4>${p.name} — ${p.specialty}</h4><p>⭐ ${p.rating} • R${p.price} ${p.offers_video?'• 📹 Video':''}</p></div>`).join('');
      }
      html += '</div>';
      container.innerHTML += html;
      container.scrollTop = container.scrollHeight;
    } catch(e) {
      container.innerHTML += `<div class="ai-msg bot">Sorry, I encountered an error. Please try again.</div>`;
    }
  },

  // ===== EMERGENCY =====
  async renderEmergency() {
    const grid = document.getElementById('emergencyGrid');
    if (!grid) return;
    const icons = { ambulance:'🚑', police:'👮', fire:'🚒', doctor:'🏥', security:'🛡️' };
    const categories = [
      {name:'Ambulance Services',cat:'ambulance',phone:'082 911',desc:'24/7 Emergency Medical Response'},
      {name:'ER24 Emergency',cat:'ambulance',phone:'084 124',desc:'24/7 Emergency Medical Response'},
      {name:'South African Police Service',cat:'police',phone:'10111',desc:'Crime Reporting & Emergency'},
      {name:'Fire & Rescue Services',cat:'fire',phone:'10177',desc:'24/7 Fire Emergency'},
      {name:'Gender-Based Violence Helpline',cat:'security',phone:'0800 428 428',desc:'24/7 Support & Counselling'},
      {name:'Suicide Helpline',cat:'doctor',phone:'0800 567 567',desc:'24/7 Mental Health Support'},
      {name:'Childline South Africa',cat:'security',phone:'0800 055 555',desc:'24/7 Children\'s Helpline'},
      {name:'Netcare 911',cat:'ambulance',phone:'082 911',desc:'24/7 Medical Emergency'},
    ];
    grid.innerHTML = categories.map(c => `<div class="emergency-card"><h3>${icons[c.cat]||'📞'} ${c.name}</h3><div class="category">${c.desc}</div><div class="phone">${c.phone}</div><div class="hours">⏰ Available 24/7</div><a href="tel:${c.phone.replace(/\s/g,'')}" class="btn btn-outline" style="width:100%;margin-top:12px;">📞 Call Now</a></div>`).join('');
  },

  // ===== NAVIGATION =====
  navigate(page, section) {
    document.querySelectorAll('.page-view').forEach(p=>p.classList.remove('active'));
    const target = document.getElementById(`page-${page}`);
    if (target) target.classList.add('active');
    document.querySelectorAll('.nav-links a').forEach(a=>a.classList.remove('active'));
    const link = document.querySelector(`.nav-links a[data-page="${page}"]`);
    if (link) link.classList.add('active');
    window.scrollTo({top:0,behavior:'smooth'});
    if (page === 'browse') this.filterPros();
    if (page === 'dashboard') this.loadDashboard();
    if (page === 'pro-dashboard') this.loadProDashboard();
  },

  // ===== DASHBOARD =====
  async loadDashboard() {
    if (!this.user) { this.navigate('home'); this.showModal('loginModal'); return; }
    document.getElementById('dashTitle').textContent = `Welcome back, ${this.user.first_name}! 👋`;
    document.getElementById('dashStats').innerHTML = `<div class="stat-card"><div class="stat-icon green">📅</div><h3>-</h3><p>Total Bookings</p></div><div class="stat-card"><div class="stat-icon blue">⏳</h3><h3>-</h3><p>Upcoming</p></div><div class="stat-card"><div class="stat-icon yellow">⭐</div><h3>-</h3><p>Reviews</p></div><div class="stat-card"><div class="stat-icon purple">🏆</div><h3>${this.user.loyalty?.points||100}</h3><p>Loyalty Points</p></div>`;
    try {
      const bookings = await this.api('/bookings');
      document.getElementById('dashBookings').innerHTML = bookings.length ? bookings.slice(0,5).map(b=>`<div class="booking-item"><div class="booking-date"><div class="day">${b.date?new Date(b.date).getDate():''}</div><div class="month">${b.date?new Date(b.date).toLocaleString('default',{month:'short'}):''}</div></div><div class="booking-info"><h4>${b.professional_name||'Professional'}</h4><p>${b.service_name||b.consultation_type||''} • ${b.time||''}</p></div><span class="booking-status status-${b.status}">${b.status}</span></div>`).join('') : '<p style="color:var(--text-light);padding:20px 0;">No bookings yet. <a href="#" onclick="App.navigate(\'browse\')" style="color:var(--primary);">Browse professionals</a> to get started.</p>';
    } catch(e) { document.getElementById('dashBookings').innerHTML = '<p style="color:var(--text-light);">No bookings yet.</p>'; }
    try {
      const notifs = await this.api('/notifications');
      document.getElementById('dashNotifications').innerHTML = notifs.length ? notifs.slice(0,5).map(n=>`<div class="notif-item"><div class="notif-dot ${n.notif_type==='booking'?'green':n.notif_type==='reminder'?'yellow':'blue'}"></div><div><p>${n.title}</p><small style="color:var(--text-light);">${n.message}</small></div></div>`).join('') : '<p style="color:var(--text-light);">No notifications.</p>';
    } catch(e) {}
    try {
      const loyalty = await this.api('/loyalty');
      document.getElementById('dashLoyalty').innerHTML = `<div style="text-align:center;padding:20px;"><div style="font-size:3rem;font-weight:800;color:var(--secondary);">${loyalty.points}</div><p style="color:var(--text-light);">Available Points</p><p style="font-size:.85rem;color:var(--text-light);">Total earned: ${loyalty.total_earned} • Redeemed: ${loyalty.total_redeemed}</p></div>`;
    } catch(e) {}
  },

  async loadProDashboard() {
    if (!this.user) { this.navigate('home'); this.showModal('loginModal'); return; }
    const pro = this.user.professional_profile;
    document.getElementById('proStats').innerHTML = pro ? `<div class="stat-card"><div class="stat-icon green">📅</div><h3>${pro.total_bookings||0}</h3><p>Total Bookings</p></div><div class="stat-card"><div class="stat-icon blue">⭐</div><h3>${pro.rating}★</h3><p>Rating</p></div><div class="stat-card"><div class="stat-icon yellow">👥</div><h3>${pro.total_patients||0}</h3><p>Patients</p></div><div class="stat-card"><div class="stat-icon purple">💰</div><h3>R${(pro.total_bookings||0)*(pro.consultation_price||0)}</h3><p>Estimated Earnings</p></div>` : '<p>Please create a professional profile first.</p>';
  },

  async setStatus(status) { this.toast(`Status updated to: ${status}`); },

  // ===== CHAT =====
  toggleChat() { document.getElementById('chatWindow').classList.toggle('open'); },
  closeChat() { document.getElementById('chatWindow').classList.remove('open'); },
  sendChat() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;
    const container = document.getElementById('chatMessages');
    container.innerHTML += `<div class="chat-msg sent">${this.escape(msg)}</div>`;
    input.value = '';
    container.scrollTop = container.scrollHeight;
    const responses = ["I'd be happy to help! What type of professional are you looking for?","You can browse professionals on the Browse page. Would you like suggestions?","Our platform supports video calls, voice calls, chat, and in-person visits.","You can book a professional right now by clicking 'Book Now' on any profile!","For emergencies, check the 🚨 Emergency page for 24/7 helplines.","ExpertConnect operates across all 9 provinces in South Africa!"];
    setTimeout(() => { container.innerHTML += `<div class="chat-msg received">${responses[Math.floor(Math.random()*responses.length)]}</div>`; container.scrollTop = container.scrollHeight; }, 800);
  },

  // ===== DOCUMENTS =====
  async uploadDocument() {
    if (!this.user) { this.showModal('loginModal'); return; }
    this.toast('Document upload feature ready. Connect a file to upload.','📄');
    this.closeModal('uploadModal');
  },

  // ===== LANGUAGE =====
  setLanguage(lang) {
    this.currentLang = lang;
    localStorage.setItem('eca_lang', lang);
    const t = translations[lang] || translations.en;
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (t[key]) el.innerHTML = t[key];
    });
    const langNames = {en:'🇬🇧 EN',zu:'🇿🇦 ZU',st:'🇿🇦 ST',tn:'🇿🇦 TN',xh:'🇿🇦 XH',af:'🇿🇦 AF'};
    document.getElementById('langBtn').textContent = `🌍 ${langNames[lang]||lang.toUpperCase()}`;
    document.getElementById('langDropdown').classList.remove('show');
  },

  toggleLangMenu() { document.getElementById('langDropdown').classList.toggle('show'); },

  // ===== MODALS =====
  showModal(id) { document.getElementById(id).classList.add('active'); document.body.style.overflow='hidden'; },
  closeModal(id) { document.getElementById(id).classList.remove('active'); document.body.style.overflow=''; },

  // ===== UI HELPERS =====
  toggleUserMenu() { document.getElementById('userDropdown').classList.toggle('show'); },
  toggleMobileNav() { document.getElementById('mobileNav').classList.toggle('open'); },
  closeMobileNav() { document.getElementById('mobileNav').classList.remove('open'); },

  setupScrollNav() {
    window.addEventListener('scroll', () => {
      document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 50);
    });
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.user-dropdown') && !e.target.closest('.nav-avatar')) document.getElementById('userDropdown')?.classList.remove('show');
      if (!e.target.closest('.lang-selector')) document.getElementById('langDropdown')?.classList.remove('show');
    });
    document.querySelectorAll('.modal-overlay').forEach(o => o.addEventListener('click', function(e) { if (e.target===this) { this.classList.remove('active'); document.body.style.overflow=''; } }));
    document.addEventListener('keydown', (e) => { if (e.key==='Escape') { document.querySelectorAll('.modal-overlay.active').forEach(m=>{m.classList.remove('active');document.body.style.overflow='';}); this.closeChat(); this.closeMobileNav(); } });
  },

  toast(msg, icon='✅') {
    const t = document.getElementById('toast');
    document.getElementById('toastMsg').textContent = msg;
    document.getElementById('toastIcon').textContent = icon;
    t.classList.add('show');
    setTimeout(()=>t.classList.remove('show'), 4000);
  },

  escape(s) { const d=document.createElement('div');d.textContent=s;return d.innerHTML; },
};

// Initialize
document.addEventListener('DOMContentLoaded', () => App.init());