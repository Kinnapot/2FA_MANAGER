// Use same-origin; nginx will proxy /api -> backend
const API = '';
let ACCOUNTS = [];
let SELECTED = null;
let LAST_OTP = '';

async function api(path, opts={}) {
  const res = await fetch(API + path, {headers: {'Content-Type':'application/json'}, ...opts});
  if (!res.ok) throw new Error(await res.text());
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}

async function refresh() {
  ACCOUNTS = await api('/api/accounts');
  render();
}

function render() {
  const tbody = document.getElementById('tbody');
  tbody.innerHTML = '';
  for (const a of ACCOUNTS) {
    const tr = document.createElement('tr');
    const tdSel = document.createElement('td');
    const r = document.createElement('input'); r.type='radio'; r.name='sel'; r.value=a.id; r.checked = a.id===SELECTED; r.addEventListener('change',()=>SELECTED=a.id); tdSel.appendChild(r);
    const tdUser = document.createElement('td'); tdUser.textContent = a.username;
    const tdPwd = document.createElement('td'); tdPwd.textContent = a.has_password ? '••••••' : '-'; tdPwd.className='masked';
    const tdSec = document.createElement('td'); tdSec.textContent = '••••••'; tdSec.className='masked';
    const tdNote = document.createElement('td'); tdNote.textContent = a.note || '-';
    const tdAct = document.createElement('td');
    const edit = document.createElement('button'); edit.textContent='Edit'; edit.addEventListener('click',()=>editRow(a));
    const del = document.createElement('button'); del.textContent='Delete'; del.className='danger'; del.addEventListener('click',()=>delRow(a.id));
    tdAct.appendChild(edit); tdAct.appendChild(del);
    [tdSel, tdUser, tdPwd, tdSec, tdNote, tdAct].forEach(td=>tr.appendChild(td));
    tbody.appendChild(tr);
  }
}

async function delRow(id){
  if(!confirm('ลบบัญชีนี้?')) return;
  await api(`/api/accounts/${id}`, {method:'DELETE'});
  if(SELECTED===id) SELECTED=null;
  await refresh();
}

function editRow(a){
  const username = prompt('Username', a.username); if(username===null) return;
  const note = prompt('Note', a.note||''); if(note===null) return;
  const digits = parseInt(prompt('Digits (6-8)', String(a.digits))||a.digits,10);
  const period = parseInt(prompt('Period (15-60)', String(a.period))||a.period,10);
  const secret = prompt('Secret (ว่าง=ไม่เปลี่ยน)','');
  const password = prompt('Password (ว่าง=ไม่เปลี่ยน)','');
  const payload = {username, note, digits, period};
  if(secret && secret.trim()) payload.secret_key = secret;
  if(password && password.trim()) payload.password = password;
  api(`/api/accounts/${a.id}`, {method:'PUT', body: JSON.stringify(payload)}).then(refresh);
}

async function addAccount(){
  const username = document.getElementById('in-username').value.trim();
  const password = document.getElementById('in-password').value.trim();
  const secret = document.getElementById('in-secret').value.trim();
  const note = document.getElementById('in-note').value.trim();
  const digits = parseInt(document.getElementById('in-digits').value||'6',10);
  const period = parseInt(document.getElementById('in-period').value||'30',10);
  if(!username || !secret){ alert('ต้องกรอก username และ secret'); return; }
  await api('/api/accounts', {method:'POST', body: JSON.stringify({username, password, secret_key: secret, note, digits, period})});
  ['in-username','in-password','in-secret','in-note'].forEach(id=>document.getElementById(id).value='');
  await refresh();
}

async function getOtp(){
  if(!SELECTED){ alert('กรุณาเลือกรายการ'); return; }
  const data = await api(`/api/accounts/${SELECTED}/otp`);
  LAST_OTP = data.otp || '';
  document.getElementById('otp-output').textContent = LAST_OTP ? `genotp : ${LAST_OTP}` : 'ยังไม่ได้ genotp';
}

async function copyOtp(){ if(!LAST_OTP){ alert('ยังไม่ได้ genotp'); return; } await navigator.clipboard.writeText(LAST_OTP); }
async function copyUser(){ if(!SELECTED){ alert('เลือกรายการ'); return; } const a = ACCOUNTS.find(x=>x.id===SELECTED); if(a) await navigator.clipboard.writeText(a.username); }
async function copyPassword(){ if(!SELECTED){ alert('เลือกรายการ'); return; } try{ const d=await api(`/api/accounts/${SELECTED}/password`); await navigator.clipboard.writeText(d.password||''); }catch(e){ alert('ไม่มี password'); } }
async function copySecret(){ if(!SELECTED){ alert('เลือกรายการ'); return; } try{ const d=await api(`/api/accounts/${SELECTED}/secret`); await navigator.clipboard.writeText(d.secret_key||''); }catch(e){ alert('คัดลอกไม่ได้'); } }

window.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('btn-confirm').addEventListener('click', addAccount);
  document.getElementById('btn-get-otp').addEventListener('click', getOtp);
  document.getElementById('btn-copy-otp').addEventListener('click', copyOtp);
  document.getElementById('btn-copy-user').addEventListener('click', copyUser);
  document.getElementById('btn-copy-password').addEventListener('click', copyPassword);
  document.getElementById('btn-copy-secret').addEventListener('click', copySecret);
  refresh();
});
