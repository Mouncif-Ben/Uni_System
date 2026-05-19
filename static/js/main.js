let allProfs = [],
  allSalles = [],
  salleTypeFilter = "",
  laboVal = 0;
let lastGeneratedData = [],
  lastFiliereName = "";

const jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"];
const heures = [
  { id: "08:30", label: "08:30 - 10:00" },
  { id: "10:15", label: "10:15 - 11:45" },
  { id: "12:00", label: "12:00 - 13:30" },
  { id: "14:30", label: "14:30 - 16:00" },
  { id: "16:15", label: "16:15 - 17:45" },
];

function showPage(page) {
  document
    .querySelectorAll(".page")
    .forEach((p) => p.classList.remove("active"));
  document
    .querySelectorAll(".nav-item")
    .forEach((n) => n.classList.remove("active"));
  document.getElementById("page-" + page).classList.add("active");
  document.getElementById("nav-" + page).classList.add("active");
  if (page === "profs") loadProfs();
  if (page === "salles") loadSalles();
  if (page === "filieres") loadFilieres();
}

async function loadFilieresBySemestre() {
  const semestre = document.getElementById("semestre").value;
  const selectFiliere = document.getElementById("filiere");
  const btnGenerer = document.getElementById("btn-generer");

  selectFiliere.innerHTML = `<option value="">-- Filière --</option>`;
  selectFiliere.disabled = true;
  btnGenerer.disabled = true;
  document.getElementById("num2").classList.remove("done");
  document.getElementById("num3").classList.remove("done");
  document.getElementById("btn-download").style.display = "none";

  if (!semestre) {
    document.getElementById("num1").classList.remove("done");
    return;
  }

  document.getElementById("num1").classList.add("done");

  try {
    const res = await fetch("/api/filieres/list");
    const all = await res.json();

    const filtered = all.filter((f) => {
      const nom = f.nom.toUpperCase().trim();
      const sem = semestre.toUpperCase().trim();
      return (
        nom.startsWith(sem + " ") || nom.startsWith(sem + "_") || nom === sem
      );
    });

    if (!filtered.length) {
      selectFiliere.innerHTML = `<option value="">Aucune filière pour ${semestre}</option>`;
      return;
    }

    filtered.forEach((f) => {
      const opt = document.createElement("option");
      opt.value = f.id;
      opt.textContent = f.nom;
      selectFiliere.appendChild(opt);
    });

    selectFiliere.disabled = false;
  } catch (err) {
    console.error("Erreur loadFilieres:", err);
  }
}

function onFiliereChange() {
  const val = document.getElementById("filiere").value;
  document.getElementById("btn-generer").disabled = !val;
  document.getElementById("num2").classList.toggle("done", !!val);
  document.getElementById("num3").classList.remove("done");
}

function buildGrid() {
  document.getElementById("timetable-body").innerHTML = heures
    .map(
      (h) => `
    <tr>
      <td class="time-col">${h.label}</td>
      ${jours
        .map((j) => {
          const dis = j === "Samedi" && (h.id === "14:30" || h.id === "16:15");
          return `<td class="${dis ? "disabled" : ""}" id="${j} ${h.id}"></td>`;
        })
        .join("")}
    </tr>
  `,
    )
    .join("");
}

async function generate() {
  const fid = document.getElementById("filiere").value;
  const sel = document.getElementById("filiere");
  lastFiliereName = sel.options[sel.selectedIndex].text;

  document.getElementById("empty-state").style.display = "none";
  document.getElementById("timetable-container").style.display = "none";
  document.getElementById("stats-bar").style.display = "none";
  document.getElementById("loading-state").style.display = "block";
  document.getElementById("btn-download").style.display = "none";

  buildGrid();

  try {
    const res = await fetch(`/generate?filiere_id=${fid}`);
    const data = await res.json();

    document.getElementById("loading-state").style.display = "none";

    if (!data.length) {
      document.getElementById("empty-state").style.display = "block";
      return;
    }

    lastGeneratedData = data;
    const profsSet = new Set(),
      sallesSet = new Set();

    data.forEach((e) => {
      const cell = document.getElementById(e.creneau);
      if (!cell || cell.classList.contains("disabled")) return;

      profsSet.add(e.prof);
      sallesSet.add(e.salle);

      const cls =
        e.type === "TD"
          ? "course-td"
          : e.type === "TP"
            ? "course-tp"
            : "course-cm";
      const badgeCls =
        e.type === "CM"
          ? "badge-cm"
          : e.type === "TD"
            ? "badge-td"
            : "badge-tp";
      const salleTxt =
        e.salle.toLowerCase().includes("amphi") ||
        e.salle.toLowerCase().includes("labo")
          ? e.salle
          : "Salle " + e.salle;

      cell.innerHTML = `
        <div class="course-cell ${cls}">
          <div class="course-name">
            ${e.cours}
            <span class="badge ${badgeCls}" style="font-size:9px;padding:1px 6px">${e.type || ""}</span>
          </div>
          <div class="course-info">
            <i class="fa-solid fa-building" style="font-size:10px"></i> ${salleTxt}
          </div>
          <div class="course-info">
            <i class="fa-solid fa-user" style="font-size:10px"></i> ${e.prof}
          </div>
        </div>
      `;
    });

    document.getElementById("stat-total").textContent = data.length;
    document.getElementById("stat-profs").textContent = profsSet.size;
    document.getElementById("stat-salles").textContent = sallesSet.size;
    document.getElementById("stats-bar").style.display = "grid";
    document.getElementById("timetable-container").style.display = "block";
    document.getElementById("btn-download").style.display = "inline-flex";
    document.getElementById("num3").classList.add("done");
  } catch (err) {
    console.error(err);
    document.getElementById("loading-state").style.display = "none";
    document.getElementById("empty-state").style.display = "block";
  }
}

function downloadPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ orientation: "landscape", unit: "mm", format: "a4" });

  const joursP = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"];
  const heuresP = ["08:30", "10:15", "12:00", "14:30", "16:15"];
  const heuresLabels = [
    "08:30-10:00",
    "10:15-11:45",
    "12:00-13:30",
    "14:30-16:00",
    "16:15-17:45",
  ];

  const grid = {};
  lastGeneratedData.forEach((e) => {
    grid[e.creneau] = e;
  });

  doc.setFontSize(14);
  doc.setTextColor(83, 74, 183);
  doc.text(`Emploi du Temps — ${lastFiliereName}`, 14, 14);
  doc.setFontSize(9);
  doc.setTextColor(150);
  doc.text(`Généré le ${new Date().toLocaleDateString("fr-FR")}`, 14, 20);

  const head = [["Horaire", ...joursP]];
  const body = heuresP.map((h, hi) => [
    heuresLabels[hi],
    ...joursP.map((j) => {
      const isDisabled = j === "Samedi" && (h === "14:30" || h === "16:15");
      if (isDisabled) return "—";
      const e = grid[`${j} ${h}`];
      if (!e) return "";
      const salleTxt =
        e.salle.toLowerCase().includes("amphi") ||
        e.salle.toLowerCase().includes("labo")
          ? e.salle
          : "Salle " + e.salle;
      return `${e.cours} (${e.type || ""})\n${salleTxt}\n${e.prof}`;
    }),
  ]);

  doc.autoTable({
    head,
    body,
    startY: 25,
    styles: {
      fontSize: 7.5,
      cellPadding: 3,
      valign: "middle",
      overflow: "linebreak",
      lineColor: [220, 220, 230],
      lineWidth: 0.3,
      minCellHeight: 18,
    },
    headStyles: {
      fillColor: [83, 74, 183],
      textColor: 255,
      fontStyle: "bold",
      halign: "center",
      fontSize: 8,
    },
    columnStyles: {
      0: {
        fillColor: [245, 247, 251],
        fontStyle: "bold",
        halign: "center",
        cellWidth: 28,
      },
    },
    didParseCell(data) {
      if (data.section === "body" && data.column.index > 0) {
        const text = data.cell.raw || "";
        if (text.includes("(CM)")) {
          data.cell.styles.fillColor = [238, 237, 254];
          data.cell.styles.textColor = [60, 52, 137];
        } else if (text.includes("(TD)")) {
          data.cell.styles.fillColor = [255, 243, 205];
          data.cell.styles.textColor = [133, 100, 4];
        } else if (text.includes("(TP)")) {
          data.cell.styles.fillColor = [234, 243, 222];
          data.cell.styles.textColor = [39, 80, 10];
        } else if (text === "—") {
          data.cell.styles.fillColor = [240, 240, 240];
          data.cell.styles.textColor = [180, 180, 180];
          data.cell.styles.halign = "center";
        }
      }
    },
    margin: { left: 10, right: 10 },
  });

  doc.save(`emploi_du_temps_${lastFiliereName.replace(/\s+/g, "_")}.pdf`);
}

async function loadProfs() {
  const res = await fetch("/api/profs");
  allProfs = await res.json();
  renderProfs(allProfs);
}

function renderProfs(list) {
  const tbody = document.getElementById("profs-tbody");
  if (!list.length) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#aaa;padding:2rem">Aucun résultat</td></tr>`;
    return;
  }
  tbody.innerHTML = list
    .map(
      (p) => `
    <tr>
      <td style="font-weight:500">${p.nom}</td>
      <td>${p.prenom}</td>
      <td style="color:#888">${p.email || "-"}</td>
      <td><span class="badge badge-cm">${p.specialite || "-"}</span></td>
      <td>
        <button class="btn btn-sm" onclick='editProf(${JSON.stringify(p)})' style="margin-right:4px" title="Modifier">
          <i class="fa-solid fa-pen"></i>
        </button>
        <button class="btn btn-sm btn-danger" onclick="deleteProf(${p.id})" title="Supprimer">
          <i class="fa-solid fa-trash"></i>
        </button>
      </td>
    </tr>
  `,
    )
    .join("");
}

function filterProfs(v) {
  const q = v.toLowerCase();
  renderProfs(
    allProfs.filter((p) =>
      (p.nom + p.prenom + (p.email || "") + (p.specialite || ""))
        .toLowerCase()
        .includes(q),
    ),
  );
}

function openProfModal() {
  document.getElementById("prof-modal-title").textContent =
    "Ajouter un professeur";
  document.getElementById("prof-id").value = "";
  ["p-nom", "p-prenom", "p-email", "p-specialite"].forEach(
    (id) => (document.getElementById(id).value = ""),
  );
  document.getElementById("modal-prof").classList.add("open");
}

function editProf(p) {
  document.getElementById("prof-modal-title").textContent =
    "Modifier le professeur";
  document.getElementById("prof-id").value = p.id;
  document.getElementById("p-nom").value = p.nom;
  document.getElementById("p-prenom").value = p.prenom;
  document.getElementById("p-email").value = p.email || "";
  document.getElementById("p-specialite").value = p.specialite || "";
  document.getElementById("modal-prof").classList.add("open");
}

async function saveProf() {
  const id = document.getElementById("prof-id").value;
  const data = {
    nom: document.getElementById("p-nom").value.trim(),
    prenom: document.getElementById("p-prenom").value.trim(),
    email: document.getElementById("p-email").value.trim(),
    specialite: document.getElementById("p-specialite").value.trim(),
  };
  if (!data.nom || !data.prenom) return alert("Nom et prénom obligatoires");

  await fetch(id ? `/api/profs/${id}` : "/api/profs", {
    method: id ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  closeModal("prof");
  loadProfs();
}

async function deleteProf(id) {
  if (!confirm("Supprimer ce professeur ?")) return;
  await fetch(`/api/profs/${id}`, { method: "DELETE" });
  loadProfs();
}

async function loadSalles() {
  const res = await fetch("/api/salles");
  allSalles = await res.json();
  renderSalles(allSalles);
}

function getSalleType(s) {
  if (s.nom.toLowerCase().includes("amphi")) return "amphi";
  if (s.labo) return "labo";
  return "normal";
}

function renderSalles(list) {
  const filtered = salleTypeFilter
    ? list.filter((s) => getSalleType(s) === salleTypeFilter)
    : list;
  const tbody = document.getElementById("salles-tbody");

  if (!filtered.length) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:#aaa;padding:2rem">Aucune salle trouvée</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered
    .map((s) => {
      const type = getSalleType(s);
      const badge =
        type === "amphi"
          ? `<span class="badge badge-amphi"><i class="fa-solid fa-building" style="font-size:10px"></i> Amphithéâtre</span>`
          : type === "labo"
            ? `<span class="badge badge-labo"><i class="fa-solid fa-computer" style="font-size:10px"></i> Laboratoire</span>`
            : `<span class="badge badge-normal">Salle normale</span>`;

      return `
      <tr>
        <td style="font-weight:500">${s.nom}</td>
        <td>${s.capacite} places</td>
        <td>${badge}</td>
        <td>
          <button class="btn btn-sm" onclick='editSalle(${JSON.stringify(s)})' style="margin-right:4px" title="Modifier">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button class="btn btn-sm btn-danger" onclick="deleteSalle(${s.id})" title="Supprimer">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>
    `;
    })
    .join("");
}

function filterSalles(v) {
  const q = v.toLowerCase();
  renderSalles(allSalles.filter((s) => s.nom.toLowerCase().includes(q)));
}

function openSalleModal() {
  document.getElementById("salle-modal-title").textContent =
    "Ajouter une salle";
  document.getElementById("salle-id").value = "";
  document.getElementById("s-nom").value = "";
  document.getElementById("s-capacite").value = "";
  laboVal = 0;
  document.getElementById("labo-track").classList.remove("on");
  document.getElementById("modal-salle").classList.add("open");
}

function editSalle(s) {
  document.getElementById("salle-modal-title").textContent =
    "Modifier la salle";
  document.getElementById("salle-id").value = s.id;
  document.getElementById("s-nom").value = s.nom;
  document.getElementById("s-capacite").value = s.capacite;
  laboVal = s.labo || 0;
  laboVal
    ? document.getElementById("labo-track").classList.add("on")
    : document.getElementById("labo-track").classList.remove("on");
  document.getElementById("modal-salle").classList.add("open");
}

function toggleLabo() {
  laboVal = laboVal ? 0 : 1;
  laboVal
    ? document.getElementById("labo-track").classList.add("on")
    : document.getElementById("labo-track").classList.remove("on");
}

async function saveSalle() {
  const id = document.getElementById("salle-id").value;
  const data = {
    nom: document.getElementById("s-nom").value.trim(),
    capacite: parseInt(document.getElementById("s-capacite").value) || 0,
    labo: laboVal,
  };
  if (!data.nom || !data.capacite) return alert("Nom et capacité obligatoires");

  await fetch(id ? `/api/salles/${id}` : "/api/salles", {
    method: id ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  closeModal("salle");
  loadSalles();
}

async function deleteSalle(id) {
  if (!confirm("Supprimer cette salle ?")) return;
  await fetch(`/api/salles/${id}`, { method: "DELETE" });
  loadSalles();
}

async function loadFilieres() {
  const res = await fetch("/api/filieres");
  const list = await res.json();
  renderFilieres(list);
}

function renderFilieres(list) {
  const tbody = document.getElementById("filieres-tbody");
  if (!list.length) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#aaa;padding:2rem">Aucune filière trouvée</td></tr>`;
    return;
  }
  tbody.innerHTML = list
    .map(
      (f) => `
    <tr>
      <td style="font-weight:500">${f.nom}</td>
      <td>${f.nb_etudiants || "-"}</td>
      <td><span class="badge badge-td">${f.nb_td} groupe(s)</span></td>
      <td><span class="badge badge-tp">${f.nb_tp} groupe(s)</span></td>
      <td>
        <button class="btn btn-sm" onclick='editFiliere(${JSON.stringify(f)})' style="margin-right:4px" title="Modifier">
          <i class="fa-solid fa-pen"></i>
        </button>
        <button class="btn btn-sm btn-danger" onclick="deleteFiliere(${f.id})" title="Supprimer">
          <i class="fa-solid fa-trash"></i>
        </button>
      </td>
    </tr>
  `,
    )
    .join("");
}

function openFiliereModal() {
  document.getElementById("filiere-modal-title").textContent =
    "Ajouter une filière";
  document.getElementById("filiere-id").value = "";
  document.getElementById("f-nom").value = "";
  document.getElementById("f-etudiants").value = "";
  document.getElementById("f-td").value = "2";
  document.getElementById("f-tp").value = "4";
  document.getElementById("modal-filiere").classList.add("open");
}

function editFiliere(f) {
  document.getElementById("filiere-modal-title").textContent =
    "Modifier la filière";
  document.getElementById("filiere-id").value = f.id;
  document.getElementById("f-nom").value = f.nom;
  document.getElementById("f-etudiants").value = f.nb_etudiants || "";
  document.getElementById("f-td").value = f.nb_td || 2;
  document.getElementById("f-tp").value = f.nb_tp || 4;
  document.getElementById("modal-filiere").classList.add("open");
}

async function saveFiliere() {
  const id = document.getElementById("filiere-id").value;
  const data = {
    nom: document.getElementById("f-nom").value.trim(),
    nb_etudiants: parseInt(document.getElementById("f-etudiants").value) || 0,
    nb_td: parseInt(document.getElementById("f-td").value) || 1,
    nb_tp: parseInt(document.getElementById("f-tp").value) || 1,
  };
  if (!data.nom) return alert("Nom de la filière obligatoire");

  await fetch(id ? `/api/filieres/${id}` : "/api/filieres", {
    method: id ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  closeModal("filiere");
  loadFilieres();
}

async function deleteFiliere(id) {
  if (!confirm("Supprimer cette filière ?")) return;
  await fetch(`/api/filieres/${id}`, { method: "DELETE" });
  loadFilieres();
}

function closeModal(type) {
  document.getElementById("modal-" + type).classList.remove("open");
}

let touchStartY = 0;
let touchStartX = 0;

document.addEventListener(
  "touchstart",
  (e) => {
    touchStartY = e.touches[0].clientY;
    touchStartX = e.touches[0].clientX;
  },
  { passive: true },
);

document.addEventListener(
  "touchend",
  (e) => {
    const dy = touchStartY - e.changedTouches[0].clientY;
    const dx = Math.abs(touchStartX - e.changedTouches[0].clientX);

    if (dy > 80 && dx < 50) {
      const page =
        document.querySelector(".page.active")?.id?.replace("page-", "") ||
        "planning";
      openFullscreen(page);
    }
  },
  { passive: true },
);

document.getElementById("fullscreen-overlay").addEventListener(
  "touchstart",
  (e) => {
    touchStartY = e.touches[0].clientY;
  },
  { passive: true },
);

document.getElementById("fullscreen-overlay").addEventListener(
  "touchend",
  (e) => {
    const dy = e.changedTouches[0].clientY - touchStartY;
    if (dy > 80) closeFullscreen();
  },
  { passive: true },
);

function openFullscreen(page) {
  const overlay = document.getElementById("fullscreen-overlay");
  const body = document.getElementById("fullscreen-body");
  const title = document.getElementById("fullscreen-title");

  const activePage =
    document.querySelector(".page.active")?.id?.replace("page-", "") || page;

  if (activePage === "planning") {
    title.textContent = "Emploi du Temps Complet";
    const container = document.getElementById("timetable-container");
    if (container && container.style.display !== "none") {
      body.innerHTML = container.innerHTML;
    } else {
      body.innerHTML = `
        <div style="text-align:center;padding:3rem;color:#aaa">
          <i class="fa-solid fa-calendar-xmark" style="font-size:40px;display:block;margin-bottom:1rem;opacity:0.3"></i>
          <p>Aucun emploi du temps généré</p>
          <p style="font-size:12px;margin-top:6px">Générez un emploi du temps d'abord</p>
        </div>`;
    }
  } else if (activePage === "profs") {
    title.textContent = "Liste des Professeurs";
    fetch("/api/profs")
      .then((r) => r.json())
      .then((profs) => {
        body.innerHTML = profs
          .map(
            (p) => `
        <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid #f0f0f0">
          <div>
            <div style="font-weight:600;font-size:14px">${p.nom} ${p.prenom}</div>
            <div style="font-size:12px;color:#888">${p.email || ""}</div>
          </div>
          <span class="badge badge-cm">${p.specialite || "-"}</span>
        </div>
      `,
          )
          .join("");
      });
  } else if (activePage === "salles") {
    title.textContent = "Liste des Salles";
    fetch("/api/salles")
      .then((r) => r.json())
      .then((salles) => {
        body.innerHTML = salles
          .map((s) => {
            const type = s.nom.toLowerCase().includes("amphi")
              ? "amphi"
              : s.labo
                ? "labo"
                : "normal";
            const badge =
              type === "amphi"
                ? `<span class="badge badge-amphi">Amphi</span>`
                : type === "labo"
                  ? `<span class="badge badge-labo">Labo</span>`
                  : `<span class="badge badge-normal">Salle</span>`;
            return `
          <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid #f0f0f0">
            <div style="font-weight:600;font-size:14px">${s.nom}</div>
            <div style="display:flex;align-items:center;gap:10px">
              <span style="font-size:12px;color:#888">${s.capacite} places</span>
              ${badge}
            </div>
          </div>
        `;
          })
          .join("");
      });
  } else if (activePage === "filieres") {
    title.textContent = "Liste des Filières";
    fetch("/api/filieres/list")
      .then((r) => r.json())
      .then((filieres) => {
        const semestres = {};
        filieres.forEach((f) => {
          const sem = f.nom.substring(0, 2);
          if (!semestres[sem]) semestres[sem] = [];
          semestres[sem].push(f);
        });
        body.innerHTML = Object.entries(semestres)
          .map(
            ([sem, list]) => `
        <div style="margin-bottom:1.25rem">
          <div style="font-size:12px;font-weight:700;color:#534AB7;margin-bottom:8px;padding:4px 0;border-bottom:2px solid #EEEDFE">${sem}</div>
          ${list
            .map(
              (f) => `
            <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f5f5f5">
              <span style="font-size:13px;font-weight:500">${f.nom}</span>
              <button class="btn btn-sm btn-primary" onclick="closeFullscreen();goGenerate('${f.nom}','${sem}')">
                <i class="fa-solid fa-rotate"></i> Générer
              </button>
            </div>
          `,
            )
            .join("")}
        </div>
      `,
          )
          .join("");
      });
  } else if (activePage === "dashboard") {
    title.textContent = "Dashboard Complet";
    Promise.all([
      fetch("/api/filieres/list").then((r) => r.json()),
      fetch("/api/profs").then((r) => r.json()),
      fetch("/api/salles").then((r) => r.json()),
    ]).then(([filieres, profs, salles]) => {
      body.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:1.25rem">
          <div style="background:#f0eeff;border-radius:10px;padding:1rem;text-align:center">
            <div style="font-size:28px;font-weight:700;color:#534AB7">${filieres.length}</div>
            <div style="font-size:12px;color:#666">Filières</div>
          </div>
          <div style="background:#eafaf1;border-radius:10px;padding:1rem;text-align:center">
            <div style="font-size:28px;font-weight:700;color:#27AE60">${profs.length}</div>
            <div style="font-size:12px;color:#666">Professeurs</div>
          </div>
          <div style="background:#fef5e7;border-radius:10px;padding:1rem;text-align:center">
            <div style="font-size:28px;font-weight:700;color:#E67E22">${salles.length}</div>
            <div style="font-size:12px;color:#666">Salles</div>
          </div>
          <div style="background:#fdedec;border-radius:10px;padding:1rem;text-align:center">
            <div style="font-size:28px;font-weight:700;color:#E74C3C">${salles.filter((s) => s.labo).length}</div>
            <div style="font-size:12px;color:#666">Labos</div>
          </div>
        </div>
        <div style="font-size:13px;font-weight:600;margin-bottom:10px">Derniers professeurs</div>
        ${profs
          .slice(0, 5)
          .map(
            (p) => `
          <div style="padding:8px 0;border-bottom:1px solid #f0f0f0;font-size:13px">
            <span style="font-weight:500">${p.nom} ${p.prenom}</span>
            <span class="badge badge-cm" style="margin-left:8px">${p.specialite || "-"}</span>
          </div>
        `,
          )
          .join("")}
      `;
    });
  }

  overlay.classList.add("open");
  document.getElementById("swipe-trigger").style.display = "none";
}

function closeFullscreen() {
  document.getElementById("fullscreen-overlay").classList.remove("open");
  document.getElementById("swipe-trigger").style.display = "flex";
}

document.addEventListener("DOMContentLoaded", () => {
  buildGrid();
});
