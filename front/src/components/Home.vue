<script setup>
import Footer from "@/components/Footer.vue";
import SideBar from "@/components/SideBar.vue";
import NavBar from "@/components/NavBar.vue";


</script>

<template>
  <div class="layout-wrapper layout-content-navbar">
    <div class="layout-container">
      <!-- Menu -->
      <SideBar/>
      <!-- / Menu -->
      <!-- Layout container -->
      <div class="layout-page">
        <NavBar/>
        <!-- Content wrapper -->
        <div class="content-wrapper">
          <!-- Content -->

            <router-view></router-view>

          <!-- / Content -->
        </div>
        <Footer/>
        <div class="content-backdrop fade"></div>

        <!-- Content wrapper -->
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('/assets/vendor/fonts/boxicons.css');
@import url('/assets/vendor/css/core.css');
@import url('/assets/vendor/css/theme-default.css');
@import url('/assets/css/demo.css');
@import url('/assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.css');
@import url('/assets/vendor/libs/apex-charts/apex-charts.css');

.layout-page {
  background-color: #f3f3f8;
}


</style>