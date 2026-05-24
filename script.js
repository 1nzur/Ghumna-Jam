const form = document.querySelector("#bookingForm");
const message = document.querySelector("#bookingMessage");
const submitButton = form.querySelector("button[type='submit']");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const booking = Object.fromEntries(formData.entries());
  booking.people = Number(booking.people);

  message.textContent = "Sending your booking request...";
  message.classList.remove("error");
  submitButton.disabled = true;

  try {
    const response = await fetch("/api/bookings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(booking)
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Unable to save booking.");
    }

    message.textContent = `Booking request saved. Reference #${result.booking_id}.`;
    form.reset();
  } catch (error) {
    message.textContent = `${error.message} Please make sure the backend and MySQL are running.`;
    message.classList.add("error");
  } finally {
    submitButton.disabled = false;
  }
});
