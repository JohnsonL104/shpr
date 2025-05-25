document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("filter-form");
  form.addEventListener("change", () => {
    form.submit(); // Automatically submit the form on change
  });
});