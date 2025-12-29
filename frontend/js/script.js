const API_URL = "/api";

async function init() {
  try {
    const res = await fetch(`${API_URL}/categories`);
    const categories = await res.json();
    const select = document.getElementById("categorySelect");
    select.innerHTML = '<option value="">-- Оберіть категорію --</option>';
    categories.forEach((cat) => {
      const opt = document.createElement("option");
      opt.value = cat.url;
      opt.text = cat.name;
      select.appendChild(opt);
    });
    select.addEventListener("change", (e) => {
      document.getElementById("customUrl").value = e.target.value;
    });
  } catch (e) {
    console.error("API Error:", e);
  }
}

async function startParsing() {
  const url = document.getElementById("customUrl").value;
  const btn = document.getElementById("parseBtn");

  if (!url) return alert("Оберіть категорію!");

  btn.disabled = true;
  btn.innerText = "⏳ Браузер збирає дані (це займе ~20 сек)...";
  document.getElementById("results").innerHTML =
    '<div class="text-center w-100 py-5"><div class="spinner-border text-primary"></div><p class="mt-2">Зачекайте, Selenium обходить захист...</p></div>';

  try {
    const res = await fetch(`${API_URL}/parse?url=${encodeURIComponent(url)}`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Помилка парсинга");
    await loadProducts();
  } catch (e) {
    alert("Помилка: " + e.message);
  } finally {
    btn.disabled = false;
    btn.innerText = "Start Parsing (Selenium)";
  }
}

async function loadProducts() {
  const sort = document.getElementById("sortBy").value;
  const rating = document.getElementById("minRating").value || 0;
  const container = document.getElementById("results");

  const res = await fetch(
    `${API_URL}/products?sort_by=${sort}&min_rating=${rating}`
  );
  const products = await res.json();

  container.innerHTML = "";
  if (products.length === 0) {
    container.innerHTML =
      '<div class="w-100 text-center text-muted">Немає даних. Запустіть парсинг.</div>';
    return;
  }

  products.forEach((p) => {
    let bulletsHtml = "";
    if (p.bullet_points && p.bullet_points.length > 0) {
      bulletsHtml = '<ul class="bullet-list">';
      p.bullet_points.slice(0, 3).forEach((txt) => {
        bulletsHtml += `<li>${txt.substring(0, 80)}${
          txt.length > 80 ? "..." : ""
        }</li>`;
      });
      bulletsHtml += "</ul>";
    }

    let priceBlock = `<h5 class="text-dark mb-0">${p.price}</h5>`;
    if (p.list_price) {
      priceBlock = `
                    <div class="d-flex align-items-baseline gap-2">
                        <h5 class="text-danger mb-0">${p.price}</h5>
                        <small class="text-decoration-line-through text-muted" style="font-size:0.8em">${p.list_price}</small>
                    </div>
                `;
    }

    let primeBadge = p.is_prime ? '<span class="prime-badge">✔ prime</span>' : "";

    const html = `<div class="col">
                    <div class="card h-100">
                        <span class="badge bg-danger rank-badge">#${p.rank}</span>
                        <div class="bg-white p-3 text-center">
                            <img src="${p.main_image_url}" class="card-img-top product-img" alt="${p.title}">
                        </div>
                        <div class="card-body d-flex flex-column p-3">
                            <h6 class="card-title text-truncate mb-1" title="${p.title}">${p.title}</h6>
                            
                            <div class="mb-2 small">
                                <span class="text-warning">★ ${p.rating}</span> 
                                <span class="text-muted">(${p.reviews_count})</span>
                            </div>

                            <div class="mb-3 flex-grow-1">
                                ${bulletsHtml}
                            </div>

                            <div class="mt-auto border-top pt-2">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    ${priceBlock}
                                    ${primeBadge}
                                </div>
                                <a href="${p.product_url}" target="_blank" class="btn btn-sm btn-dark w-100">Дивитись на Amazon</a>
                            </div>
                        </div>
                    </div>
                </div>`;
    container.insertAdjacentHTML("beforeend", html);
  });
}

init();