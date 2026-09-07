/* CampusMind — Client JS */

// Assistant chat
document.addEventListener('DOMContentLoaded', () => {
  const chatSend = document.getElementById('chatSend');
  const chatInput = document.getElementById('chatInput');
  const chatMessages = document.getElementById('chatMessages');

  if (chatSend && chatInput && chatMessages) {
    const sendMsg = async () => {
      const msg = chatInput.value.trim();
      if (!msg) return;

      // Add user message
      const userDiv = document.createElement('div');
      userDiv.className = 'chat-msg user';
      userDiv.textContent = msg;
      chatMessages.appendChild(userDiv);
      chatInput.value = '';
      chatMessages.scrollTop = chatMessages.scrollHeight;

      try {
        const res = await fetch('/api/assistant/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        const botDiv = document.createElement('div');
        botDiv.className = 'chat-msg bot';
        botDiv.innerHTML = data.reply.replace(/\n/g, '<br>');
        chatMessages.appendChild(botDiv);
      } catch (e) {
        const errDiv = document.createElement('div');
        errDiv.className = 'chat-msg bot';
        errDiv.textContent = 'Sorry, something went wrong.';
        chatMessages.appendChild(errDiv);
      }
      chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    chatSend.addEventListener('click', sendMsg);
    chatInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMsg(); });
  }

  // Attendance mark
  const attForm = document.getElementById('attendanceForm');
  if (attForm) {
    attForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(attForm);
      const res = await fetch('/api/attendance/mark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.fromEntries(formData))
      });
      const data = await res.json();
      const resultDiv = document.getElementById('attendanceResult');
      if (resultDiv) {
        resultDiv.innerHTML = data.success
          ? `<div class="alert alert-success">${data.message}</div>`
          : `<div class="alert alert-error">${data.message}</div>`;
      }
    });
  }

  // Syllabus toggle
  document.querySelectorAll('.syllabus-toggle').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      const res = await fetch(`/api/syllabus/${id}/toggle`, { method: 'POST' });
      const data = await res.json();
      if (data.success) location.reload();
    });
  });

  // Notification read
  document.querySelectorAll('.notif-read').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      await fetch(`/api/notifications/${id}/read`, { method: 'POST' });
      btn.closest('.card').style.opacity = '0.5';
      btn.remove();
    });
  });

  // Confirm dialogs
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });
});
