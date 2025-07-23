<script setup>
import { useRoute } from "vue-router";

const route = useRoute();
const isActive = (path) => route.path === path;
// Check if the current path starts with /home
const isStart = (path) => route.path.startsWith(path);
const isLogin = sessionStorage.getItem('isLoggedIn');
</script>

<template>
  <aside id="layout-menu" class="layout-menu menu-vertical menu bg-menu-theme">
    <div class="app-brand demo">
      <a href="" class="app-brand-link">
        <span class="app-brand-text demo menu-text fw-bolder ms-2" style="text-transform: uppercase;">
          <img src="../../assets/picture/Logo.png" class="mb-2" alt="" width="4%">AgentDroid
        </span>
      </a>

      <a href="javascript:void(0);" class="layout-menu-toggle menu-link text-large ms-auto d-block d-xl-none">
        <i class="bx bx-chevron-left bx-sm align-middle"></i>
      </a>
    </div>

    <div class="menu-inner-shadow"></div>

    <ul class="menu-inner py-1">
      <!-- Dashboard -->
      <li v-show="isLogin" :class="{ 'active': isActive('/home/index'), 'menu-item': true }">
        <router-link to="/home/index" class="menu-link">
          <i class="menu-icon tf-icons bx bx-home-circle"></i>
          <div data-i18n="Analytics">Dashboard</div>
        </router-link>
        <!--
        <router-link to="/home/ipTracking" class="menu-link">
          <i class="menu-icon tf-icons bx bx-home-circle"></i>
          <div data-i18n="Analytics">IP Tracking</div>
        </router-link>
        -->
      </li>

      <li v-show="isLogin" class="menu-header small text-uppercase">
        <span class="menu-header-text">Project Management</span>
      </li>

      <li
        v-show="isLogin"
        :class="{ 'active': isActive('/home/project') || isActive('/home/projectDetail') || isStart('/home/projectDetail'), 'menu-item': true }"
      >
        <router-link to="/home/project" class="menu-link">
          <i class="menu-icon tf-icons bx bx-detail"></i>
          <div data-i18n="Form Elements">Scan List</div>
        </router-link>
      </li>

      <li v-show="isLogin" :class="{ 'active': isActive('/home/upgradeProjectView'), 'menu-item': true }">
        <router-link to="/home/upgradeProjectView" class="menu-link">
          <i class="menu-icon tf-icons bx bx-upload"></i>
          <div data-i18n="Form Elements">APP Scan</div>
        </router-link>
      </li>

      <li v-show="isLogin" :class="{ 'active': isActive('/home/whiteSetting'), 'menu-item': true }">
        <router-link to="/home/whiteSetting" class="menu-link">
          <i class="menu-icon tf-icons bx bxs-cog"></i>
          <div data-i18n="Form Elements">Allow & Block List</div>
        </router-link>
      </li>

      <li v-show="isLogin" class="menu-header small text-uppercase">
        <span class="menu-header-text">Quick Start</span>
      </li>

      <li v-show="isLogin" :class="{ 'active': isActive('/home/catalogue'), 'menu-item': true }">
        <router-link to="/home/catalogue" class="menu-link">
          <i class="menu-icon tf-icons bx bx-cube-alt"></i>
          <div data-i18n="Account Settings">Smart Q&A</div>
        </router-link>
      </li>

      <li v-show="isLogin" :class="{ 'active': isActive('/home/realTimeDetect') || isStart('/home/realTimeDetect'), 'menu-item': true }">
        <router-link to="/home/realTimeDetect" class="menu-link">
          <i class="menu-icon tf-icons bx bx-crown"></i>
          <div data-i18n="Account Settings">Runtime Simulation</div>
        </router-link>
      </li>

      <li v-show="isLogin" class="menu-header small text-uppercase">
        <span class="menu-header-text">Account Management</span>
      </li>

      <li v-show="isLogin" :class="{ 'active': isActive('/home/account'), 'menu-item': true }">
        <router-link to="/home/account" class="menu-link">
          <i class="menu-icon tf-icons bx bx-dock-top"></i>
          <div data-i18n="Account Settings">Account Settings</div>
        </router-link>
      </li>

      <li v-show="!isLogin" class="menu-header small text-uppercase">
        <span class="menu-header-text">Offline Mode</span>
      </li>

      <li v-show="!isLogin" :class="{ 'active': isActive('/home/offline') || isStart('/home/offanalyze'), 'menu-item': true }">
        <router-link to="/home/offline" class="menu-link">
          <i class="menu-icon tf-icons bx bx-wifi-off"></i>
          <div data-i18n="Account Settings">Offline Scan</div>
        </router-link>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
@import url('/assets/vendor/fonts/boxicons.css');
@import url('/assets/vendor/css/core.css');
@import url('/assets/vendor/css/theme-default.css');
@import url('/assets/css/demo.css');
@import url('/assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.css');
@import url('/assets/vendor/libs/apex-charts/apex-charts.css');
</style>
