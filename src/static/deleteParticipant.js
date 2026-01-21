document.addEventListener('click', (event) => {
  if (event.target.classList.contains('delete-btn')) {
    const email = event.target.getAttribute('data-email');
    // Call the function to unregister the participant
    unregisterParticipant(email);
  }
});

async function unregisterParticipant(email) {
  try {
    const response = await fetch(`/unregister?email=${encodeURIComponent(email)}`, {
      method: 'DELETE',
    });
    const result = await response.json();
    if (response.ok) {
      // Handle success (e.g., refresh the activities list)
      fetchActivities();
    } else {
      console.error('Error unregistering participant:', result);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}