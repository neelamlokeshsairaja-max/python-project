async function apiRequest(url, data = null) {
  const options = data ? {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  } : {};
  const response = await fetch(url, options);
  const result = await response.json();
  if (!response.ok || result.success === false) throw new Error(result.message || "Operation failed.");
  return result;
}
function showMessage(id, message, success = true) {
  const element = document.getElementById(id);
  element.textContent = message;
  element.style.color = success ? "green" : "red";
}
async function loadDashboard() {
  try {
    const data = await apiRequest("/api/dashboard");
    document.getElementById("total-balance").textContent = "₹" + Number(data.total_balance).toFixed(2);
    document.getElementById("total-customers").textContent = data.total_customers;
    document.getElementById("total-accounts").textContent = data.total_accounts;
    document.getElementById("total-transactions").textContent = data.total_transactions;
  } catch (error) { console.error("Dashboard error:", error.message); }
}
document.getElementById("customer-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const customer = {
    name: document.getElementById("customer-name").value.trim(),
    phone: document.getElementById("customer-phone").value.trim(),
    email: document.getElementById("customer-email").value.trim()
  };
  try {
    const result = await apiRequest("/api/customers", customer);
    showMessage("message", `${result.message} Customer ID: ${result.customer_id}`);
    document.getElementById("customer-result").textContent = `Registered customer ID: ${result.customer_id}`;
    document.getElementById("account-customer-id").value = result.customer_id;
    this.reset(); await loadDashboard();
  } catch (error) { showMessage("message", error.message, false); }
});
document.getElementById("account-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const account = {
    customer_id: document.getElementById("account-customer-id").value,
    account_number: document.getElementById("account-number").value.trim(),
    account_type: document.getElementById("account-type").value,
    balance: document.getElementById("opening-balance").value
  };
  try {
    const result = await apiRequest("/api/accounts", account);
    showMessage("account-message", result.message);
    ["transaction-account", "statement-account", "interest-account"].forEach(id => {
      document.getElementById(id).value = result.account_number;
    });
    this.reset(); await loadDashboard();
  } catch (error) { showMessage("account-message", error.message, false); }
});
document.getElementById("transaction-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const transaction = {
    account_number: document.getElementById("transaction-account").value.trim(),
    transaction_type: document.getElementById("transaction-type").value,
    amount: document.getElementById("transaction-amount").value
  };
  try {
    const result = await apiRequest("/api/transactions", transaction);
    showMessage("transaction-message", `${result.message} New balance: ₹${Number(result.balance).toFixed(2)}`);
    this.reset(); await loadDashboard();
  } catch (error) { showMessage("transaction-message", error.message, false); }
});
document.getElementById("transfer-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const transfer = {
    sender_account: document.getElementById("sender-account").value.trim(),
    receiver_account: document.getElementById("receiver-account").value.trim(),
    amount: document.getElementById("transfer-amount").value
  };
  try {
    const result = await apiRequest("/api/transfers", transfer);
    showMessage("transfer-message", `${result.message} Sender: ₹${result.sender_balance.toFixed(2)} | Receiver: ₹${result.receiver_balance.toFixed(2)}`);
    this.reset(); await loadDashboard();
  } catch (error) { showMessage("transfer-message", error.message, false); }
});
document.getElementById("statement-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const account = document.getElementById("statement-account").value.trim();
  try {
    const result = await apiRequest(`/api/accounts/${encodeURIComponent(account)}/statement`);
    const rows = result.transactions.map(item =>
      `<tr><td>${escapeHtml(item.date)}</td><td>${escapeHtml(item.type)}</td><td>₹${Number(item.amount).toFixed(2)}</td><td>₹${Number(item.balance).toFixed(2)}</td><td>${escapeHtml(item.counterparty || "-")}</td></tr>`
    ).join("");
    document.getElementById("statement-result").innerHTML =
      `<p><strong>${escapeHtml(result.customer_name)}</strong> | ${escapeHtml(result.account_type)} | Balance: ₹${Number(result.balance).toFixed(2)}</p>
       <div class="table-wrap"><table><thead><tr><th>Date</th><th>Type</th><th>Amount</th><th>Balance</th><th>Counterparty</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  } catch (error) { showMessage("statement-result", error.message, false); }
});
document.getElementById("interest-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const account = document.getElementById("interest-account").value.trim();
  try {
    const result = await apiRequest(`/api/accounts/${encodeURIComponent(account)}/interest`);
    showMessage("interest-result", `Annual interest preview: ₹${Number(result.interest_preview).toFixed(2)}. ${result.note}`);
  } catch (error) { showMessage("interest-result", error.message, false); }
});
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  })[char]);
}
loadDashboard();
