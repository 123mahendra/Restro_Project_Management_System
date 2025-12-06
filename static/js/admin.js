
// async function apiGET(path){ const r = await fetch(path); return r.ok ? r.json() : Promise.reject(await r.text()); }
// async function apiPOST(path, body){ const r = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)}); return r.ok ? r.json() : Promise.reject(await r.text()); }
// async function apiPUT(path, body){ const r = await fetch(path, {method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)}); return r.ok ? r.json() : Promise.reject(await r.text()); }
// async function apiDELETE(path){ const r = await fetch(path, {method:'DELETE'}); return r.ok ? r.json() : Promise.reject(await r.text()); }

// // ========== Announcements ==========
// async function loadAnnouncementsAdmin(){
//   const listEl = document.getElementById('ann-list') || document.getElementById('ann-editor-list');
//   if(!listEl) return;
//   listEl.innerHTML = 'Loading...';
//   try{
//     const anns = await apiGET('/api/announcements');
//     listEl.innerHTML = '';
//     anns.forEach(a => {
//       const div = document.createElement('div');
//       div.className = 'announcement-row';
//       div.innerHTML = `<strong>${a.title}</strong> — ${a.message || a.content || ''}
//         <button class="btn small" data-id="${a._id}" data-act="delete">Delete</button>`;
//       listEl.appendChild(div);
//     });
//     document.querySelectorAll('[data-act="delete"]').forEach(b=>{
//       b.onclick = async ()=> {
//         if(!confirm('Delete announcement?')) return;
//         const id = b.dataset.id;
//         await apiDELETE('/api/announcements/'+id);
//         loadAnnouncementsAdmin();
//       };
//     });
//   }catch(e){ listEl.innerHTML = 'Failed to load.'; console.error(e);}
// }

// document.addEventListener('DOMContentLoaded', ()=>{
//   // announcements add
//   const annAddBtn = document.getElementById('ann-add');
//   if(annAddBtn){
//     annAddBtn.onclick = async ()=>{
//       const form = document.getElementById('ann-form');
//       const fd = new FormData(form);
//       const body = { title: fd.get('title'), content: fd.get('content') };
//       try{ await apiPOST('/api/announcements', body); form.reset(); loadAnnouncementsAdmin(); } catch(e){ alert('Failed: ' + e); }
//     };
//   }
//   loadAnnouncementsAdmin();

//   // menu list load
//   loadMenuAdmin();

//   // orders
//   loadOrdersAdmin();
// });

// // ========== Menu admin ==========
// async function loadMenuAdmin(){
//   const el = document.getElementById('menu-list');
//   if(!el) return;
//   el.innerHTML = 'Loading...';
//   try{
//     const items = await apiGET('/api/menu');
//     el.innerHTML = '';
//     items.forEach(it => {
//       const itemDiv = document.createElement('div');
//       itemDiv.className = 'menu-row';
//       itemDiv.innerHTML = `<div class="menu-left">
//           <strong>${(it.name_en||it.name)}</strong> <span class="muted">€${Number(it.price).toFixed(2)}</span>
//           <div class="muted small">${(it.category||'')} • Days: ${(it.active_days||[]).join(',')}</div>
//         </div>
//         <div class="menu-actions">
//           <a class="btn small" href="/admin/menu/edit/${it._id}">Edit</a>
//           <button class="btn small danger" data-id="${it._id}" data-act="del">Delete</button>
//         </div>`;
//       el.appendChild(itemDiv);
//     });

//     el.querySelectorAll('[data-act="del"]').forEach(btn=>{
//       btn.onclick = async ()=>{
//         if(!confirm('Delete menu item?')) return;
//         try{
//           await apiDELETE('/api/menu/'+btn.dataset.id);
//           loadMenuAdmin();
//         }catch(e){ alert('Failed: '+e); }
//       };
//     });
//   }catch(e){ el.innerHTML = 'Failed to load menu.'; console.error(e); }
// }

// // ========== Orders admin ==========
// async function loadOrdersAdmin(){
//   const el = document.getElementById('order-list') || document.getElementById('orders-admin-list');
//   if(!el) return;
//   el.innerHTML = 'Loading...';
//   try{
//     const orders = await apiGET('/api/orders');
//     el.innerHTML = '';
//     orders.forEach(o=>{
//       const card = document.createElement('div');
//       card.className = 'order-row';
//       const itemsHTML = (o.items||[]).map(it => `<li>${it.name} x${it.qty} — €${Number(it.price).toFixed(2)}</li>`).join('');
//       card.innerHTML = `<div><strong>Order ${o._id}</strong> • ${o.created_at || ''} • €${Number(o.total||0).toFixed(2)}</div>
//         <div><ul>${itemsHTML}</ul></div>
//         <div class="order-actions">
//           <select data-id="${o._id}" class="order-status">
//             <option ${o.status==='pending'?'selected':''} value="pending">Pending</option>
//             <option ${o.status==='preparing'?'selected':''} value="preparing">Preparing</option>
//             <option ${o.status==='completed'?'selected':''} value="completed">Completed</option>
//             <option ${o.status==='cancelled'?'selected':''} value="cancelled">Cancelled</option>
//           </select>
//           <button class="btn small" data-act="update" data-id="${o._id}">Update</button>
//         </div>`;
//       el.appendChild(card);
//     });

//     el.querySelectorAll('[data-act="update"]').forEach(b=>{
//       b.onclick = async ()=>{
//         const id = b.dataset.id;
//         const sel = b.parentElement.querySelector('.order-status');
//         const status = sel.value;
//         try{
//           await apiPOST('/api/orders/'+id+'/status', { status });
//           loadOrdersAdmin();
//         }catch(e){ alert('Failed to update status: ' + e); }
//       };
//     });
//   }catch(e){ el.innerHTML = 'Failed to load orders.'; console.error(e); }
// }



// Sidebar toggle for mobile
const closeBtn = document.getElementById("close-sidebar");
closeBtn.addEventListener("click", () => {
    sidebar.classList.remove("mobile-active");
});


// Sidebar toggle for mobile
const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("menu-toggle");
toggleBtn.addEventListener("click", () => {
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle("mobile-active");
    } else {
        // DESKTOP VIEW — collapse/expand sidebar
        sidebar.classList.toggle("collapsed");
    }
});


// Page switching
const links = document.querySelectorAll(".sidebar a");
const pages = document.querySelectorAll(".section-page");


// Open sidebar when clicking dashboard icon on mobile
const dashboardIcon = document.querySelector("[data-section='dashboard'] .material-icons");
dashboardIcon.addEventListener("click", (e) => {
    if (window.innerWidth <= 768) {
        e.stopPropagation();
        sidebar.classList.add("mobile-active");
    }
});


links.forEach(link => {
    link.addEventListener("click", () => {
        links.forEach(l => l.classList.remove("active"));
        link.classList.add("active");


        const section = link.dataset.section;
        document.getElementById("section-title").innerText = section.charAt(0).toUpperCase() + section.slice(1);


        pages.forEach(page => page.classList.remove("active"));
        document.getElementById(section).classList.add("active");
    });
});