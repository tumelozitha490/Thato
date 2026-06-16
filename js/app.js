/* ===== ExpertConnect Africa - Application Logic ===== */

// ===== DATA =====
const categories = [
  { id: 'healthcare', name: 'Healthcare', icon: '🩺', count: 850, category: 'Healthcare', desc: 'Doctors, dentists, therapists' },
  { id: 'legal', name: 'Legal Services', icon: '⚖️', count: 420, category: 'Legal', desc: 'Lawyers, notaries, consultants' },
  { id: 'education', name: 'Education', icon: '📚', count: 680, category: 'Education', desc: 'Tutors, coaches, mentors' },
  { id: 'business', name: 'Business', icon: '💼', count: 530, category: 'Business', desc: 'Accountants, tax, advisors' },
  { id: 'home', name: 'Home Services', icon: '🏠', count: 390, category: 'Home', desc: 'Electricians, plumbers, handymen' },
  { id: 'technology', name: 'Technology', icon: '💻', count: 310, category: 'Technology', desc: 'Developers, IT, designers' },
  { id: 'fitness', name: 'Fitness & Wellness', icon: '💪', count: 280, category: 'Healthcare', desc: 'Trainers, dietitians, physios' },
  { id: 'finance', name: 'Financial Services', icon: '📈', count: 220, category: 'Business', desc: 'Advisors, planners, auditors' },
];

const professionals = [
  {
    id: 1,
    name: 'Dr. Amina Osei',
    initials: 'AO',
    type: 'doctor',
    specialty: 'General Practitioner',
    category: 'Healthcare',
    location: 'Johannesburg, South Africa',
    rating: 4.9,
    reviewCount: 127,
    patients: '500+',
    experience: '12 yrs',
    price: 350,
    priceSymbol: 'R',
    tags: ['Family Medicine', 'Preventive Care', 'Chronic Disease'],
    online: true,
    featured: true,
    bio: 'Dr. Amina Osei is a highly experienced General Practitioner with over 12 years of clinical practice. She specializes in family medicine, preventive care, and chronic disease management. Registered with HPCSA.',
    services: [
      { name: 'General Consultation', desc: 'In-person consultation', price: 350 },
      { name: 'Follow-up Visit', desc: 'Returning patient review', price: 200 },
      { name: 'Health Certificate', desc: 'Medical fitness certificate', price: 500 },
      { name: 'Video Consultation', desc: 'Online video call', price: 300 },
    ],
    reviews: [
      { author: 'Nomsa K.', initials: 'NK', rating: 5, text: 'Dr. Osei is incredibly thorough and caring. She took the time to explain everything and made me feel comfortable. Highly recommended!', date: '2 weeks ago' },
      { author: 'James M.', initials: 'JM', rating: 5, text: 'Best doctor I have visited. Professional, knowledgeable, and genuinely cares about her patients.', date: '1 month ago' },
      { author: 'Fatima A.', initials: 'FA', rating: 4, text: 'Great experience. The online booking was seamless and the consultation was thorough.', date: '2 months ago' },
    ]
  },
  {
    id: 2,
    name: 'Adv. Bongani Ndlovu',
    initials: 'BN',
    type: 'lawyer',
    specialty: 'Corporate Lawyer',
    category: 'Legal',
    location: 'Cape Town, South Africa',
    rating: 4.8,
    reviewCount: 89,
    patients: '300+',
    experience: '15 yrs',
    price: 500,
    priceSymbol: 'R',
    tags: ['Corporate Law', 'Contracts', 'M&A'],
    online: true,
    featured: true,
    bio: 'Advocate Bongani Ndlovu specializes in corporate and commercial law with 15 years of experience. He has advised major corporations across Southern Africa on mergers, acquisitions, and regulatory compliance.',
    services: [
      { name: 'Legal Consultation', desc: '1-hour consultation', price: 500 },
      { name: 'Contract Review', desc: 'Review and advice on contracts', price: 800 },
      { name: 'Company Registration', desc: 'Full CIPC registration', price: 1200 },
      { name: 'Labour Dispute', desc: 'Employment law advice', price: 600 },
    ],
    reviews: [
      { author: 'Sipho D.', initials: 'SD', rating: 5, text: 'Adv. Ndlovu handled our company merger with exceptional skill. Very professional and knowledgeable.', date: '3 weeks ago' },
      { author: 'Lerato M.', initials: 'LM', rating: 5, text: 'Excellent lawyer. He explained all the legal complexities in simple terms.', date: '2 months ago' },
    ]
  },
  {
    id: 3,
    name: 'Sarah Mensah',
    initials: 'SM',
    type: 'tutor',
    specialty: 'Mathematics Tutor',
    category: 'Education',
    location: 'Accra, Ghana',
    rating: 4.9,
    reviewCount: 203,
    patients: '150+',
    experience: '8 yrs',
    price: 250,
    priceSymbol: 'R',
    tags: ['Mathematics', 'Grade 10-12', 'University Level'],
    online: true,
    featured: true,
    bio: 'Sarah Mensah is a passionate mathematics educator with 8 years of experience. She specializes in making complex mathematical concepts accessible and enjoyable for students at all levels.',
    services: [
      { name: '1-on-1 Tutoring', desc: '60-minute session', price: 250 },
      { name: 'Group Session', desc: 'Up to 4 students', price: 150 },
      { name: 'Exam Preparation', desc: 'Intensive 2-hour session', price: 400 },
      { name: 'Online Tutoring', desc: 'Video call session', price: 200 },
    ],
    reviews: [
      { author: 'Grace O.', initials: 'GO', rating: 5, text: 'My daughter went from a D to an A in maths within 3 months! Sarah is an amazing tutor.', date: '1 week ago' },
      { author: 'Kofi A.', initials: 'KA', rating: 5, text: 'Very patient and explains things clearly. Highly recommend for anyone struggling with maths.', date: '1 month ago' },
      { author: 'Aisha B.', initials: 'AB', rating: 5, text: 'Best tutor we have ever had. Worth every rand.', date: '3 months ago' },
    ]
  },
  {
    id: 4,
    name: 'Dr. Thabo Moyo',
    initials: 'TM',
    type: 'doctor',
    specialty: 'Dentist',
    category: 'Healthcare',
    location: 'Pretoria, South Africa',
    rating: 4.7,
    reviewCount: 95,
    patients: '400+',
    experience: '10 yrs',
    price: 400,
    priceSymbol: 'R',
    tags: ['General Dentistry', 'Cosmetic', 'Orthodontics'],
    online: false,
    featured: true,
    bio: 'Dr. Thabo Moyo is a skilled dentist offering comprehensive dental care including preventive, restorative, and cosmetic dentistry. HPCSA registered.',
    services: [
      { name: 'Dental Check-up', desc: 'Examination + X-rays', price: 400 },
      { name: 'Teeth Cleaning', desc: 'Professional cleaning', price: 600 },
      { name: 'Filling', desc: 'Composite filling', price: 800 },
      { name: 'Whitening', desc: 'Professional whitening', price: 2500 },
    ],
    reviews: [
      { author: 'Thandiwe N.', initials: 'TN', rating: 5, text: 'Dr. Moyo made my dental experience painless and comfortable. Very gentle hands!', date: '2 weeks ago' },
      { author: 'Pieter V.', initials: 'PV', rating: 4, text: 'Good service, professional environment. Will come back.', date: '1 month ago' },
    ]
  },
  {
    id: 5,
    name: 'Peter Adeyemi',
    initials: 'PA',
    type: 'accountant',
    specialty: 'Tax Consultant',
    category: 'Business',
    location: 'Lagos, Nigeria',
    rating: 4.8,
    reviewCount: 156,
    patients: '600+',
    experience: '18 yrs',
    price: 450,
    priceSymbol: 'R',
    tags: ['Tax Planning', 'SARS', 'Business Tax'],
    online: true,
    featured: true,
    bio: 'Peter Adeyemi is a seasoned tax consultant with 18 years of experience helping businesses and individuals optimize their tax positions across Africa.',
    services: [
      { name: 'Tax Consultation', desc: '1-hour consultation', price: 450 },
      { name: 'Tax Return Prep', desc: 'Individual IT return', price: 800 },
      { name: 'Business Tax', desc: 'Company tax filing', price: 2500 },
      { name: 'Tax Audit Support', desc: 'SARS audit assistance', price: 1500 },
    ],
    reviews: [
      { author: 'Chioma E.', initials: 'CE', rating: 5, text: 'Peter saved us thousands in tax. His knowledge is incredible and he explains everything clearly.', date: '1 month ago' },
      { author: 'David O.', initials: 'DO', rating: 5, text: 'Professional and efficient. Highly recommend for any tax matters.', date: '2 months ago' },
    ]
  },
  {
    id: 6,
    name: 'Lerato Dlamini',
    initials: 'LD',
    type: 'fitness',
    specialty: 'Personal Trainer',
    category: 'Healthcare',
    location: 'Durban, South Africa',
    rating: 4.9,
    reviewCount: 178,
    patients: '200+',
    experience: '6 yrs',
    price: 300,
    priceSymbol: 'R',
    tags: ['Strength Training', 'Weight Loss', 'Nutrition'],
    online: true,
    featured: false,
    bio: 'Lerato Dlamini is a certified personal trainer and nutritionist. She specializes in strength training, weight management, and holistic wellness programs.',
    services: [
      { name: 'Personal Training', desc: '1-hour session', price: 300 },
      { name: 'Online Coaching', desc: 'Monthly program', price: 1500 },
      { name: 'Meal Planning', desc: 'Custom nutrition plan', price: 800 },
      { name: 'Group Fitness', desc: 'Per session', price: 100 },
    ],
    reviews: [
      { author: 'Michelle R.', initials: 'MR', rating: 5, text: 'Lerato completely transformed my lifestyle. Lost 15kg in 4 months!', date: '3 weeks ago' },
      { author: 'Sibusiso K.', initials: 'SK', rating: 5, text: 'Best trainer in Durban. Very motivating and knowledgeable.', date: '1 month ago' },
    ]
  },
  {
    id: 7,
    name: 'Tendai Murapa',
    initials: 'TM',
    type: 'tech',
    specialty: 'Software Developer',
    category: 'Technology',
    location: 'Harare, Zimbabwe',
    rating: 4.7,
    reviewCount: 64,
    patients: '80+',
    experience: '9 yrs',
    price: 600,
    priceSymbol: 'R',
    tags: ['Web Development', 'Mobile Apps', 'UI/UX'],
    online: true,
    featured: false,
    bio: 'Tendai Murapa is a full-stack software developer with expertise in web applications, mobile apps, and user interface design. Building Africa\'s digital future.',
    services: [
      { name: 'Web Development', desc: 'Custom website', price: 5000 },
      { name: 'Consultation', desc: '1-hour tech consultation', price: 600 },
      { name: 'UI/UX Design', desc: 'App or web design', price: 3500 },
      { name: 'Code Review', desc: '1-hour code audit', price: 800 },
    ],
    reviews: [
      { author: 'Mutapa Z.', initials: 'MZ', rating: 5, text: 'Tendai built our e-commerce platform perfectly. On time and on budget.', date: '2 weeks ago' },
      { author: 'Anna K.', initials: 'AK', rating: 4, text: 'Very skilled developer. Great communication throughout the project.', date: '1 month ago' },
    ]
  },
  {
    id: 8,
    name: 'Dr. Ngozi Okonkwo',
    initials: 'NO',
    type: 'doctor',
    specialty: 'Psychologist',
    category: 'Healthcare',
    location: 'Abuja, Nigeria',
    rating: 4.9,
    reviewCount: 112,
    patients: '350+',
    experience: '14 yrs',
    price: 500,
    priceSymbol: 'R',
    tags: ['CBT', 'Anxiety', 'Depression', 'Trauma'],
    online: true,
    featured: true,
    bio: 'Dr. Ngozi Okonkwo is a clinical psychologist specializing in cognitive behavioral therapy. She helps individuals overcome anxiety, depression, and trauma with evidence-based approaches.',
    services: [
      { name: 'Therapy Session', desc: '50-minute session', price: 500 },
      { name: 'Couple Therapy', desc: 'Joint session', price: 700 },
      { name: 'Online Therapy', desc: 'Video call session', price: 450 },
      { name: 'Assessment', desc: 'Psychological evaluation', price: 1200 },
    ],
    reviews: [
      { author: 'Blessing I.', initials: 'BI', rating: 5, text: 'Dr. Okonkwo helped me through the darkest time in my life. She is compassionate and skilled.', date: '1 week ago' },
      { author: 'Emeka U.', initials: 'EU', rating: 5, text: 'Professional, warm, and truly understands mental health. Thank you.', date: '1 month ago' },
    ]
  },
  {
    id: 9,
    name: 'Amara Diallo',
    initials: 'AD',
    type: 'tutor',
    specialty: 'Career Coach',
    category: 'Education',
    location: 'Dakar, Senegal',
    rating: 4.8,
    reviewCount: 88,
    patients: '120+',
    experience: '7 yrs',
    price: 400,
    priceSymbol: 'R',
    tags: ['Career Planning', 'CV Review', 'Interview Prep'],
    online: true,
    featured: false,
    bio: 'Amara Diallo is a certified career coach helping professionals navigate their career paths. She offers guidance on career planning, CV optimization, and interview preparation.',
    services: [
      { name: 'Career Consultation', desc: '60-minute session', price: 400 },
      { name: 'CV/Resume Review', desc: 'Professional review + edits', price: 300 },
      { name: 'Interview Prep', desc: 'Mock interview session', price: 500 },
      { name: 'Career Plan', desc: 'Comprehensive career roadmap', price: 1200 },
    ],
    reviews: [
      { author: 'Fatou S.', initials: 'FS', rating: 5, text: 'Amara helped me land my dream job. Her interview tips are gold!', date: '2 weeks ago' },
      { author: 'Mohamed D.', initials: 'MD', rating: 5, text: 'Professional, insightful, and truly invested in her clients success.', date: '1 month ago' },
    ]
  },
  {
    id: 10,
    name: 'Thabo Molefe',
    initials: 'TM',
    type: 'fitness',
    specialty: 'Electrician',
    category: 'Home',
    location: 'Bloemfontein, South Africa',
    rating: 4.6,
    reviewCount: 73,
    patients: '250+',
    experience: '11 yrs',
    price: 350,
    priceSymbol: 'R',
    tags: ['Wiring', 'Solar', 'Maintenance', 'Compliance'],
    online: false,
    featured: false,
    bio: 'Thabo Molefe is a qualified and licensed electrician with 11 years of experience. He specializes in residential and commercial electrical work, including solar installations.',
    services: [
      { name: 'Electrical Inspection', desc: 'Full property inspection', price: 350 },
      { name: 'Fault Finding', desc: 'Diagnostic service', price: 450 },
      { name: 'Installation', desc: 'New wiring/fixtures', price: 600 },
      { name: 'Solar Setup', desc: 'Solar panel installation', price: 5000 },
    ],
    reviews: [
      { author: 'Johan P.', initials: 'JP', rating: 5, text: 'Thabo did excellent work on our solar installation. Very professional.', date: '3 weeks ago' },
      { author: 'Mary L.', initials: 'ML', rating: 4, text: 'Good service, arrived on time and fixed the issue quickly.', date: '1 month ago' },
    ]
  },
  {
    id: 11,
    name: 'Dr. Fatima Benali',
    initials: 'FB',
    type: 'doctor',
    specialty: 'Pharmacist',
    category: 'Healthcare',
    location: 'Casablanca, Morocco',
    rating: 4.7,
    reviewCount: 68,
    patients: '300+',
    experience: '9 yrs',
    price: 200,
    priceSymbol: 'R',
    tags: ['Medication Review', 'Drug Interaction', 'Chronic Meds'],
    online: true,
    featured: false,
    bio: 'Dr. Fatima Benali is a licensed pharmacist providing medication counseling and drug interaction reviews. She helps patients optimize their medication regimens.',
    services: [
      { name: 'Medication Review', desc: 'Full medication assessment', price: 200 },
      { name: 'Online Consultation', desc: 'Video pharmacist consult', price: 180 },
      { name: 'Chronic Care', desc: 'Monthly medication management', price: 350 },
    ],
    reviews: [
      { author: 'Amina R.', initials: 'AR', rating: 5, text: 'Dr. Benali caught a dangerous drug interaction my doctor missed. Lifesaver!', date: '2 weeks ago' },
    ]
  },
  {
    id: 12,
    name: 'Kwame Asante',
    initials: 'KA',
    type: 'accountant',
    specialty: 'Financial Advisor',
    category: 'Business',
    location: 'Kumasi, Ghana',
    rating: 4.8,
    reviewCount: 91,
    patients: '180+',
    experience: '13 yrs',
    price: 550,
    priceSymbol: 'R',
    tags: ['Investment', 'Retirement', 'Estate Planning'],
    online: true,
    featured: false,
    bio: 'Kwame Asante is a certified financial advisor helping individuals and businesses build wealth through smart investment and retirement planning.',
    services: [
      { name: 'Financial Planning', desc: 'Comprehensive plan', price: 1500 },
      { name: 'Investment Review', desc: 'Portfolio assessment', price: 550 },
      { name: 'Retirement Planning', desc: 'Retirement roadmap', price: 800 },
      { name: 'Quick Consultation', desc: '30-minute session', price: 300 },
    ],
    reviews: [
      { author: 'Abena O.', initials: 'AO', rating: 5, text: 'Kwame helped me set up a retirement plan that will secure my future. Excellent advisor.', date: '1 month ago' },
    ]
  },
];

const chatResponses = [
  "I'd be happy to help! What type of professional are you looking for?",
  "You can browse our professionals by category on the Browse page. Would you like me to suggest some top-rated options?",
  "Our platform supports secure online payments via credit card, debit card, and EFT.",
  "You can book a video consultation with any professional marked as 'online'. It's quick and easy!",
  "For any issues with a booking, you can request a refund within 24 hours through your dashboard.",
  "ExpertConnect operates across Africa — we have professionals in South Africa, Kenya, Nigeria, Ghana, and more!",
];

// ===== STATE =====
let currentUser = null;
let currentPage = 'home';
let selectedProfessional = null;

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
  renderCategories();
  renderFeaturedProfessionals();
  renderBrowsePage();
  renderFilterChips();
  setupScrollAnimations();
  setupNavbarScroll();
  setupSignupRoleToggle();
  setupModalCloseOnOverlay();
  setDefaultBookingDate();
});

// ===== NAVIGATION =====
function navigateTo(page, section) {
  // Hide all pages
  document.querySelectorAll('.page-view').forEach(p => p.classList.remove('active'));
  
  // Show target page
  const targetPage = document.getElementById('page-' + page);
  if (targetPage) {
    targetPage.classList.add('active');
  }
  
  // Update nav active state
  document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
  const activeLink = document.querySelector(`.nav-links a[data-page="${page}"]`);
  if (activeLink) activeLink.classList.add('active');
  
  // Scroll to top or section
  if (section) {
    setTimeout(() => {
      const el = document.getElementById(section);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  } else {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  currentPage = page;
  
  // Refresh browse grid when navigating to browse
  if (page === 'browse') {
    renderBrowseProfessionals(professionals);
  }
}

// ===== CATEGORIES =====
function renderCategories() {
  const grid = document.getElementById('categoryGrid');
  if (!grid) return;
  
  grid.innerHTML = categories.map(cat => `
    <div class="category-card" onclick="filterByCategory('${cat.category}')">
      <div class="category-icon"><span>${cat.icon}</span></div>
      <h3>${cat.name}</h3>
      <p>${cat.count} experts</p>
    </div>
  `).join('');
}

function filterByCategory(category) {
  navigateTo('browse');
  setTimeout(() => {
    const filter = document.getElementById('browseCategoryFilter');
    if (filter) {
      filter.value = category;
      filterBrowseProfessionals();
    }
    // Update filter chips
    document.querySelectorAll('.filter-chip').forEach(chip => {
      chip.classList.toggle('active', chip.dataset.category === category);
    });
  }, 100);
}

// ===== PROFESSIONALS RENDERING =====
function createProfessionalCard(pro) {
  const starsHtml = getStarsHtml(pro.rating);
  return `
    <div class="professional-card" onclick="viewProfile(${pro.id})">
      <div class="professional-card-header">
        <div class="professional-avatar ${pro.type}">${pro.initials}</div>
        <div class="professional-info">
          <h3>${pro.name}</h3>
          <div class="specialty">${pro.specialty}</div>
          <div class="location">📍 ${pro.location}</div>
        </div>
      </div>
      <div class="professional-card-body">
        <div class="professional-rating">
          <span class="stars">${starsHtml}</span>
          <strong>${pro.rating}</strong>
          <span class="rating-count">(${pro.reviewCount} reviews)</span>
          ${pro.online ? '<span class="online-dot"></span><span style="font-size:0.8rem; color:#4CAF50;">Online</span>' : ''}
        </div>
        <div class="professional-tags">
          ${pro.tags.map(tag => `<span class="professional-tag">${tag}</span>`).join('')}
        </div>
        <div class="professional-price">
          <span class="amount">${pro.priceSymbol}${pro.price}</span>
          <span class="period">per session</span>
        </div>
      </div>
      <div class="professional-card-footer">
        <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); viewProfile(${pro.id})">View Profile</button>
        <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); quickBook(${pro.id})">Book Now</button>
      </div>
    </div>
  `;
}

function renderFeaturedProfessionals() {
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;
  
  const featured = professionals.filter(p => p.featured);
  grid.innerHTML = featured.map(createProfessionalCard).join('');
}

function getStarsHtml(rating) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}

// ===== BROWSE PAGE =====
function renderFilterChips() {
  const container = document.getElementById('browseFilterChips');
  if (!container) return;
  
  const allCategories = ['Healthcare', 'Legal', 'Education', 'Business', 'Home', 'Technology'];
  container.innerHTML = `
    <button class="filter-chip active" data-category="" onclick="setFilterChip(this, '')">All</button>
    ${allCategories.map(cat => `
      <button class="filter-chip" data-category="${cat}" onclick="setFilterChip(this, '${cat}')">${cat}</button>
    `).join('')}
  `;
}

function setFilterChip(el, category) {
  document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('browseCategoryFilter').value = category;
  filterBrowseProfessionals();
}

function renderBrowsePage() {
  renderBrowseProfessionals(professionals);
}

function renderBrowseProfessionals(pros) {
  const grid = document.getElementById('browseGrid');
  if (!grid) return;
  
  if (pros.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
        <div style="font-size: 3rem; margin-bottom: 16px;">🔍</div>
        <h3 style="margin-bottom: 8px; color: var(--text-dark);">No professionals found</h3>
        <p style="color: var(--text-light);">Try adjusting your search or filter criteria.</p>
      </div>
    `;
  } else {
    grid.innerHTML = pros.map(createProfessionalCard).join('');
  }
  
  const info = document.getElementById('browseResultsInfo');
  if (info) {
    info.innerHTML = `Showing <strong>${pros.length}</strong> professional${pros.length !== 1 ? 's' : ''}`;
  }
}

function filterBrowseProfessionals() {
  const searchInput = document.getElementById('browseSearchInput');
  const categoryFilter = document.getElementById('browseCategoryFilter');
  const sortFilter = document.getElementById('browseSortFilter');
  
  const search = searchInput ? searchInput.value.toLowerCase() : '';
  const category = categoryFilter ? categoryFilter.value : '';
  const sort = sortFilter ? sortFilter.value : 'featured';
  
  let filtered = professionals.filter(pro => {
    const matchSearch = !search || 
      pro.name.toLowerCase().includes(search) || 
      pro.specialty.toLowerCase().includes(search) ||
      pro.tags.some(t => t.toLowerCase().includes(search)) ||
      pro.location.toLowerCase().includes(search);
    
    const matchCategory = !category || pro.category === category;
    
    return matchSearch && matchCategory;
  });
  
  // Sort
  switch(sort) {
    case 'rating':
      filtered.sort((a, b) => b.rating - a.rating);
      break;
    case 'price-low':
      filtered.sort((a, b) => a.price - b.price);
      break;
    case 'price-high':
      filtered.sort((a, b) => b.price - a.price);
      break;
    default: // featured
      filtered.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0));
  }
  
  renderBrowseProfessionals(filtered);
}

function performHeroSearch() {
  const input = document.getElementById('heroSearchInput');
  const category = document.getElementById('heroSearchCategory');
  
  const search = input ? input.value : '';
  const cat = category ? category.value : '';
  
  navigateTo('browse');
  
  setTimeout(() => {
    const browseInput = document.getElementById('browseSearchInput');
    const browseCategory = document.getElementById('browseCategoryFilter');
    
    if (browseInput) browseInput.value = search;
    if (browseCategory) browseCategory.value = cat;
    
    filterBrowseProfessionals();
  }, 200);
}

function handleHeroSearch(event) {
  if (event.key === 'Enter') {
    performHeroSearch();
  }
}

// ===== PROFESSIONAL PROFILE =====
function viewProfile(id) {
  const pro = professionals.find(p => p.id === id);
  if (!pro) return;
  
  selectedProfessional = pro;
  
  // Update profile page
  document.getElementById('profileAvatarLarge').textContent = pro.initials;
  document.getElementById('profileAvatarLarge').className = 'profile-avatar-large professional-avatar ' + pro.type;
  document.getElementById('profileName').textContent = pro.name;
  document.getElementById('profileSpecialty').textContent = pro.specialty;
  document.getElementById('profileLocation').textContent = '📍 ' + pro.location;
  document.getElementById('profileRating').textContent = pro.rating;
  document.getElementById('profileReviews').textContent = pro.reviewCount;
  document.getElementById('profilePatients').textContent = pro.patients;
  document.getElementById('profileExp').textContent = pro.experience;
  document.getElementById('profileBio').textContent = pro.bio;
  
  // Services
  const servicesList = document.getElementById('profileServices');
  if (servicesList) {
    servicesList.innerHTML = pro.services.map(s => `
      <div class="service-item">
        <div>
          <h4>${s.name}</h4>
          <p>${s.desc}</p>
        </div>
        <div class="price">${pro.priceSymbol}${s.price}</div>
      </div>
    `).join('');
  }
  
  // Reviews
  const reviewsList = document.getElementById('profileReviewsList');
  if (reviewsList) {
    reviewsList.innerHTML = pro.reviews.map(r => `
      <div class="review-card">
        <div class="review-card-header">
          <div class="review-author">
            <div class="review-avatar">${r.initials}</div>
            <div>
              <h4>${r.author}</h4>
              <p>${r.date}</p>
            </div>
          </div>
          <span class="stars">${getStarsHtml(r.rating)}</span>
        </div>
        <p class="review-text">${r.text}</p>
      </div>
    `).join('');
  }
  
  // Update booking sidebar
  const bookingService = document.getElementById('bookingService');
  if (bookingService && pro.services.length > 0) {
    bookingService.innerHTML = pro.services.map((s, i) => 
      `<option value="${i}">${s.name} — ${pro.priceSymbol}${s.price}</option>`
    ).join('');
  }
  
  // Update booking modal
  document.getElementById('bookingProName').textContent = pro.name;
  
  navigateTo('profile');
}

function quickBook(id) {
  viewProfile(id);
  setTimeout(() => openModal('bookingModal'), 300);
}

// ===== MODALS =====
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

function setupModalCloseOnOverlay() {
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function(e) {
      if (e.target === this) {
        this.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  });
}

// ===== AUTH =====
function loginUser() {
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  
  if (!email || !password) {
    showToast('Please fill in all fields', '⚠️');
    return;
  }
  
  // Simulate login
  currentUser = {
    name: email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    email: email,
  };
  
  closeModal('loginModal');
  updateUIForLoggedInUser();
  showToast(`Welcome back, ${currentUser.name}!`, '✅');
}

function signupUser() {
  const role = document.getElementById('signupRole').value;
  const first = document.getElementById('signupFirst').value;
  const last = document.getElementById('signupLast').value;
  const email = document.getElementById('signupEmail').value;
  const password = document.getElementById('signupPassword').value;
  
  if (!first || !last || !email || !password) {
    showToast('Please fill in all fields', '⚠️');
    return;
  }
  
  if (role === 'professional') {
    const category = document.getElementById('signupCategory').value;
    if (!category) {
      showToast('Please select your professional category', '⚠️');
      return;
    }
  }
  
  // Simulate signup
  currentUser = {
    name: first + ' ' + last,
    email: email,
    role: role,
  };
  
  closeModal('signupModal');
  updateUIForLoggedInUser();
  showToast(`Welcome to ExpertConnect, ${first}! 🎉`, '✅');
}

function logoutUser() {
  currentUser = null;
  updateUIForLoggedOutUser();
  navigateTo('home');
  showToast('You have been logged out', '👋');
  closeDropdown();
}

function updateUIForLoggedInUser() {
  document.getElementById('loginBtn').style.display = 'none';
  document.getElementById('signupBtn').style.display = 'none';
  
  const avatar = document.getElementById('navAvatar');
  avatar.style.display = 'flex';
  avatar.childNodes[0].textContent = currentUser.name.charAt(0);
  
  document.getElementById('dashboardUserName').textContent = currentUser.name.split(' ')[0];
}

function updateUIForLoggedOutUser() {
  document.getElementById('loginBtn').style.display = '';
  document.getElementById('signupBtn').style.display = '';
  document.getElementById('navAvatar').style.display = 'none';
}

function toggleDropdown() {
  document.getElementById('avatarDropdown').classList.toggle('show');
}

function closeDropdown() {
  document.getElementById('avatarDropdown').classList.remove('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
  const avatar = document.getElementById('navAvatar');
  if (avatar && !avatar.contains(e.target)) {
    closeDropdown();
  }
});

function setupSignupRoleToggle() {
  const roleSelect = document.getElementById('signupRole');
  if (roleSelect) {
    roleSelect.addEventListener('change', function() {
      const catGroup = document.getElementById('signupCategoryGroup');
      catGroup.style.display = this.value === 'professional' ? 'block' : 'none';
    });
  }
}

// ===== BOOKING =====
function setDefaultBookingDate() {
  const dateInput = document.getElementById('bookingDate');
  if (dateInput) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.min = tomorrow.toISOString().split('T')[0];
    dateInput.value = tomorrow.toISOString().split('T')[0];
  }
}

function updateBookingPrice() {
  const select = document.getElementById('bookingService');
  if (select && selectedProfessional) {
    const idx = parseInt(select.value);
    const service = selectedProfessional.services[idx];
    if (service) {
      document.getElementById('bookingPrice').textContent = selectedProfessional.priceSymbol + service.price;
    }
  }
}

function confirmBooking() {
  closeModal('bookingModal');
  
  if (!currentUser) {
    showToast('Please log in to complete your booking', '🔒');
    setTimeout(() => openModal('loginModal'), 500);
    return;
  }
  
  showToast('Booking confirmed! Check your email for details. 📧', '✅');
}

function selectSlot(el) {
  document.querySelectorAll('.hero-card-slot').forEach(s => s.classList.remove('active'));
  el.classList.add('active');
}

// ===== MOBILE NAV =====
function toggleMobileNav() {
  document.getElementById('mobileNav').classList.toggle('open');
}

function closeMobileNav() {
  document.getElementById('mobileNav').classList.remove('open');
}

// ===== NAVBAR SCROLL =====
function setupNavbarScroll() {
  window.addEventListener('scroll', function() {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

// ===== SCROLL ANIMATIONS =====
function setupScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
  
  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
  
  // Add animation classes to sections
  const sections = document.querySelectorAll('.categories, .how-it-works, .featured, .testimonials, .revenue, .cta');
  sections.forEach(section => {
    section.classList.add('animate-on-scroll');
    observer.observe(section);
  });
}

// ===== CHAT =====
function toggleChat() {
  document.getElementById('chatWindow').classList.toggle('open');
}

function openChat() {
  document.getElementById('chatWindow').classList.add('open');
}

function closeChat() {
  document.getElementById('chatWindow').classList.remove('open');
}

function sendChatMessage() {
  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;
  
  const messagesContainer = document.getElementById('chatMessages');
  
  // Add user message
  const userMsg = document.createElement('div');
  userMsg.className = 'chat-message sent';
  userMsg.textContent = message;
  messagesContainer.appendChild(userMsg);
  
  input.value = '';
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  
  // Simulate bot response
  setTimeout(() => {
    const response = chatResponses[Math.floor(Math.random() * chatResponses.length)];
    const botMsg = document.createElement('div');
    botMsg.className = 'chat-message received';
    botMsg.textContent = response;
    messagesContainer.appendChild(botMsg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }, 1000);
}

// ===== TOAST NOTIFICATIONS =====
function showToast(message, icon = '✅') {
  const toast = document.getElementById('toast');
  const toastMessage = document.getElementById('toastMessage');
  const toastIcon = toast.querySelector('.toast-icon');
  
  toastMessage.textContent = message;
  toastIcon.textContent = icon;
  
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 4000);
}

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', function(e) {
  // ESC closes modals
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(modal => {
      modal.classList.remove('active');
    });
    document.body.style.overflow = '';
    closeChat();
    closeMobileNav();
    closeDropdown();
  }
});