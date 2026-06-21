const API = window.location.origin + '/api';
const App = {
  user: null, token: localStorage.getItem('eca_t'), cats: [], pros: [], selPro: null,
  favs: JSON.parse(localStorage.getItem('eca_favs') || '[]'),

  async init() {
    this.events();
    this.applyDarkMode();
    try {
      const [cats, pros] = await Promise.all([this.fetch('/categories'), this.fetch('/professionals')]);
      this.cats = cats; this.pros = pros;
    } catch { this.toast('Could not load data', '⚠️'); return; }
    this.renderCats(); this.renderChips(); this.renderFeatured(); this.renderEmergency();
    this.popSelects();
    const d = new Date(); d.setDate(d.getDate() + 1);
    const el = document.getElementById('bookingDate');
    if (el) { el.min = d.toISOString().split('T')[0]; el.value = d.toISOString().split('T')[0]; }
    if (this.token) try { this.user = await this.fetch('/auth/me'); this.ui(); } catch { this.token = null; localStorage.removeItem('eca_t'); }
  },

  async fetch(url, opts = {}) {
    const h = { 'Content-Type': 'application/json', ...opts.headers };
    if (this.token) h['Authorization'] = 'Bearer ' + this.token;
    const r = await fetch(API + url, { ...opts, headers: h });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || 'Request failed');
    return d;
  },

  toast(m, ic = '✅') {
    document.getElementById('toast').querySelector('span').textContent = m;
    document.querySelector('.toast .ic').textContent = ic;
    document.getElementById('toast').classList.add('show');
    setTimeout(() => document.getElementById('toast').classList.remove('show'), 4000);
  },

  go(p) {
    document.querySelectorAll('.page').forEach(x => x.classList.remove('active'));
    const e = document.getElementById('page-' + p);
    if (e) e.classList.add('active');
    document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
    const l = document.querySelector(`.nav-links a[data-page="${p}"]`);
    if (l) l.classList.add('active');
    window.scrollTo({ top: 0 });
    if (p === 'browse') this.filter();
    if (p === 'dashboard' && this.user) this.dash();
    if (p === 'favourites') this.renderFavs();
  },

  popSelects() {
    const opts = this.cats.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    document.getElementById('heroCategory').innerHTML = '<option value="">All categories</option>' + opts;
    document.getElementById('browseCategory').innerHTML = '<option value="">All categories</option>' + opts;
    document.getElementById('signupCat').innerHTML = '<option value="">Select category</option>' + opts;
  },

  // ===== DARK MODE =====
  toggleDark() {
    document.body.classList.toggle('dark');
    localStorage.setItem('eca_dark', document.body.classList.contains('dark') ? '1' : '0');
    this.applyDarkMode();
  },
  applyDarkMode() {
    if (localStorage.getItem('eca_dark') === '1') document.body.classList.add('dark');
    else document.body.classList.remove('dark');
  },

  // ===== WHATSAPP BOOKING =====
  waBook(proId, proName) {
    const msg = `Hi ExpertConnect! I'd like to book an appointment with ${proName}. Can you help me with availability?`;
    window.open(`https://wa.me/27741000000?text=${encodeURIComponent(msg)}`, '_blank');
    this.toast('Opening WhatsApp...', '📱');
  },

  // ===== REFERRAL =====
  getReferralLink() {
    const code = this.user?.id || 'guest';
    const link = `https://expertconnect.app/ref/${code}`;
    if (navigator.share) {
      navigator.share({ title: 'ExpertConnect Africa', text: 'Get R50 free credit! Join ExpertConnect and book trusted professionals.', url: link });
    } else {
      navigator.clipboard.writeText(link);
      this.toast('Referral link copied! Share it and earn R50', '🔗');
    }
  },

  // ===== FAVOURITES =====
  toggleFav(id) {
    const idx = this.favs.indexOf(id);
    if (idx > -1) this.favs.splice(idx, 1);
    else this.favs.push(id);
    localStorage.setItem('eca_favs', JSON.stringify(this.favs));
    this.filter();
    this.toast(idx > -1 ? 'Removed from favourites' : 'Added to favourites ❤️');
  },
  isFav(id) { return this.favs.includes(id); },
  renderFavs() {
    const f = this.pros.filter(p => this.favs.includes(p.id));
    document.getElementById('favGrid').innerHTML = f.length ? f.map(p => this.card(p)).join('') :
      '<div style="grid-column:1/-1;text-align:center;padding:60px 20px;"><div style="font-size:3rem;margin-bottom:12px;">❤️</div><h3>No favourites yet</h3><p style="color:var(--slate-400)">Tap the heart icon on a professional to save them here.</p></div>';
  },

  // ===== RENDER =====
  renderCats() {
    document.getElementById('categoryGrid').innerHTML = this.cats.map(c =>
      `<div class="cat-card" onclick="App.browseCat(${c.id})"><div class="i">${c.icon}</div><h3>${c.name}</h3><p>${c.count} pros</p></div>`
    ).join('');
  },

  renderChips() {
    document.getElementById('filterChips').innerHTML =
      '<button class="filter-chip active" onclick="App.chip(this,\'\')">All</button>' +
      this.cats.map(c => `<button class="filter-chip" onclick="App.chip(this,${c.id})">${c.icon} ${c.name}</button>`).join('');
  },

  chip(el, id) {
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('browseCategory').value = id;
    this.filter();
  },

  renderFeatured() {
    document.getElementById('featuredGrid').innerHTML = this.pros.slice(0, 6).map(p => this.card(p)).join('');
  },

  renderEmergency() {
    const data = [
      { n: 'Netcare 911', c: 'ambulance', p: '082 911' }, { n: 'ER24', c: 'ambulance', p: '084 124' },
      { n: 'SAPS', c: 'police', p: '10111' }, { n: 'Fire & Rescue', c: 'fire', p: '10177' },
      { n: 'GBV Helpline', c: 'counselling', p: '0800 428 428' }, { n: 'Suicide Helpline', c: 'counselling', p: '0800 567 567' },
    ];
    const ic = { ambulance: '🚑', police: '👮', fire: '🚒', counselling: '📞' };
    document.getElementById('emergencyGrid').innerHTML = data.map(x =>
      `<div class="e-card"><h3>${ic[x.c] || '📞'} ${x.n}</h3><div class="c">${x.c.charAt(0).toUpperCase() + x.c.slice(1)}</div><div class="ph">${x.p}</div><div class="hr">⏰ 24/7</div><a href="tel:${x.p.replace(/\s/g, '')}" class="btn btn-outline" style="width:100%;margin-top:10px;">📞 Call</a></div>`
    ).join('');
  },

  avClass(cat) {
    const m = { 'Healthcare': 'av-1', 'Legal Services': 'av-2', 'Education': 'av-3', 'Business Services': 'av-4',
                'Home Services': 'av-5', 'Technology': 'av-6', 'Fitness & Wellness': 'av-7', 'Financial Advisory': 'av-8' };
    return m[cat] || 'av-1';
  },

  card(p) {
    const sm = { available: '<span class="badge badge-green">🟢 Available</span>', busy: '<span class="badge badge-amber">🟡 Busy</span>',
                 offline: '<span class="badge badge-slate">⚫ Offline</span>', leave: '<span class="badge badge-red">🟠 Leave</span>' };
    const st = '★'.repeat(Math.round(p.rating)) + '☆'.repeat(5 - Math.round(p.rating));
    const isFav = this.isFav(p.id) ? '❤️' : '🤍';
    return `<div class="pro-card" onclick="App.viewPro(${p.id})"><div class="t"><div class="av ${this.avClass(p.category)}">${p.initials || 'NN'}</div><div class="info"><h3>${p.name} ${p.plan === 'professional' ? '🏆' : ''}</h3><div class="s">${p.specialty}</div><div class="l">${p.address || 'Africa'}</div></div><button class="fav-btn" onclick="event.stopPropagation();App.toggleFav(${p.id})">${isFav}</button></div><div class="m"><div class="r"><span class="stars">${st}</span><strong>${p.rating}</strong><span style="color:var(--slate-400)">(${p.reviews_count})</span>${sm[p.status] || ''}</div><div class="tags">${p.verified ? '<span class="tag" style="background:#d1fae5;color:#065f46">✅ Verified</span>' : ''}${p.bookings_count > 100 ? '<span class="tag" style="background:#fef3c7;color:#92400e">🏆 Top Pro</span>' : ''}${p.has_video ? '<span class="tag">📹</span>' : ''}${p.has_house ? '<span class="tag">🏠</span>' : ''}</div><div class="pr">R${p.price} <small>/ session</small></div></div><div class="b"><button class="btn btn-outline btn-sm" onclick="event.stopPropagation();App.viewPro(${p.id})">Profile</button><button class="btn btn-primary btn-sm" onclick="event.stopPropagation();App.qb(${p.id})">Book</button><button class="btn btn-amber btn-sm" onclick="event.stopPropagation();App.waBook(${p.id},'${p.name}')">📱</button></div></div>`;
  },

  filter() {
    const q = (document.getElementById('browseSearch').value || '').toLowerCase();
    const cat = document.getElementById('browseCategory').value;
    const s = document.getElementById('browseSort').value;
    const v = document.getElementById('filterVideo').checked;
    const h = document.getElementById('filterHouse').checked;
    const ve = document.getElementById('filterVerified').checked;
    let f = this.pros.filter(p => {
      if (q && !`${p.name}${p.specialty}${p.address}${p.business}`.toLowerCase().includes(q)) return false;
      if (cat && p.category_id != cat) return false;
      if (v && !p.has_video) return false;
      if (h && !p.has_house) return false;
      if (ve && !p.verified) return false;
      return true;
    });
    if (s === 'rating') f.sort((a, b) => b.rating - a.rating);
    else if (s === 'price_low') f.sort((a, b) => a.price - b.price);
    else if (s === 'price_high') f.sort((a, b) => b.price - a.price);
    else if (s === 'reviews') f.sort((a, b) => b.reviews_count - a.reviews_count);
    document.getElementById('browseGrid').innerHTML = f.length ? f.map(p => this.card(p)).join('') :
      '<div style="grid-column:1/-1;text-align:center;padding:60px 20px;"><div style="font-size:2.5rem;margin-bottom:12px;">🔍</div><h3>No professionals found</h3><p style="color:var(--slate-400)">Try different filters.</p></div>';
    document.getElementById('browseCount').innerHTML = `Showing <strong>${f.length}</strong> professional${f.length !== 1 ? 's' : ''}`;
  },

  browseCat(id) { this.go('browse'); setTimeout(() => { document.getElementById('browseCategory').value = id; this.filter(); }, 100); },
  heroSearch() {
    const q = document.getElementById('heroSearch').value, cat = document.getElementById('heroCategory').value;
    this.go('browse');
    setTimeout(() => { document.getElementById('browseSearch').value = q; if (cat) document.getElementById('browseCategory').value = cat; this.filter(); }, 100);
  },

  selectConsult(el) { document.querySelectorAll('.hero-ct-item').forEach(c => c.classList.remove('active')); el.classList.add('active'); },
  selectSlot(el) { document.querySelectorAll('.hero-slot').forEach(s => s.classList.remove('active')); el.classList.add('active'); },

  // ===== AUTH =====
  async login() {
    const e = document.getElementById('loginEmail').value, p = document.getElementById('loginPass').value;
    if (!e || !p) return this.toast('Fill in all fields', '⚠️');
    try {
      const d = await this.fetch('/auth/login', { method: 'POST', body: JSON.stringify({ email: e, password: p }) });
      this.token = d.token; this.user = d.user; localStorage.setItem('eca_t', d.token);
      this.closeModal('login'); this.ui(); this.toast('Welcome back! 👋');
    } catch (e) { this.toast(e.message, '❌'); }
  },

  async signup() {
    const b = {
      email: document.getElementById('signupEmail').value, password: document.getElementById('signupPass').value,
      first_name: document.getElementById('signupFirst').value, last_name: document.getElementById('signupLast').value,
      phone: document.getElementById('signupPhone').value, province: document.getElementById('signupProv').value,
      role: document.getElementById('signupRole').value
    };
    if (!b.email || !b.password || !b.first_name || !b.last_name) return this.toast('Fill in all fields', '⚠️');
    if (document.getElementById('refCode')?.value) b.referral = document.getElementById('refCode').value;
    if (b.role === 'professional') {
      b.category_id = document.getElementById('signupCat').value;
      b.specialty = document.getElementById('signupSpec').value;
      b.business = document.getElementById('signupBus').value;
      b.price = parseFloat(document.getElementById('signupPrice').value) || 0;
    }
    try {
      const d = await this.fetch('/auth/register', { method: 'POST', body: JSON.stringify(b) });
      this.token = d.token; this.user = d.user; localStorage.setItem('eca_t', d.token);
      this.closeModal('signup'); this.ui(); this.toast('Welcome! You got R50 free credit! 🎉');
    } catch (e) { this.toast(e.message, '❌'); }
  },

  logout() { this.user = null; this.token = null; localStorage.removeItem('eca_t'); this.ui(); this.go('home'); this.toast('Logged out'); },
  ui() {
    document.getElementById('loginBtn').style.display = this.user ? 'none' : '';
    document.getElementById('signupBtn').style.display = this.user ? 'none' : '';
    document.getElementById('refBtn').style.display = this.user ? 'inline-flex' : 'none';
    const av = document.getElementById('avatarBtn');
    if (this.user) { av.style.display = 'flex'; document.getElementById('avatarText').textContent = this.user.first_name[0]; }
    else av.style.display = 'none';
  },
  togglePro() { document.getElementById('proFields').style.display = document.getElementById('signupRole').value === 'professional' ? 'block' : 'none'; },

  // ===== PROFILE =====
  async viewPro(id) {
    try {
      const p = await this.fetch(`/professionals/${id}`);
      this.selPro = p;
      document.getElementById('profileAvatar').textContent = p.initials || 'NN';
      document.getElementById('profileAvatar').className = `profile-av ${this.avClass(p.category)}`;
      document.getElementById('profileName').textContent = p.name;
      document.getElementById('profileSpec').textContent = p.specialty;
      document.getElementById('profileLoc').textContent = '📍 ' + (p.address || 'Africa');
      document.getElementById('profileBio').textContent = p.bio;
      const sm = { available: '🟢 Available', busy: '🟡 Busy', offline: '⚫ Offline', leave: '🟠 Leave' };
      document.getElementById('profileBadges').innerHTML =
        (p.verified ? '<span class="badge badge-green">✅ Verified</span>' : '') +
        (p.bookings_count > 100 ? '<span class="badge badge-amber">🏆 Top Pro</span>' : '') +
        `<span class="badge badge-blue">${sm[p.status] || ''}</span>` +
        (p.has_video ? '<span class="badge badge-slate">📹 Video</span>' : '') +
        (p.has_house ? '<span class="badge badge-slate">🏠 House</span>' : '');
      document.getElementById('profileStats').innerHTML =
        `<div class="profile-stat"><div class="n">${p.rating}★</div><div class="l">Rating</div></div>` +
        `<div class="profile-stat"><div class="n">${p.reviews_count}</div><div class="l">Reviews</div></div>` +
        `<div class="profile-stat"><div class="n">${p.bookings_count}</div><div class="l">Bookings</div></div>`;
      document.getElementById('profileServices').innerHTML = (p.services || []).map(s =>
        `<div class="svc-item"><div><h4>${s.name}</h4><p>${s.description || ''}</p></div><div class="pr">R${s.price}</div></div>`
      ).join('') || '<p style="color:var(--slate-400)">No services listed.</p>';
      document.getElementById('profileReviews').innerHTML = (p.reviews || []).map(r =>
        `<div class="rv-card"><div class="rh"><div class="ra"><div class="ra-av">${r.client_name ? r.client_name[0] : 'U'}</div><div><h4>${r.client_name || 'User'}</h4></div></div><span class="stars">${'★'.repeat(r.rating)}</span></div><p>${r.comment || ''}</p></div>`
      ).join('') || '<p style="color:var(--slate-400)">No reviews yet.</p>';
      const sv = document.getElementById('bookingService');
      sv.innerHTML = (p.services || []).map(s => `<option value="${s.id}">${s.name} — R${s.price}</option>`).join('') ||
        `<option value="">Consultation — R${p.price}</option>`;
      this.go('profile');
    } catch { this.toast('Failed to load profile', '❌'); }
  },

  qb(id) { this.viewPro(id); setTimeout(() => this.modal('booking'), 300); },

  // ===== MODALS =====
  modal(id) {
    document.getElementById('modal-' + id).classList.add('active');
    document.body.style.overflow = 'hidden';
    if (id === 'booking' && this.selPro) {
      const p = this.selPro;
      const sv = document.getElementById('bookingService');
      const opt = sv.options[sv.selectedIndex];
      const price = opt?.textContent?.match(/R(\d+)/)?.[1] || p.price;
      document.getElementById('bookingSummary').innerHTML =
        `<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;"><div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#059669,#f59e0b);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:.875rem;">${p.initials || 'P'}</div><div><h4 style="font-size:.9375rem;font-weight:600;">${p.name}</h4><p style="font-size:.8125rem;color:var(--slate-400)">${p.specialty}</p></div></div>` +
        `<div style="display:flex;gap:16px;font-size:.875rem;color:var(--slate-500)">📅 ${document.getElementById('bookingDate').value || 'Today'} 🕐 ${document.getElementById('bookingTime').value || '09:00'}</div>`;
      document.getElementById('bookingTotal').textContent = 'R' + price + '.00';
    }
  },
  closeModal(id) { document.getElementById('modal-' + id).classList.remove('active'); document.body.style.overflow = ''; },

  async confirmBooking() {
    if (!this.user) { this.closeModal('booking'); this.modal('login'); return this.toast('Please log in', '🔒'); }
    const p = this.selPro;
    if (!p) { this.closeModal('booking'); return this.toast('Select a professional', '⚠️'); }
    try {
      const d = await this.fetch('/bookings', {
        method: 'POST', body: JSON.stringify({
          professional_id: p.id, service_id: document.getElementById('bookingService').value || null,
          type: document.getElementById('bookingType').value, consult: document.getElementById('consultType').value,
          date: document.getElementById('bookingDate').value, time: document.getElementById('bookingTime').value,
          notes: document.getElementById('bookingNotes').value, family: document.getElementById('bookingFamily').value || null
        })
      });
      this.closeModal('booking');
      this.toast('Booking confirmed! Invoice: ' + (d.invoice?.number || 'pending') + ' 📧');
    } catch (e) { this.toast(e.message, '❌'); }
  },

  // ===== AI =====
  async aiSend() {
    const input = document.getElementById('aiInput'), msg = input.value.trim();
    if (!msg) return;
    const c = document.getElementById('aiMessages');
    c.innerHTML += `<div class="ai-msg user">${this.esc(msg)}</div>`;
    input.value = ''; c.scrollTop = c.scrollHeight;
    try {
      const d = await this.fetch('/ai/assist', { method: 'POST', body: JSON.stringify({ message: msg }) });
      let h = `<div class="ai-msg bot">${d.response}`;
      if (d.professionals?.length) h += d.professionals.map(p =>
        `<div class="ps" onclick="App.viewPro(${p.id})"><h4>${p.name} — ${p.specialty}</h4><p>⭐ ${p.rating} • R${p.price} <button class="btn btn-sm btn-amber" style="padding:4px 10px;font-size:.75rem" onclick="event.stopPropagation();App.waBook(${p.id},'${p.name}')">📱 WhatsApp</button></p></div>`
      ).join('');
      h += '</div>'; c.innerHTML += h; c.scrollTop = c.scrollHeight;
    } catch { c.innerHTML += '<div class="ai-msg bot">Sorry, try again.</div>'; }
  },

  // ===== DASHBOARD =====
  async dash() {
    document.getElementById('dashTitle').textContent = 'Welcome, ' + (this.user?.first_name || 'User') + '! 👋';
    document.getElementById('dashStats').innerHTML = `
      <div class="stat-card"><div class="i g">📅</div><h3>-</h3><p>Bookings</p></div>
      <div class="stat-card"><div class="i b">⭐</div><h3>${this.favs.length}</h3><p>Favourites</p></div>
      <div class="stat-card"><div class="i a">🏆</div><h3>${this.user?.loyalty_points || 0}</h3><p>Points</p></div>
      <div class="stat-card"><div class="i p">R50</div><h3>1</h3><p>Referrals</p></div>`;
    try {
      const b = await this.fetch('/bookings');
      document.getElementById('dashBookings').innerHTML = b.length ? b.slice(0, 5).map(b =>
        `<div class="bk-item"><div class="d"><div class="dd">${b.date ? new Date(b.date).getDate() : ''}</div><div class="dm">${b.date ? new Date(b.date).toLocaleString('default', { month: 'short' }) : ''}</div></div><div class="info"><h4>${b.pro_name}</h4><p>${b.service_name || b.type} • ${b.time}</p></div><div class="flex gap-2"><span class="st st-${b.status}">${b.status}</span><button class="btn btn-sm btn-ghost" onclick="App.waBook(null,'${b.pro_name}')">📱</button></div></div>`
      ).join('') : '<p style="color:var(--slate-400);padding:20px 0;">No bookings yet. <a href="#" onclick="App.go(\'browse\')" style="color:var(--primary-dark);font-weight:600;">Browse professionals</a></p>';
    } catch {}
    try {
      const n = await this.fetch('/notifications');
      document.getElementById('dashNotifs').innerHTML = n.length ? n.slice(0, 5).map(n =>
        `<div style="display:flex;gap:10px;padding:10px 0;border-bottom:1px solid var(--slate-100);font-size:.875rem;"><div style="width:6px;height:6px;border-radius:50%;background:${n.type === 'booking' ? '#059669' : '#f59e0b'};margin-top:6px;flex-shrink:0;"></div><div><p style="font-weight:600;">${n.title}</p><p style="font-size:.75rem;color:var(--slate-400)">${n.message}</p></div></div>`
      ).join('') : '<p style="color:var(--slate-400)">No notifications.</p>';
    } catch {}
  },

  // ===== CHAT =====
  toggleChat() { document.getElementById('chatWindow').classList.toggle('open'); },
  closeChat() { document.getElementById('chatWindow').classList.remove('open'); },
  sendChat() {
    const input = document.getElementById('chatInput'), msg = input.value.trim();
    if (!msg) return;
    const c = document.getElementById('chatMessages');
    c.innerHTML += `<div class="chat-m s">${this.esc(msg)}</div>`;
    input.value = ''; c.scrollTop = c.scrollHeight;
    const r = ["How can I help?", "Looking for a specific pro?", "We support video, voice & chat!", "Try AI assistant!", "For emergencies use 🚨", "Earn R50 per referral! Share with friends!"];
    setTimeout(() => { c.innerHTML += `<div class="chat-m r">${r[Math.floor(Math.random() * r.length)]}</div>`; c.scrollTop = c.scrollHeight; }, 600);
  },

  // ===== EVENTS =====
  events() {
    document.addEventListener('click', e => {
      if (!e.target.closest('.avatar-btn') && !e.target.closest('.dropdown')) document.getElementById('userDropdown')?.classList.remove('show');
    });
    document.querySelectorAll('.modal-overlay').forEach(m => m.addEventListener('click', function(e) {
      if (e.target === this) { this.classList.remove('active'); document.body.style.overflow = ''; }
    }));
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(m => { m.classList.remove('active'); document.body.style.overflow = ''; });
        this.closeChat(); document.getElementById('mobileNav').classList.remove('open');
      }
    });
  },

  toggleDropdown() { document.getElementById('userDropdown').classList.toggle('show'); },
  toggleMobile() { document.getElementById('mobileNav').classList.toggle('open'); },

  esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
};

document.addEventListener('DOMContentLoaded', () => App.init());