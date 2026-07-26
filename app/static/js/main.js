function postJSON(url, body) {
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  }).then(async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Something went wrong.");
    return data;
  });
}

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

document.addEventListener("click", (e) => {
  const saveBtn = e.target.closest("[data-save-btn]");
  if (saveBtn) {
    const card = saveBtn.closest("[data-job-id]");
    const jobId = card.dataset.jobId;
    saveBtn.disabled = true;
    postJSON(`/api/jobs/${jobId}/save`)
      .then(({ saved, save_count }) => {
        saveBtn.classList.toggle("is-saved", saved);
        saveBtn.querySelector("[data-save-label]").textContent = saved ? "Saved" : "Save";
        saveBtn.querySelector("[data-save-count]").textContent = save_count;
      })
      .catch((err) => alert(err.message))
      .finally(() => { saveBtn.disabled = false; });
    return;
  }

  const toggleBtn = e.target.closest("[data-toggle-comments]");
  if (toggleBtn) {
    const card = toggleBtn.closest("[data-job-id]");
    const panel = card.querySelector("[data-comments]");
    panel.hidden = !panel.hidden;
    return;
  }

  const closeBtn = e.target.closest("[data-close-job-btn]");
  if (closeBtn) {
    const jobId = closeBtn.dataset.jobId;
    closeBtn.disabled = true;
    postJSON(`/api/jobs/${jobId}/toggle`)
      .then(({ is_active }) => {
        closeBtn.textContent = is_active ? "Close listing" : "Reopen listing";
        const badge = document.querySelector(`[data-status-badge="${jobId}"]`);
        if (badge) badge.textContent = is_active ? "Open" : "Closed";
      })
      .catch((err) => alert(err.message))
      .finally(() => { closeBtn.disabled = false; });
  }
});

document.addEventListener("submit", (e) => {
  const form = e.target.closest("[data-comment-form]");
  if (!form) return;
  e.preventDefault();

  const card = form.closest("[data-job-id]");
  const jobId = card.dataset.jobId;
  const input = form.querySelector("input");
  const body = input.value.trim();
  if (!body) return;

  const button = form.querySelector("button");
  button.disabled = true;

  postJSON(`/api/jobs/${jobId}/comments`, { body })
    .then(({ name, body: savedBody, comment_count }) => {
      const list = card.querySelector("[data-comment-list]");
      const li = document.createElement("li");
      li.innerHTML = `<strong>${escapeHTML(name)}</strong> `;
      li.append(document.createTextNode(savedBody));
      list.appendChild(li);
      card.querySelector("[data-comment-count]").textContent = comment_count;
      input.value = "";
    })
    .catch((err) => alert(err.message))
    .finally(() => { button.disabled = false; });
});
