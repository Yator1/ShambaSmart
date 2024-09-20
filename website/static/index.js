function confirmDelete(event) {
    if (!confirm('Are you sure you want to delete this crop?')) {
        event.preventDefault();  // Prevent form submission if canceled
    }
}