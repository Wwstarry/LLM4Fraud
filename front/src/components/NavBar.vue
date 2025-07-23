<script setup>
import {useRouter} from "vue-router";
import {ref} from "vue";

const router = useRouter();

const user = ref({
  Uname: '123',
  UFacePath: '/assets/photo/default.png',
  Uposition: 'Unknown'
});
const handleLogout = () => {
  sessionStorage.removeItem('isLoggedIn');
  router.push('/login');
}

</script>

<template>
  <!-- Navbar -->

  <nav
      class="layout-navbar container-xxl navbar navbar-expand-xl navbar-detached align-items-center bg-navbar-theme"
      id="layout-navbar"
  >
    <div class="layout-menu-toggle navbar-nav align-items-xl-center me-3 me-xl-0 d-xl-none">
      <a class="nav-item nav-link px-0 me-xl-4" href="javascript:void(0)">
        <i class="bx bx-menu bx-sm"></i>
      </a>
    </div>

    <div class="navbar-nav-right d-flex align-items-center" id="navbar-collapse">
      <!-- Search -->
      <div class="navbar-nav align-items-center">
        <div class="nav-item d-flex align-items-center">
          <i class="bx bx-search fs-4 lh-0"></i>
          <input
              type="text"
              class="form-control border-0 shadow-none"
              placeholder="Search..."
              aria-label="Search..."
          />
        </div>
      </div>
      <!-- /Search -->

      <ul class="navbar-nav flex-row align-items-center ms-auto">
        <!-- Place this tag where you want the button to render. -->

        <li class="nav-item navbar-dropdown dropdown-user dropdown">
          <a class="nav-link dropdown-toggle hide-arrow" href="javascript:void(0);"
             data-bs-toggle="dropdown">
            <div class="avatar avatar-online">
              <img :src="user.UFacePath" alt class="w-px-40 h-auto rounded-circle"/>
            </div>
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <a class="dropdown-item" href="#">
                <div class="d-flex">
                  <div class="flex-shrink-0 me-3">
                    <div class="avatar avatar-online">
                      <img :src="user.UFacePath" alt
                           class="w-px-40 h-auto rounded-circle"/>
                    </div>
                  </div>
                  <div class="flex-grow-1">
                    <span class="fw-semibold d-block">{{ user.Uname }}</span>
                    <small class="text-muted">{{user.Uposition}}</small>
                  </div>
                </div>
              </a>
            </li>
            <li>
              <div class="dropdown-divider"></div>
            </li>
            <li>
              <router-link class="dropdown-item" to="account">
                <i class="bx bx-user me-2"></i>
                <span class="align-middle">我的信息</span>
              </router-link>
            </li>
            <li>
              <router-link class="dropdown-item" to="account">
                <i class="bx bx-cog me-2"></i>
                <span class="align-middle">Settings</span>
              </router-link>
            </li>

            <li>
              <div class="dropdown-divider"></div>
            </li>
            <li>
              <a class="dropdown-item" @click="handleLogout" href=" ">
                <i class="bx bx-power-off me-2"></i>
                <span class="align-middle">退出登录</span>
              </a>
            </li>
          </ul>
        </li>
        <!--/ User -->
      </ul>
    </div>
  </nav>

  <!-- / Navbar -->
</template>

<style scoped>
@import url('/assets/vendor/fonts/boxicons.css');
@import url('/assets/vendor/css/core.css');
@import url('/assets/vendor/css/theme-default.css');
@import url('/assets/css/demo.css');
@import url('/assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.css');
@import url('/assets/vendor/libs/apex-charts/apex-charts.css');
</style>