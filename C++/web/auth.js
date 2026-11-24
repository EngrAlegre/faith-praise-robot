/* Account layer for C++ Lab.
   Firebase Auth (email/password) + Firestore for progress that follows a learner
   between devices. Loaded as a module; the SDK itself is vendored in vendor/ as
   compat scripts, so nothing here depends on a CDN at run time. */

import { firebaseConfig } from './firebase-config.js';

let app = null;
let auth = null;
let db = null;

export const USER_DOMAIN = 'cpplab.local';

/* --------------------------------------------------------------- helpers */
function whenSdkLoaded(timeoutMs = 5000) {
  return new Promise((resolve) => {
    const started = Date.now();
    const tick = () => {
      if (window.firebase && typeof window.firebase.initializeApp === 'function') return resolve(true);
      if (Date.now() - started > timeoutMs) return resolve(false);
      setTimeout(tick, 60);
    };
    tick();
  });
}

export function usernameToEmail(raw) {
  const value = String(raw || '').trim();
  if (value.includes('@')) return value.toLowerCase();
  return value.toLowerCase().replace(/[^a-z0-9._-]/g, '') + '@' + USER_DOMAIN;
}

export function prettyName(user) {
  if (!user) return '';
  if (user.displayName) return user.displayName;
  const email = user.email || '';
  const local = email.split('@')[0];
  return local.charAt(0).toUpperCase() + local.slice(1);
}

export function friendlyError(err) {
  const code = err && err.code ? err.code : '';
  switch (code) {
    case 'auth/email-already-in-use':
      return 'That name is already taken. Try “Sign in” instead, or pick another name.';
    case 'auth/invalid-email':
      return 'That does not look like a name or an email address.';
    case 'auth/weak-password':
      return 'Passwords need at least 6 characters.';
    case 'auth/missing-password':
      return 'Type a password.';
    case 'auth/wrong-password':
    case 'auth/invalid-credential':
    case 'auth/invalid-login-credentials':
      return 'Wrong password for that name. Try again.';
    case 'auth/user-not-found':
      return 'No account with that name yet. Use “Create account”.';
    case 'auth/too-many-requests':
      return 'Too many tries. Wait a minute, then try again.';
    case 'auth/network-request-failed':
      return 'No internet connection. You can keep working — progress is saved on this device.';
    case 'auth/configuration-not-found':
    case 'auth/operation-not-allowed':
      return 'Sign-in is not switched on for this Firebase project yet. An adult needs to open the Firebase console, go to Authentication, and enable Email/Password (it is free).';
    case 'auth/admin-restricted-operation':
      return 'Sign-ups are turned off for this project. An adult needs to enable them in the Firebase console.';
    case 'permission-denied':
      return 'Signed in, but the database refused the request. Check the Firestore rules.';
    default:
      return (err && err.message) ? err.message : 'Something went wrong. Try again.';
  }
}

/* ------------------------------------------------------------------ init */
export async function initFirebase() {
  if (app) return true;
  if (!(await whenSdkLoaded())) return false;
  try {
    const cfg = firebaseConfig;
    app = window.firebase.apps.length ? window.firebase.app() : window.firebase.initializeApp(cfg);
    auth = window.firebase.auth();
    db = window.firebase.firestore();
    // survive offline: Firestore queues writes and replays them
    try { await db.enablePersistence({ synchronizeTabs: true }); } catch { /* fine */ }
    return true;
  } catch (err) {
    console.warn('Firebase did not start:', err);
    return false;
  }
}

export function onChange(callback) {
  if (!auth) return () => {};
  return auth.onAuthStateChanged(callback);
}

export function currentUser() {
  return auth ? auth.currentUser : null;
}

/* ------------------------------------------------------------- accounts */
export async function signUp({ name, email, password }) {
  const cred = await auth.createUserWithEmailAndPassword(usernameToEmail(email), password);
  const display = (name || '').trim() || prettyName(cred.user);
  try {
    await cred.user.updateProfile({ displayName: display });
  } catch { /* not fatal */ }
  // Seed the document, but never make the learner wait for the network.
  pushProgress(cred.user.uid, {
    name: display,
    progress: { completed: {}, quiz: {}, drafts: {}, last: null },
  }).catch(() => {});
  return cred.user;
}

export async function signIn({ email, password }) {
  const cred = await auth.signInWithEmailAndPassword(usernameToEmail(email), password);
  return cred.user;
}

export async function signOutNow() {
  if (auth) await auth.signOut();
}

/* ------------------------------------------------------------- progress */
const SYNC_TIMEOUT = 8000;

function withTimeout(promise, label) {
  return Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error(label)), SYNC_TIMEOUT)),
  ]);
}

export async function pullProgress(uid) {
  if (!db) return null;
  const snap = await withTimeout(db.collection('users').doc(uid).get(), 'cloud read timed out');
  return snap.exists ? snap.data() : null;
}

export async function pushProgress(uid, data) {
  if (!db) return;
  await withTimeout(db.collection('users').doc(uid).set({
    ...data,
    updatedAt: window.firebase.firestore.FieldValue.serverTimestamp(),
  }, { merge: true }), 'cloud write timed out');
}
