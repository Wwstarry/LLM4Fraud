<script setup>
const year = new Date().getFullYear();
</script>

<template>
  <!-- Footer -->
  <footer class="content-footer footer bg-footer-theme">
    <div class="container-xxl d-flex flex-wrap justify-content-between py-2 flex-md-row flex-column">
      <div class="mb-2 mb-md-0">
        © {{year}}, AgentDroid
      </div>
    </div>
  </footer>
  <!-- / Footer -->
</template>

<style scoped>
@import url('/assets/vendor/fonts/boxicons.css');
@import url('/assets/vendor/css/core.css');
@import url('/assets/vendor/css/theme-default.css');
@import url('/assets/css/demo.css');
@import url('/assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.css');
@import url('/assets/vendor/libs/apex-charts/apex-charts.css');
</style>