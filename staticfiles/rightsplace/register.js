// ======================================================================
// Handling dynamic role-based form switching on the registration page.
// ======================================================================

// Hide all role forms
function hideAllForms() {
  document.getElementById('form-user').classList.add('hidden');
  document.getElementById('form-lawyer').classList.add('hidden');
  document.getElementById('form-ngo').classList.add('hidden');
}

// Show the form for the selected role
function selectRole(role) {
  hideAllForms();

  const formId = 'form-' + role;
  const formElement = document.getElementById(formId);

  if (formElement) {
    formElement.classList.remove('hidden');

    // Don't duplicate the hidden role input
    const existing = formElement.querySelector("input[name='role']");
    if (!existing) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'role';
      input.value = role;
      formElement.querySelector('form').appendChild(input);
    }
  }

  // Scroll smoothly to the revealed form
  formElement.scrollIntoView({ behavior: 'smooth' });
}
