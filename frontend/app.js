const contractForm = document.querySelector("#contract-form");
const validationForm = document.querySelector("#validation-form");
const contractSelect = document.querySelector("#contract-select");
const contractMessage = document.querySelector("#contract-message");
const resultBox = document.querySelector("#validation-result");
const historyState = document.querySelector("#history-state");
const historyList = document.querySelector("#history-list");

async function request(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) {
    const detail = payload.detail;
    const message = Array.isArray(detail) ? detail.map(item => item.msg).join("; ") : detail;
    throw new Error(message || `Request failed (${response.status}).`);
  }
  return payload;
}

function showError(target, error) {
  target.textContent = error.message;
  target.classList.add("error");
}

async function loadContracts(selectedId) {
  const contracts = await request("/api/contracts");
  contractSelect.replaceChildren();
  const prompt = new Option(contracts.length ? "Select a contract" : "Create a contract first", "");
  contractSelect.add(prompt);
  for (const contract of contracts) {
    contractSelect.add(new Option(`${contract.name} · ${contract.missing_value_threshold}% max missing`, contract.id));
  }
  contractSelect.disabled = contracts.length === 0;
  if (selectedId) contractSelect.value = String(selectedId);
}

function appendReasons(parent, reasons) {
  if (!reasons.length) return;
  const list = document.createElement("ul");
  for (const reason of reasons) {
    const item = document.createElement("li");
    item.textContent = reason;
    list.append(item);
  }
  parent.append(list);
}

function displayResult(validation) {
  resultBox.replaceChildren();
  resultBox.className = `result ${validation.status.toLowerCase()}`;
  const heading = document.createElement("h3");
  heading.textContent = `${validation.status} · ${validation.filename}`;
  resultBox.append(heading);
  if (validation.reasons.length) appendReasons(resultBox, validation.reasons);
  else resultBox.append("All required columns meet the contract threshold.");
}

async function loadHistory() {
  historyState.textContent = "Loading history…";
  const validations = await request("/api/validations");
  historyList.replaceChildren();
  historyState.textContent = validations.length ? "Most recent validations first." : "No validations yet. Run one above to start a history.";
  for (const validation of validations) {
    const item = document.createElement("article");
    item.className = "history-item";
    const badge = document.createElement("span");
    badge.className = `badge ${validation.status.toLowerCase()}`;
    badge.textContent = validation.status;
    const title = document.createElement("strong");
    title.textContent = validation.filename;
    const meta = document.createElement("p");
    meta.textContent = `${validation.contract_name} · ${new Date(validation.created_at).toLocaleString()}`;
    item.append(badge, title, meta);
    appendReasons(item, validation.reasons);
    historyList.append(item);
  }
}

contractForm.addEventListener("submit", async event => {
  event.preventDefault();
  const button = contractForm.querySelector("button");
  button.disabled = true;
  contractMessage.textContent = "Saving contract…";
  contractMessage.className = "message";
  try {
    const data = new FormData(contractForm);
    const columns = String(data.get("required_columns")).split(",").map(value => value.trim());
    const contract = await request("/api/contracts", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: data.get("name"), required_columns: columns,
        missing_value_threshold: Number(data.get("missing_value_threshold")) })
    });
    contractMessage.textContent = `Saved contract “${contract.name}”.`;
    contractMessage.classList.add("success");
    contractForm.reset();
    await loadContracts(contract.id);
  } catch (error) { showError(contractMessage, error); }
  finally { button.disabled = false; }
});

validationForm.addEventListener("submit", async event => {
  event.preventDefault();
  const button = validationForm.querySelector("button");
  button.disabled = true;
  resultBox.className = "result";
  resultBox.textContent = "Validating CSV…";
  try {
    const validation = await request("/api/validate", { method: "POST", body: new FormData(validationForm) });
    displayResult(validation);
    await loadHistory();
  } catch (error) { showError(resultBox, error); }
  finally { button.disabled = false; }
});

loadContracts().catch(error => {
  contractSelect.replaceChildren(new Option("Unable to load contracts", ""));
  showError(resultBox, error);
});
loadHistory().catch(error => showError(historyState, error));
