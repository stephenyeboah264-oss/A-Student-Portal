document.addEventListener("DOMContentLoaded", () => {
  const stateSelect = document.getElementById("state");
  const lgaSelect = document.getElementById("lga");

 
  if (stateSelect && lgaSelect) {
    loadStates(stateSelect, lgaSelect);
    stateSelect.addEventListener("change", () => {
      loadLgas(stateSelect.value, lgaSelect);
    });
  }

  
  const statusSelect = document.getElementById("change-status");
  if (statusSelect) {
    const detailsSection = document.querySelector(".details-section");
    const studentId = detailsSection.dataset.studentId;
    statusSelect.addEventListener("change", () => {
      updateAdmissionStatus(studentId, statusSelect.value);
    });
  }
});


async function loadStates(stateSelect, lgaSelect) {
  try {
    const response = await fetch("/api/states");
    const states = await response.json();

    states.forEach((state) => {
      const option = document.createElement("option");
      option.value = state;
      option.textContent = state;
      stateSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Failed to load states:", error);
  }
}


async function loadLgas(state, lgaSelect) {
  lgaSelect.innerHTML = '<option value="">Select Local Government</option>';

  if (!state) return;

  try {
    const response = await fetch(`/api/lgas/${encodeURIComponent(state)}`);
    const lgas = await response.json();

    lgas.forEach((lga) => {
      const option = document.createElement("option");
      option.value = lga;
      option.textContent = lga;
      lgaSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Failed to load local governments:", error);
  }
}

async function updateAdmissionStatus(studentId, newStatus) {
  const messageEl = document.getElementById("status-message");
  const badgeEl = document.getElementById("status-badge");
  const currentStatusEl = document.getElementById("current-status");

  if (!newStatus) return;

  try {
    const response = await fetch(`/update_status/${studentId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    const result = await response.json();

    if (result.success) {
      badgeEl.textContent = result.status;
      badgeEl.className = `status-badge status-${result.status}`;
      currentStatusEl.textContent = result.status;
      messageEl.textContent = "Status updated!";
      messageEl.style.color = "green";
    } else {
      messageEl.textContent = result.message || "Update failed.";
      messageEl.style.color = "red";
    }
  } catch (error) {
    messageEl.textContent = "Network error. Please try again.";
    messageEl.style.color = "red";
    console.error(error);
  }
}