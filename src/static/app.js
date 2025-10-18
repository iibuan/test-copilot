// Function to unregister a participant (global scope for onclick handler)
async function unregisterParticipant(activityName, email) {
  const messageDiv = document.getElementById("message");
  
  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );

    const result = await response.json();

    if (response.ok) {
      // Show success message
      messageDiv.textContent = result.message;
      messageDiv.className = "success";
      messageDiv.classList.remove("hidden");

      // Refresh the activities list to show updated participants
      location.reload();
    } else {
      messageDiv.textContent = result.detail || "An error occurred";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
    }

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  } catch (error) {
    messageDiv.textContent = "Failed to unregister. Please try again.";
    messageDiv.className = "error";
    messageDiv.classList.remove("hidden");
    console.error("Error unregistering:", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        let participantsListElem;
        if (details.participants.length > 0) {
          participantsListElem = document.createElement("ul");
          participantsListElem.className = "participants-list";
          details.participants.forEach(email => {
            const li = document.createElement("li");

            const emailSpan = document.createElement("span");
            emailSpan.className = "participant-email";
            emailSpan.textContent = email;

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.title = "Remove participant";
            deleteBtn.textContent = "✕";
            deleteBtn.addEventListener("click", () => {
              unregisterParticipant(name, email);
            });

            li.appendChild(emailSpan);
            li.appendChild(deleteBtn);
            participantsListElem.appendChild(li);
          });
        } else {
          participantsListElem = document.createElement("p");
          participantsListElem.className = "no-participants";
          participantsListElem.textContent = "No participants yet";
        }

        activityCard.innerHTML = `
          <h4></h4>
          <p class="activity-description"></p>
          <p><strong>Schedule:</strong> <span class="activity-schedule"></span></p>
          <p><strong>Availability:</strong> <span class="activity-spots"></span></p>
          <div class="participants-section">
            <p><strong>Current Participants:</strong></p>
          </div>
        `;

        // Set safe text content for activity details
        activityCard.querySelector("h4").textContent = name;
        activityCard.querySelector(".activity-description").textContent = details.description;
        activityCard.querySelector(".activity-schedule").textContent = details.schedule;
        activityCard.querySelector(".activity-spots").textContent = `${spotsLeft} spots left`;

        // Append participants list element
        activityCard.querySelector(".participants-section").appendChild(participantsListElem);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Refresh the page to show updated participants
        setTimeout(() => {
          location.reload();
        }, 1000);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
