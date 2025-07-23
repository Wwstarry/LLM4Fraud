<template>
  <div aria-live="polite" aria-atomic="true" style="position: relative; min-height: 200px;">
    <div id="toast-container" style="position: absolute; top: 1rem; right: 1rem;">
      <!-- Toast messages will be appended here -->
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    showToast({ title, message, type = 'success', delay = 3000 }) {
      const toastContainer = this.$el.querySelector('#toast-container');
      const toastId = `toast-${Date.now()}`;
      const toastTypeClass = type === 'success' ? 'bg-success' : type === 'danger' ? 'bg-danger' : 'bg-info';
      const toastHtml = `
          <div id="${toastId}" class="toast ${toastTypeClass} text-white" role="alert" aria-live="assertive" aria-atomic="true" data-delay="${delay}">
              <div class="toast-header">
                  <strong class="mr-auto">${title}</strong>
                  <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
                      <span aria-hidden="true">&times;</span>
                  </button>
              </div>
              <div class="toast-body">
                  ${message}
              </div>
          </div>
      `;

      $(toastContainer).append(toastHtml);
      $(`#${toastId}`).toast('show');

      // Automatically remove the toast element after it hides
      $(`#${toastId}`).on('hidden.bs.toast', function () {
        $(this).remove();
      });
    }
  }
}
</script>

<style scoped>
/* Add your custom styles here */
</style>