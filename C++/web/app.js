/* C++ Lab - course app
   Data-driven: every lesson comes from /data/*.json, nothing is hard-coded here. */

import * as Account from './auth.js';

const LEGACY_PROFILES = ['faith', 'praise'];   // only used to migrate old guest progress
const STORE = 'cpplab.v1.';
const GUEST = 'guest';
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const state = {
  course: null,
  levels: {},          // levelId -> {name, lessons:[...]}
  profile: 'guest',
  progress: {},        // per profile, or per account when signed in
  search: '',
  health: null,
  route: { name: 'home' },
  booted: false,
  user: null,          // signed-in Firebase user, or null
  sync: 'local',       // local | syncing | saved | error
  guestSession: false, // explicit "continue without saving" for offline use
  authReady: false,    // did the Firebase SDK start?
};

/* ------------------------------------------------------------------ utils */
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const KEYWORDS = [
  'alignas', 'auto', 'bool', 'break', 'case', 'catch', 'char', 'class', 'concept',
  'const', 'constexpr', 'continue', 'default', 'delete', 'do', 'double', 'else',
  'enum', 'explicit', 'false', 'float', 'for', 'friend', 'if', 'inline', 'int',
  'long', 'namespace', 'new', 'noexcept', 'nullptr', 'operator', 'private',
  'protected', 'public', 'requires', 'return', 'short', 'signed', 'sizeof',
  'static', 'static_assert', 'struct', 'switch', 'template', 'throw', 'true',
  'try', 'typedef', 'typename', 'unsigned', 'using', 'void', 'volatile', 'while',
];

const HL = new RegExp(
  '(\\/\\/[^\\n]*)|("(?:\\\\.|[^"\\\\])*")|(\'(?:\\\\.|[^\'\\\\])*\')|^([ \\t]*#[^\\n]*)' +
  '|\\b(' + KEYWORDS.join('|') + ')\\b|\\b(\\d+(?:\\.\\d+)?)\\b', 'gm');

function highlight(code) {
  let out = '', last = 0, m;
  HL.lastIndex = 0;
  while ((m = HL.exec(code)) !== null) {
    out += esc(code.slice(last, m.index));
    const cls = m[1] ? 'c' : m[2] || m[3] ? 's' : m[4] ? 'p' : m[5] ? 'k' : 'n';
    out += `<span class="${cls}">${esc(m[0])}</span>`;
    last = m.index + m[0].length;
  }
  return out + esc(code.slice(last));
}

function normalise(text) {
  return String(text ?? '')
    .replace(/\r\n?/g, '\n')
    .split('\n').map((l) => l.replace(/\s+$/, '')).join('\n')
    .replace(/^\n+|\n+$/g, '');
}

function toast(msg) {
  let t = $('.toast');
  if (!t) {
    t = document.createElement('div');
    t.className = 'toast';
    t.setAttribute('role', 'status');
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 2400);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    ta.remove();
    return ok;
  }
}

/* ------------------------------------------------------------- persistence */
function blank() {
  return { completed: {}, quiz: {}, drafts: {}, last: null, visits: 0 };
}

function loadProfile(name) {
  try {
    const raw = localStorage.getItem(STORE + name);
    return raw ? { ...blank(), ...JSON.parse(raw) } : blank();
  } catch {
    return blank();
  }
}

/** Storage suffix: the account, when there is one. */
function storeSuffix() {
  return state.user ? `u.${state.user.uid}` : null;
}

/* ------------------------------------------------------------- account UI */
function renderAccount() {
  const el = $('#accountArea');
  if (!el) return;

  // while the gate is showing, the header carries no account buttons
  if (isGated() && state.course) {
    el.innerHTML = '';
    const sub = $('#brandSub');
    if (sub) sub.textContent = `C++20 · ${state.course.total} lessons`;
    return;
  }

  if (state.user) {
    const name = Account.prettyName(state.user);
    const syncText = { syncing: 'saving…', saved: 'saved', error: 'offline — kept here', local: 'saved here' }[state.sync] || '';
    el.innerHTML = `
      <div class="who" title="${esc(state.user.email || '')}">
        <span class="avatar" aria-hidden="true">${esc((name[0] || '?').toUpperCase())}</span>
        <span class="who-text"><b>${esc(name)}</b><small data-sync>${esc(syncText)}</small></span>
      </div>
      <button class="btn ghost small" type="button" data-signout>Sign out</button>`;
    $('[data-signout]', el).addEventListener('click', async () => {
      await Account.signOutNow();
      toast('Signed out. Your progress stays on this device.');
    });
  } else {
    el.innerHTML = `
      <button class="btn ghost small" type="button" data-open-signin>Sign in</button>
      <button class="btn small" type="button" data-open-auth>Create account</button>`;
    $('[data-open-signin]', el).addEventListener('click', () => openAuthModal('signin'));
    $('[data-open-auth]', el).addEventListener('click', () => openAuthModal('signup'));
  }

  const note = $('#localNote');
  if (note) {
    if (!state.user) {
      note.textContent = 'You are not signed in. Progress stays in this browser — make an account to keep it everywhere.';
    } else if (state.sync === 'saved') {
      note.textContent = `Signed in as ${Account.prettyName(state.user)}. Progress is saved to this account and follows you to another device.`;
    } else {
      note.textContent = `Signed in as ${Account.prettyName(state.user)}. Progress is saved on this device; cloud sync is not working yet, so it does not follow you to other devices.`;
    }
  }

  // the subtitle follows whoever is signed in, never a hard-coded name
  const sub = $('#brandSub');
  if (sub) {
    const total = state.course ? state.course.total : 46;
    sub.textContent = state.user
      ? Account.prettyName(state.user)
      : `C++20 · ${total} lessons`;
  }
  document.title = state.user
    ? `C++ Lab · ${Account.prettyName(state.user)}`
    : 'C++ Lab · C++20 for beginners';
}

let modalEl = null;

function openAuthModal(mode = 'signin') {
  if (!state.authReady) {
    toast('Accounts need an internet connection. You can keep learning as a guest.');
    return;
  }
  closeAuthModal();

  modalEl = document.createElement('div');
  modalEl.className = 'modal-back';
  modalEl.innerHTML = `
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="authTitle">
      <button class="modal-x" type="button" aria-label="Close" data-close>×</button>
      <h2 id="authTitle">Save your progress</h2>
      <p class="modal-sub">Make an account and your lessons follow you to any device.</p>

      <div class="auth-tabs" role="tablist">
        <button type="button" role="tab" data-mode="signup">Create account</button>
        <button type="button" role="tab" data-mode="signin">Sign in</button>
      </div>

      <label class="field" data-name-field hidden>
        <span>Your name</span>
        <input name="name" autocomplete="nickname" placeholder="Ana" maxlength="30">
      </label>
      <label class="field">
        <span>Name or email</span>
        <input name="email" autocomplete="username" placeholder="ana" required>
      </label>
      <label class="field">
        <span>Password</span>
        <input name="password" type="password" autocomplete="current-password" placeholder="at least 6 characters" required>
      </label>

      <p class="auth-hint" data-hint></p>
      <div class="auth-error" data-error hidden></div>
      <button class="btn wide" type="button" data-submit>Sign in</button>
      <p class="modal-foot">Nobody else can read your progress — the database only lets you open your own record.</p>
    </div>`;
  document.body.appendChild(modalEl);
  document.body.classList.add('modal-open');

  const form = $('.modal', modalEl);
  const setMode = (next) => {
    modalEl.dataset.mode = next;
    $$('[data-mode]', form).forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === next)));
    const nameField = $('[data-name-field]', form);
    nameField.hidden = next !== 'signup';
    nameField.style.display = next === 'signup' ? '' : 'none';   // beats .field { display:block }
    $('[data-submit]', form).textContent = next === 'signup' ? 'Create my account' : 'Sign in';
    $('[data-hint]', form).textContent = next === 'signup'
      ? 'A name is enough — we turn “ana” into ana@cpplab.local, so no email address is needed.'
      : 'Type the same name (or email) and password you used when you made the account.';
    $('[name=password]', form).setAttribute('autocomplete', next === 'signup' ? 'new-password' : 'current-password');
    showError('');
    ($('[data-name-field]', form).hidden ? $('[name=email]', form) : $('[name=name]', form)).focus();
  };

  const showError = (msg) => {
    const box = $('[data-error]', form);
    box.hidden = !msg;
    box.textContent = msg;
  };

  $$('[data-mode]', form).forEach((b) => b.addEventListener('click', () => setMode(b.dataset.mode)));
  $('[data-close]', form).addEventListener('click', closeAuthModal);
  modalEl.addEventListener('mousedown', (e) => { if (e.target === modalEl) closeAuthModal(); });

  form.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); submit(); }
    if (e.key === 'Escape') closeAuthModal();
  });

  async function submit() {
    const btn = $('[data-submit]', form);
    const mode2 = modalEl.dataset.mode;
    const name = ($('[name=name]', form).value || '').trim();
    const who = ($('[name=email]', form).value || '').trim();
    const pass = $('[name=password]', form).value || '';

    if (!who) return showError('Type a name first.');
    if (mode2 === 'signup' && pass.length < 6) return showError('Passwords need at least 6 characters.');

    btn.disabled = true;
    const label = btn.textContent;
    btn.textContent = mode2 === 'signup' ? 'Creating…' : 'Signing in…';
    showError('');
    try {
      if (mode2 === 'signup') await Account.signUp({ name, email: who, password: pass });
      else await Account.signIn({ email: who, password: pass });
      closeAuthModal();
      toast(mode2 === 'signup' ? 'Account created. Welcome!' : 'Signed in.');
    } catch (err) {
      showError(Account.friendlyError(err));
      btn.disabled = false;
      btn.textContent = label;
    }
  }

  $('[data-submit]', form).addEventListener('click', submit);
  setMode(mode);
}

function closeAuthModal() {
  if (modalEl) { modalEl.remove(); modalEl = null; }
  document.body.classList.remove('modal-open');
}

/* ------------------------------------------------------------ account boot */
async function adoptAccount(user) {
  state.user = user;
  state.guestSession = false;
  state.progress = loadProfile(`u.${user.uid}`);
  state.sync = 'syncing';
  // mirror first, so nothing is lost even if the cloud never answers
  localStorage.setItem(STORE + `u.${user.uid}`, JSON.stringify(state.progress));
  renderAccount();
  if (state.course) render();        // repaint immediately; the pull can take its time

  try {
    const cloud = await Account.pullProgress(user.uid);
    if (cloud && cloud.progress) {
      state.progress = mergeProgress(state.progress, cloud.progress);
      localStorage.setItem(STORE + `u.${user.uid}`, JSON.stringify(state.progress));
    }
    state.sync = 'saved';
  } catch {
    state.sync = 'error';       // saved here; will retry on the next change
  }

  renderAccount();
  if (state.course) render();
  if (!sessionStorage.getItem('cpplab.hello.' + user.uid)) {
    sessionStorage.setItem('cpplab.hello.' + user.uid, '1');
    toast(`Signed in as ${Account.prettyName(user)}.`);
  }
}

function releaseAccount() {
  state.user = null;
  state.sync = 'local';
  state.guestSession = false;      // signed out means: back to the sign-in gate
  state.progress = blank();
  renderAccount();
  if (state.course) render();
}


let cloudTimer = null;

function saveProfile() {
  // No account, no saved progress: a guest session lives in memory only.
  if (!state.user) return;
  try {
    state.progress.updated = new Date().toISOString();
    localStorage.setItem(STORE + storeSuffix(), JSON.stringify(state.progress));
  } catch (e) {
    toast('This browser refused to save progress (storage is full or blocked).');
  }
  queueCloudSave();
}

function queueCloudSave() {
  state.sync = 'syncing';
  renderAccount();
  clearTimeout(cloudTimer);
  cloudTimer = setTimeout(async () => {
    try {
      await Account.pushProgress(state.user.uid, {
        name: Account.prettyName(state.user),
        progress: state.progress,
      });
      state.sync = 'saved';
    } catch {
      state.sync = 'error';
    }
    renderAccount();
  }, 700);
}

/** Union of two progress objects: nothing a learner finished is ever lost. */
function mergeProgress(local, cloud) {
  const out = blank();
  out.completed = { ...(local.completed || {}), ...(cloud.completed || {}) };
  out.drafts = { ...(cloud.drafts || {}), ...(local.drafts || {}) };
  out.quiz = { ...(cloud.quiz || {}) };
  for (const [id, q] of Object.entries(local.quiz || {})) {
    const best = out.quiz[id];
    if (!best || (q.right || 0) > (best.right || 0)) out.quiz[id] = q;
  }
  out.last = cloud.last || local.last || null;
  out.visits = Math.max(local.visits || 0, cloud.visits || 0);
  return out;
}

/* -------------------------------------------------------------------- data */
async function getJSON(url) {
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

async function loadCourse() {
  state.course = await getJSON('/data/course.json');
  const results = await Promise.all(
    state.course.levels.map(async (lv) => {
      const data = await getJSON(`/data/lessons/${lv.id}.json`);
      const byId = Object.fromEntries(data.lessons.map((l) => [l.id, l]));
      return [lv.id, byId];
    })
  );
  state.levels = Object.fromEntries(results);
  state.best = {};   // id -> lesson
  for (const [lv, byId] of Object.entries(state.levels)) {
    for (const [id, lesson] of Object.entries(byId)) state.best[id] = lesson;
  }
  fetch('/api/health').then((r) => r.json()).then((h) => { state.health = h; render(); })
    .catch(() => { state.health = { ok: false, compiler: null }; render(); });
}

function lesson(id) { return state.best[id]; }
function levelOf(id) { return state.course.lessons.find((l) => l.id === id)?.level; }

function orderedLessons() {
  return state.course.levels.flatMap((lv) => lv.lessons);
}

/* ---------------------------------------------------------------- routing */
function parseHash() {
  const h = location.hash.replace(/^#\/?/, '');
  if (!h) return { name: 'landing' };
  if (h === 'home') return { name: 'home' };
  const [kind, id] = h.split('/');
  if (kind === 'signin') return { name: 'signin' };
  if (kind === 'signup') return { name: 'signup' };
  if (kind === 'lesson' && id) return { name: 'lesson', id };
  if (kind === 'level' && id) return { name: 'level', id };
  return { name: 'landing' };
}

function go(hash) {
  if (location.hash === hash) { render(); return; }
  location.hash = hash;
}

/* ---------------------------------------------------------------- landing */
function landingHTML() {
  const total = state.course ? state.course.total : 46;
  const levels = state.course ? state.course.levels : [];
  const minutes = state.course
    ? state.course.lessons.reduce((sum, l) => sum + l.minutes, 0)
    : 731;

  return `<div class="wrap landing">
    <section class="landing-hero">
      <span class="landing-kicker">C++20 · ${total} lessons</span>
      <h1>Learn C++ by <em>doing</em>,<br>not by copying.</h1>
      <p class="landing-lead">
        A hands-on programming course for absolute beginners. Every lesson asks you to predict
        what the code does, run it on a real compiler, and then write your own version.
      </p>

      <div class="landing-cta">
        <a class="btn" href="#/signup">Create a free account</a>
        <a class="btn ghost" href="#/signin">I already have one</a>
      </div>

      <div class="credit">
        <div class="credit-avatar" aria-hidden="true">MA</div>
        <div>
          <strong>Built by Mr. Alegre</strong>
          <span>Developed for C++ beginners — and for two young learners who wanted a robot.</span>
        </div>
      </div>
    </section>

    <section class="landing-features">
      <article>
        <h3>Real compiler, real output</h3>
        <p>Code is compiled with <code>g++ -std=c++20</code>. If it does not build, you see the
           compiler's own message — never a fake “correct”.</p>
      </article>
      <article>
        <h3>Predict before you run</h3>
        <p>Every lesson starts with a question you answer before the explanation appears. Guessing
           wrong is the point — that is when it sticks.</p>
      </article>
      <article>
        <h3>Short lessons</h3>
        <p>${total} lessons of about 10–25 minutes, ${Math.round(minutes / 60)} hours in total,
           each ending in a small program you write yourself.</p>
      </article>
      <article>
        <h3>Progress that follows you</h3>
        <p>Sign in and your finished lessons, quiz scores and saved code follow you to any
           device — phone, tablet or laptop.</p>
      </article>
    </section>

    <section class="landing-levels">
      <h2>What you will learn</h2>
      <div class="levels">
        ${levels.map((lv) => `
          <div class="level-card landing-level">
            <div class="lc-top">
              <h3>${esc(lv.name)}</h3>
              <span class="tag time">${lv.lessons.length} lessons</span>
            </div>
            <p>${esc(lv.blurb)}</p>
          </div>`).join('')}
      </div>
    </section>

    <footer class="landing-foot">
      <p><strong>C++ Lab</strong> — built by Mr. Alegre for C++ beginners.</p>
      <p class="muted">Free, no ads. An account is only used to save your progress.</p>
    </footer>
  </div>`;
}

/* ------------------------------------------------------------------- gate */
function isGated() {
  return !state.user && !state.guestSession;
}

function gateHTML(mode = 'signin') {
  const total = state.course ? state.course.total : 46;
  return `<div class="gate">
    <form class="gate-card" data-gate data-start="${mode}" novalidate>
      <a class="gate-back" href="#/">← Back</a>
      <div class="gate-mark" aria-hidden="true">C++</div>
      <h1>Sign in to C++ Lab</h1>
      <p class="gate-sub">${total} short lessons in C++20. Your progress is saved to your account.</p>

      <div class="auth-tabs" role="tablist">
        <button type="button" role="tab" data-mode="signin" aria-pressed="${mode === 'signin'}">Sign in</button>
        <button type="button" role="tab" data-mode="signup" aria-pressed="${mode === 'signup'}">Create account</button>
      </div>

      <label class="field" data-name-field hidden>
        <span>Your name</span>
        <input name="name" autocomplete="nickname" placeholder="Ana" maxlength="30">
      </label>
      <label class="field">
        <span>Name or email</span>
        <input name="email" autocomplete="username" placeholder="ana" required>
      </label>
      <label class="field">
        <span>Password</span>
        <input name="password" type="password" autocomplete="current-password" placeholder="at least 6 characters" required>
      </label>

      <p class="auth-hint" data-hint></p>
      <div class="auth-error" data-error hidden></div>
      <button class="btn wide" type="submit" data-submit>Sign in</button>
      <button class="gate-skip" type="button" data-skip>Continue without an account — nothing is saved</button>
    </form>
  </div>`;
}

function bindGate(startMode = 'signin') {
  const form = $('[data-gate]');
  if (!form) return;

  const nameField = $('[data-name-field]', form);
  const submitBtn = $('[data-submit]', form);
  const errorBox = $('[data-error]', form);
  const hint = $('[data-hint]', form);

  const showError = (msg) => {
    errorBox.hidden = !msg;
    errorBox.textContent = msg;
  };

  const setMode = (mode) => {
    form.dataset.mode = mode;
    $$('[data-mode]', form).forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === mode)));
    nameField.hidden = mode !== 'signup';
    nameField.style.display = mode === 'signup' ? '' : 'none';
    submitBtn.textContent = mode === 'signup' ? 'Create my account' : 'Sign in';
    $('[name=password]', form).setAttribute('autocomplete', mode === 'signup' ? 'new-password' : 'current-password');
    hint.textContent = mode === 'signup'
      ? 'A name is enough — we turn “ana” into ana@cpplab.local, so no email address is needed.'
      : 'Use the same name and password you signed up with.';
    showError('');
    (mode === 'signup' ? $('[name=name]', form) : $('[name=email]', form)).focus();
  };

  $$('[data-mode]', form).forEach((b) => b.addEventListener('click', () => setMode(b.dataset.mode)));

  $('[data-skip]', form).addEventListener('click', () => {
    state.guestSession = true;
    state.progress = blank();
    toast('Continuing without an account — progress will not be saved.');
    render();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const mode = form.dataset.mode;
    const name = ($('[name=name]', form).value || '').trim();
    const who = ($('[name=email]', form).value || '').trim();
    const pass = $('[name=password]', form).value || '';

    if (!who) return showError('Type a name first.');
    if (mode === 'signup' && pass.length < 6) return showError('Passwords need at least 6 characters.');

    submitBtn.disabled = true;
    const label = submitBtn.textContent;
    submitBtn.textContent = mode === 'signup' ? 'Creating…' : 'Signing in…';
    showError('');
    try {
      if (mode === 'signup') await Account.signUp({ name, email: who, password: pass });
      else await Account.signIn({ email: who, password: pass });
      // onAuthStateChanged takes over: adoptAccount() then render()
    } catch (err) {
      showError(Account.friendlyError(err));
      submitBtn.disabled = false;
      submitBtn.textContent = label;
    }
  });

  setMode(startMode);
}

/* ------------------------------------------------------------------ render */
function render() {
  if (!state.course) return;
  const route = parseHash();
  state.route = route;

  const publicView = !state.user && !state.guestSession;
  document.body.classList.toggle('gated', publicView);
  const main = $('#main');

  // someone signed in never needs the landing page or the sign-in screen
  if (state.user && ['landing', 'signin', 'signup'].includes(route.name)) {
    if (location.hash !== '#/home') location.hash = '#/home';
    return;
  }

  if (publicView) {
    $('#lessonNav').innerHTML = '';
    if (route.name === 'landing') {
      main.innerHTML = landingHTML();
      document.title = 'C++ Lab · learn C++20 from scratch';
      return;
    }
    const mode = route.name === 'signup' ? 'signup' : 'signin';
    main.innerHTML = gateHTML(mode);
    bindGate(mode);
    document.title = 'C++ Lab · sign in';
    return;
  }

  renderNav();
  if (state.route.name === 'lesson') {
    const l = lesson(state.route.id);
    main.innerHTML = l ? lessonHTML(l) : notFound(state.route.id);
    if (l) bindLesson(l);
    else main.innerHTML = notFound(state.route.id);
  } else if (state.route.name === 'level') {
    main.innerHTML = levelHTML(state.route.id);
  } else {
    main.innerHTML = homeHTML();
  }
  window.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
}

function doneCount(ids) {
  return ids.filter((id) => state.progress.completed[id]).length;
}

function pct(n, total) { return total ? Math.round((n / total) * 100) : 0; }

function renderNav() {
  const nav = $('#lessonNav');
  const query = state.search.trim().toLowerCase();
  let html = '';
  for (const lv of state.course.levels) {
    const ids = lv.lessons.filter((id) => {
      if (!query) return true;
      const l = lesson(id);
      return (l.title + ' ' + (l.tags || []).join(' ') + ' ' + l.goal).toLowerCase().includes(query);
    });
    if (query && !ids.length) continue;
    const done = doneCount(lv.lessons);
    html += `<button class="nav-level" type="button" data-level="${lv.id}">
      <span>${esc(lv.name)}</span><span class="count">${done}/${lv.lessons.length}</span></button>`;
    for (const id of ids) {
      const l = lesson(id);
      const isDone = !!state.progress.completed[id];
      const current = state.route.name === 'lesson' && state.route.id === id;
      html += `<a class="nav-item" href="#/lesson/${id}" ${current ? 'aria-current="page"' : ''}>
        <span class="nav-num">${esc(id.toUpperCase())}</span>
        <span class="nav-title">${esc(l.title)}</span>
        ${isDone ? '<span class="tick" aria-label="completed">✓</span>' : ''}
      </a>`;
    }
  }
  nav.innerHTML = html || '<p class="local-note">No lesson matches that search.</p>';
  const all = orderedLessons();
  $('#sideProgress').textContent = pct(doneCount(all), all.length) + '%';
  $('#sideTitle').textContent = query ? `Search: “${state.search.trim()}”` : 'Course';

  $$('.nav-level', nav).forEach((b) => b.addEventListener('click', () => go(`#/level/${b.dataset.level}`)));
}

/* --------------------------------------------------------------- dashboard */
function nextLesson() {
  const all = orderedLessons();
  const last = state.progress.last;
  if (last && !state.progress.completed[last]) return last;
  return all.find((id) => !state.progress.completed[id]) || last || all[0];
}

function homeHTML() {
  const all = orderedLessons();
  const done = doneCount(all);
  const quizzes = Object.values(state.progress.quiz);
  const right = quizzes.reduce((s, q) => s + (q.right || 0), 0);
  const asked = quizzes.reduce((s, q) => s + (q.total || 0), 0);
  const name = state.user ? Account.prettyName(state.user) : '';

  if (state.search.trim()) return searchHTML();

  const nx = nextLesson();
  const nxl = lesson(nx);
  const started = done > 0 || Object.keys(state.progress.drafts).length > 0;

  return `<div class="wrap">
    <section class="hero">
      <h1>${name
        ? (started ? `Welcome back, ${esc(name)}.` : `Hello, ${esc(name)}.`)
        : (started ? 'Welcome back.' : 'Hello there.')}</h1>
      <p>Learn C++ by predicting what code does, running it, and testing your own version.
         ${state.course.total} short lessons, one at a time.</p>
    </section>

    <div class="continue-card">
      <div class="cc-body">
        <div class="cc-kicker">${started ? 'Continue learning' : 'Start here'}</div>
        <h3>${esc(nxl.title)}</h3>
        <p>${esc(nxl.goal)}</p>
      </div>
      <a class="btn" href="#/lesson/${nx}">${started ? 'Continue' : 'Begin'} →</a>
    </div>

    <div class="stat-row">
      <div class="stat"><b>${done}<span style="font-size:14px;color:var(--muted)"> / ${all.length}</span></b><span>lessons complete</span></div>
      <div class="stat"><b>${asked ? Math.round((right / asked) * 100) + '%' : '—'}</b><span>quiz answers right</span></div>
      <div class="stat"><b>${Object.keys(state.progress.drafts).length}</b><span>saved code drafts</span></div>
    </div>

    <div class="levels">
      ${state.course.levels.map((lv) => {
        const d = doneCount(lv.lessons);
        return `<a class="level-card" href="#/level/${lv.id}">
          <div class="lc-top"><h3>${esc(lv.name)}</h3>
            <span class="tag time">${lv.lessons.length} lessons</span></div>
          <p>${esc(lv.blurb)}</p>
          <div class="bar"><i style="width:${pct(d, lv.lessons.length)}%"></i></div>
          <div class="lc-meta"><span>${d} of ${lv.lessons.length} done</span><span>${pct(d, lv.lessons.length)}%</span></div>
        </a>`;
      }).join('')}
    </div>

    <p class="local-note" style="margin-top:26px">
      ${state.user
        ? `Progress, quiz results and code drafts are saved to <b>${esc(name)}</b>'s account and follow you to any device.`
        : 'Progress is saved in this browser only. <b>Create an account</b> to keep it on any device.'}
    </p>
  </div>`;
}

function searchHTML() {
  const q = state.search.trim().toLowerCase();
  const hits = orderedLessons().map(lesson).filter((l) =>
    (l.title + ' ' + (l.tags || []).join(' ') + ' ' + l.goal + ' ' + l.recap).toLowerCase().includes(q));
  return `<div class="wrap">
    <section class="hero"><h1>${hits.length} lesson${hits.length === 1 ? '' : 's'} matching “${esc(state.search.trim())}”</h1></section>
    ${hits.length ? `<div class="levels">${hits.map((l) => `
      <a class="level-card" href="#/lesson/${l.id}">
        <div class="lc-top"><h3>${esc(l.title)}</h3>
          <span class="tag time">${esc(l.id.toUpperCase())}</span></div>
        <p>${esc(l.goal)}</p>
        <div class="lc-meta"><span>${esc(l.level)}</span><span>${l.minutes} min</span></div>
      </a>`).join('')}</div>`
      : '<p class="local-note">Try “loop”, “vector”, “class” or “file”.</p>'}
  </div>`;
}

function levelHTML(levelId) {
  const lv = state.course.levels.find((x) => x.id === levelId);
  if (!lv) return notFound(levelId);
  const d = doneCount(lv.lessons);
  return `<div class="wrap">
    <div class="crumbs"><a href="#/home">Course</a> › ${esc(lv.name)}</div>
    <section class="hero"><h1>${esc(lv.name)}</h1><p>${esc(lv.blurb)}</p></section>
    <div class="stat-row">
      <div class="stat"><b>${d}/${lv.lessons.length}</b><span>complete</span></div>
      <div class="stat"><b>${lv.lessons.reduce((s, id) => s + lesson(id).minutes, 0)}</b><span>minutes of lessons</span></div>
    </div>
    <div class="levels">
      ${lv.lessons.map((id, i) => {
        const l = lesson(id);
        const done = !!state.progress.completed[id];
        const q = state.progress.quiz[id];
        return `<a class="level-card" href="#/lesson/${id}">
          <div class="lc-top"><h3>${i + 1}. ${esc(l.title)}</h3>
            <span class="tag ${done ? 'done' : 'time'}">${done ? '✓ done' : l.minutes + ' min'}</span></div>
          <p>${esc(l.goal)}</p>
          <div class="lc-meta"><span>${esc(id.toUpperCase())}</span>
            <span>${q ? `quiz ${q.right}/${q.total}` : (l.tags || []).slice(0, 2).join(' · ')}</span></div>
        </a>`;
      }).join('')}
    </div>
  </div>`;
}

function notFound(id) {
  return `<div class="wrap"><h1>Lesson not found</h1>
    <p>The course data has no lesson called “${esc(id)}”.</p>
    <p><a class="btn" href="#/home">Back to the course</a></p></div>`;
}

/* ------------------------------------------------------------------ lesson */
function lessonHTML(l) {
  const isDone = !!state.progress.completed[l.id];
  const draft = state.progress.drafts[l.id];
  const quiz = state.progress.quiz[l.id];
  const ex = l.example;

  return `<div class="wrap lesson">
    <header class="lesson-head">
      <div class="crumbs"><a href="#/home">Course</a> › <a href="#/level/${l.level}">${esc(l.level)}</a> › ${esc(l.id.toUpperCase())}</div>
      <h1>${esc(l.title)}</h1>
      <div class="meta-row">
        <span class="tag time">${l.minutes} min</span>
        ${(l.tags || []).map((t) => `<span class="tag">${esc(t)}</span>`).join('')}
        ${isDone ? '<span class="tag done">✓ completed</span>' : ''}
      </div>
    </header>

    <section class="card">
      <h2><span class="dot"></span>Goal</h2>
      <p class="lead">${esc(l.goal)}</p>
    </section>

    <section class="card">
      <h2><span class="dot"></span>The idea</h2>
      <div class="prose">${l.explain.map((p) => `<p>${esc(p)}</p>`).join('')}</div>
    </section>

    <section class="card">
      <h2><span class="dot"></span>A complete program</h2>
      <div class="code-block">
        <div class="code-bar">
          <span class="fname">${esc(ex.title || 'example.cpp')}</span>
          <span class="acts">
            <button class="mini-btn" type="button" data-copy-example>Copy</button>
          </span>
        </div>
        <pre class="code"><code>${highlight(ex.code)}</code></pre>
      </div>

      <div class="output-block">
        <div class="out-label">What it prints</div>
        <pre class="out">${esc(ex.output) || '<span style="color:var(--muted)">(no output)</span>'}</pre>
      </div>

      ${ex.stdin ? `<div class="output-block">
        <div class="out-label">Input it was given</div>
        <pre class="out">${esc(ex.stdin)}</pre></div>` : ''}

      <ul class="notes">
        ${(ex.notes || []).map(([code, why]) => `<li><code>${esc(code)}</code><span>${esc(why)}</span></li>`).join('')}
      </ul>
    </section>

    <section class="card" data-predict>
      <h2><span class="dot"></span>Predict before you run</h2>
      <p style="font-size:17px">${esc(l.predict.q)}</p>
      <div data-predict-options>
        ${l.predict.options.map((o, i) => `
          <button class="opt" type="button" data-i="${i}">
            <span class="key">${String.fromCharCode(65 + i)}</span><span>${esc(o)}</span>
          </button>`).join('')}
      </div>
      <div data-predict-result hidden></div>
    </section>

    <section class="card" data-quiz>
      <h2><span class="dot"></span>Quiz</h2>
      ${l.quiz.map((q, qi) => `
        <div class="quiz-q" data-q="${qi}">
          <h4><span class="qnum">${qi + 1}.</span>${esc(q.q)}</h4>
          ${q.options.map((o, oi) => `
            <button class="opt" type="button" data-o="${oi}">
              <span class="key">${String.fromCharCode(65 + oi)}</span><span>${esc(o)}</span>
            </button>`).join('')}
          <div class="feedback" hidden></div>
        </div>`).join('')}
      <div class="quiz-foot">
        <button class="btn" type="button" data-check-quiz>Check answers</button>
        <button class="btn ghost" type="button" data-retry-quiz>Try again</button>
        <span class="score-note" data-quiz-score>${quiz ? `Best so far: ${quiz.right}/${quiz.total}` : `${l.quiz.length} questions`}</span>
      </div>
    </section>

    <section class="card" data-activity>
      <h2><span class="dot"></span>Your turn</h2>
      <p style="font-size:17px"><b>Task.</b> ${esc(l.activity.goal)}</p>

      <div class="activity-grid">
        <div class="editor-wrap">
          <div class="editor-bar">
            <span class="fname">main.cpp</span>
            <span class="acts">
              <button class="mini-btn" type="button" data-reset-code>Reset</button>
              <button class="mini-btn" type="button" data-copy-code>Copy</button>
            </span>
          </div>
          <textarea class="code-input" spellcheck="false" autocapitalize="off" autocorrect="off"
            aria-label="Your C++ code" data-editor>${esc(draft || l.activity.starter)}</textarea>
        </div>

        <div class="run-row">
          <button class="btn" type="button" data-run>Run ▶</button>
          <span class="run-status" data-run-status role="status"></span>
        </div>

        <div class="compare" data-compare hidden>
          <div>
            <h5>Expected</h5>
            <pre class="out" data-expected>${esc(l.activity.expected)}</pre>
          </div>
          <div>
            <h5>Your output</h5>
            <pre class="out" data-actual></pre>
          </div>
        </div>
        <div data-verdict hidden></div>
      </div>

      <div style="margin-top:18px">
        <div class="out-label">Hints — one at a time</div>
        ${l.activity.hints.map((h, i) => `
          <details class="hint"><summary>Hint ${i + 1}</summary><div>${esc(h)}</div></details>`).join('')}
      </div>

      <div class="solution-gate">
        <button class="btn ghost small" type="button" data-show-solution>Show the worked solution</button>
        <div class="solution-body" data-solution hidden style="margin-top:14px">
          <div class="code-block">
            <div class="code-bar"><span class="fname">solution.cpp</span>
              <span class="acts"><button class="mini-btn" type="button" data-copy-solution>Copy</button></span></div>
            <pre class="code"><code>${highlight(l.activity.solution)}</code></pre>
          </div>
        </div>
      </div>
    </section>

    <section class="card">
      <h2><span class="dot"></span>Watch out for</h2>
      <div class="mistake"><b>Common mistake.</b> ${esc(l.mistake)}</div>
    </section>

    <div class="recap">
      <span aria-hidden="true">◆</span>
      <div><strong>Recap.</strong> ${esc(l.recap)}</div>
    </div>

    <div class="lesson-foot">
      <button class="btn ${isDone ? 'ghost' : ''}" type="button" data-complete>
        ${isDone ? '✓ Completed — tap to undo' : 'Mark lesson complete'}
      </button>
      <div class="pager">${pagerHTML(l.id)}</div>
    </div>
  </div>`;
}

function pagerHTML(id) {
  const all = orderedLessons();
  const i = all.indexOf(id);
  const prev = i > 0 ? all[i - 1] : null;
  const next = i >= 0 && i < all.length - 1 ? all[i + 1] : null;
  return `${prev ? `<a class="btn ghost" href="#/lesson/${prev}">← Previous</a>` : ''}
          ${next ? `<a class="btn" href="#/lesson/${next}">Next →</a>` : ''}`;
}

/* --------------------------------------------------------------- behaviour */
/* Remote compile path: used when the page is hosted and /api/run is missing. */
async function runRemotely(code, stdin) {
  try {
    const res = await fetch('https://wandbox.org/api/compile.json', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        compiler: 'gcc-13.2.0',
        code,
        stdin: stdin || '',
        'compiler-option-raw': '-std=c++20\n-O1\n-Wall',
      }),
    });
    const data = await res.json();
    const compileErr = (data.compiler_error || '').trim();
    const ok = String(data.status) === '0' && !compileErr;
    return {
      ok,
      phase: compileErr ? 'compile' : 'run',
      stdout: data.program_output || '',
      stderr: compileErr || (data.program_error || ''),
      run_ms: 0,
      message: compileErr ? 'The compiler found a problem. Read the first message above.' : '',
    };
  } catch {
    return { ok: false, phase: 'error', stdout: '', stderr: '',
             message: 'The online compiler could not be reached.' };
  }
}

function bindLesson(l) {
  const root = $('#main');
  const prog = state.progress;

  // ---- copy example
  const copyEx = $('[data-copy-example]', root);
  copyEx?.addEventListener('click', async () => {
    toast((await copyText(l.example.code)) ? 'Example copied' : 'Copy failed — select the text instead');
  });

  // ---- predict
  const predict = $('[data-predict]', root);
  if (predict) {
    const result = $('[data-predict-result]', predict);
    $$('.opt', predict).forEach((btn) => btn.addEventListener('click', () => {
      const picked = Number(btn.dataset.i);
      const right = picked === l.predict.answer;
      $$('.opt', predict).forEach((b) => {
        b.disabled = true;
        const i = Number(b.dataset.i);
        if (i === l.predict.answer) b.classList.add('right');
        else if (i === picked) b.classList.add('wrong');
      });
      result.hidden = false;
      result.className = 'feedback ' + (right ? 'good' : 'bad');
      result.innerHTML = `<b>${right ? 'Yes.' : 'Not quite.'}</b> ${esc(l.predict.why)}`;
    }));
  }

  // ---- quiz
  const quiz = $('[data-quiz]', root);
  if (quiz) {
    const picked = new Map();
    $$('.quiz-q', quiz).forEach((qEl, qi) => {
      $$('.opt', qEl).forEach((btn) => btn.addEventListener('click', () => {
        if (qEl.dataset.locked === '1') return;
        picked.set(qi, Number(btn.dataset.o));
        $$('.opt', qEl).forEach((b) => b.setAttribute('aria-pressed', String(Number(b.dataset.o) === Number(btn.dataset.o))));
        $$('.opt', qEl).forEach((b) => {
          if (Number(b.dataset.o) === Number(btn.dataset.o)) b.classList.add('right');
          else b.classList.remove('right');
        });
      }));
    });

    $('[data-check-quiz]', quiz).addEventListener('click', () => {
      let right = 0;
      $$('.quiz-q', quiz).forEach((qEl, qi) => {
        const q = l.quiz[qi];
        const fb = $('.feedback', qEl);
        const got = picked.get(qi);
        if (got === undefined) {
          fb.hidden = false;
          fb.className = 'feedback';
          fb.innerHTML = 'Pick an answer first.';
          return;
        }
        qEl.dataset.locked = '1';
        const ok = got === q.answer;
        if (ok) right++;
        $$('.opt', qEl).forEach((b) => {
          b.disabled = true;
          const i = Number(b.dataset.o);
          b.classList.remove('right');
          if (i === q.answer) b.classList.add('right');
          else if (i === got) b.classList.add('wrong');
        });
        fb.hidden = false;
        fb.className = 'feedback ' + (ok ? 'good' : 'bad');
        fb.innerHTML = `<b>${ok ? 'Correct.' : `Not quite — ${String.fromCharCode(65 + q.answer)} is right.`}</b> ${esc(q.why)}`;
      });
      const total = l.quiz.length;
      $('[data-quiz-score]', quiz).textContent = `This try: ${right}/${total}`;
      const best = prog.quiz[l.id];
      if (!best || right > best.right) prog.quiz[l.id] = { right, total, at: Date.now() };
      saveProfile();
      renderNav();
    });

    $('[data-retry-quiz]', quiz).addEventListener('click', () => {
      picked.clear();
      $$('.quiz-q', quiz).forEach((qEl) => {
        delete qEl.dataset.locked;
        $$('.opt', qEl).forEach((b) => {
          b.disabled = false;
          b.classList.remove('right', 'wrong');
          b.removeAttribute('aria-pressed');
        });
        const fb = $('.feedback', qEl);
        fb.hidden = true;
        fb.textContent = '';
      });
      $('[data-quiz-score]', quiz).textContent = 'Try again — no peeking.';
    });
  }

  // ---- activity
  const act = $('[data-activity]', root);
  const editor = $('[data-editor]', act);
  const status = $('[data-run-status]', act);
  const compare = $('[data-compare]', act);
  const verdict = $('[data-verdict]', act);

  let saveTimer = null;
  editor.addEventListener('input', () => {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      prog.drafts[l.id] = editor.value;
      saveProfile();
    }, 600);
  });

  editor.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const s = editor.selectionStart, en = editor.selectionEnd;
      editor.value = editor.value.slice(0, s) + '    ' + editor.value.slice(en);
      editor.selectionStart = editor.selectionEnd = s + 4;
    }
  });

  $('[data-reset-code]', act).addEventListener('click', () => {
    editor.value = l.activity.starter;
    prog.drafts[l.id] = l.activity.starter;
    saveProfile();
    status.textContent = 'Reset to the starter code.';
    compare.hidden = true;
    verdict.hidden = true;
  });

  $('[data-copy-code]', act).addEventListener('click', async () => {
    toast((await copyText(editor.value)) ? 'Your code copied' : 'Copy failed');
  });

  $('[data-copy-solution]', act).addEventListener('click', async () => {
    toast((await copyText(l.activity.solution)) ? 'Solution copied' : 'Copy failed');
  });

  $('[data-show-solution]', act).addEventListener('click', (e) => {
    const body = $('[data-solution]', act);
    body.hidden = !body.hidden;
    e.currentTarget.textContent = body.hidden ? 'Show the worked solution' : 'Hide the solution';
  });

  const runBtn = $('[data-run]', act);
  runBtn.addEventListener('click', async () => {
    if (state.health && state.health.compiler === null) {
      verdict.hidden = false;
      verdict.className = 'verdict neutral';
      verdict.innerHTML = 'No C++ compiler is available on this machine, so nothing was run. ' +
        'Ask an adult to start the server with the bundled toolchain, or copy your code into an online compiler.';
      return;
    }
    runBtn.disabled = true;
    status.textContent = 'Compiling…';
    compare.hidden = true;
    verdict.hidden = true;
    try {
      let out;
      try {
        const res = await fetch('/api/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: editor.value, stdin: l.activity.stdin || '' }),
        });
        if (!res.ok) throw new Error('no local runner');
        out = await res.json();
      } catch {
        // hosted without the API function: compile on the online service instead
        out = await runRemotely(editor.value, l.activity.stdin || '');
      }
      const expect = normalise(l.activity.expected);
      const actual = normalise(out.stdout || '');

      compare.hidden = false;
      $('[data-actual]', act).textContent = out.stdout || (out.stderr ? out.stderr : '(no output)');

      if (out.phase === 'compile') {
        status.textContent = `Compile error (${out.compile_ms} ms)`;
        verdict.hidden = false;
        verdict.className = 'verdict fail';
        verdict.innerHTML = 'The compiler stopped on an error, so the program never ran. Read the first message above.';
      } else if (!out.ok) {
        status.textContent = out.message || 'The program did not finish cleanly.';
        verdict.hidden = false;
        verdict.className = 'verdict fail';
        verdict.innerHTML = esc(out.message || 'The program exited with an error.');
      } else {
        const pass = actual === expect;
        status.textContent = `Ran in ${out.run_ms} ms` +
          (out.warnings ? ' · compiler warnings above' : '');
        verdict.hidden = false;
        verdict.className = 'verdict ' + (pass ? 'pass' : 'fail');
        verdict.innerHTML = pass
          ? '✓ Output matches the expected result exactly.'
          : 'Output does not match yet — compare the two panels line by line.';
        if (pass && !prog.completed[l.id]) {
          prog.completed[l.id] = true;
          saveProfile();
          renderNav();
          $('[data-complete]', root).className = 'btn ghost';
          $('[data-complete]', root).textContent = '✓ Completed — tap to undo';
          toast('Activity passed — lesson marked complete.');
        }
      }
    } catch (err) {
      status.textContent = 'Could not reach the runner.';
      verdict.hidden = false;
      verdict.className = 'verdict fail';
      verdict.innerHTML = 'The server did not answer. Is <code>python server.py</code> still running?';
    } finally {
      runBtn.disabled = false;
    }
  });

  // ---- completion
  $('[data-complete]', root).addEventListener('click', (e) => {
    if (prog.completed[l.id]) {
      delete prog.completed[l.id];
      e.currentTarget.className = 'btn';
      e.currentTarget.textContent = 'Mark lesson complete';
    } else {
      prog.completed[l.id] = true;
      e.currentTarget.className = 'btn ghost';
      e.currentTarget.textContent = '✓ Completed — tap to undo';
    }
    saveProfile();
    renderNav();
  });

  prog.last = l.id;
  prog.visits = (prog.visits || 0) + 1;
  saveProfile();
}

/* -------------------------------------------------------------------- boot */
function bindChrome() {
  $('#search').addEventListener('input', (e) => {
    state.search = e.target.value;
    renderNav();
    if (state.route.name === 'home' || state.search.trim()) {
      $('#main').innerHTML = state.search.trim() ? searchHTML() : homeHTML();
    }
  });

  $('#search').addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { e.target.value = ''; state.search = ''; renderNav(); }
    if (e.key === 'Enter') {
      const first = orderedLessons().map(lesson).find((l) =>
        (l.title + ' ' + (l.tags || []).join(' ')).toLowerCase().includes(state.search.trim().toLowerCase()));
      if (first) go(`#/lesson/${first.id}`);
    }
  });

  // account buttons are bound by renderAccount(), which rebuilds them on every change

  const navToggle = $('#navToggle');
  const sidebar = $('#sidebar');
  const scrim = $('#scrim');
  const closeNav = () => {
    sidebar.classList.remove('open');
    scrim.hidden = true;
    navToggle.setAttribute('aria-expanded', 'false');
  };
  navToggle.addEventListener('click', () => {
    const open = !sidebar.classList.contains('open');
    sidebar.classList.toggle('open', open);
    scrim.hidden = !open;
    navToggle.setAttribute('aria-expanded', String(open));
  });
  scrim.addEventListener('click', closeNav);
  window.addEventListener('hashchange', () => { closeNav(); render(); });

  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement.tagName !== 'TEXTAREA' && document.activeElement.tagName !== 'INPUT') {
      e.preventDefault();
      $('#search').focus();
    }
  });
}

async function boot() {
  bindChrome();
  state.profile = GUEST;
  state.progress = blank();
  renderAccount();

  // Accounts are optional: if Firebase cannot start, the course still runs as a guest.
  state.authReady = await Account.initFirebase();
  if (state.authReady) {
    Account.onChange(async (user) => {
      try {
        if (user) await adoptAccount(user);
        else releaseAccount();
      } catch (err) {
        toast('Could not load your saved progress. Keep working — it is stored here too.');
        console.warn(err);
      }
    });
  }

  try {
    await loadCourse();
    render();
  } catch (err) {
    $('#main').innerHTML = `<div class="wrap"><h1>The course data did not load</h1>
      <p>${esc(err.message)}</p>
      <p>Start the app with <code>python server.py</code> and open the address it prints.</p></div>`;
  }
}

boot();
