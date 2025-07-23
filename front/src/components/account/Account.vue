<script setup>
import {ref, onMounted, handleError} from "vue";

const user = ref({
  UFacePath: '/assets/photo/default.png',
  UFirstName: '123',
  ULastName: '123',
  Uemail: '',
  Uorgnization: '',
  Uphone: '',
  Uposition: '',
});

// 上传文件
const upload = ref(null);

// 修改密码
const old_password = ref('');
const password = ref('');
const confirm_password = ref('');


function handleFileUpload(event) {
  upload.value = event.target.files[0];
}
function upgradePhoto() {

}

function validatePhoneNumber() {

}

function changPassword() {

}

function deleteAccount() {

}

</script>

<template>
  <!-- Content -->

  <div class="container-xxl flex-grow-1 container-p-y">

    <div class="row">
      <div class="col-md-12">
        <ul class="nav nav-pills flex-column flex-md-row mb-3">
          <li class="nav-item">
            <a class="nav-link active" href="javascript:void(0);"><i
                class="bx bx-user me-1"></i> 账户</a>
          </li>
        </ul>
        <div class="card mb-4">
          <h5 class="card-header">详细信息</h5>
          <!-- Account -->
          <div class="card-body">
            <div class="d-flex align-items-start align-items-sm-center gap-4">
              <img
                  :src="user.UFacePath"
                  alt=""
                  class="d-block rounded"
                  height="100"
                  width="100"
                  id="uploadedAvatar"
              />
              <div class="button-wrapper">
                <form method="POST" @submit.prevent="upgradePhoto"
                      enctype="multipart/form-data" id="uploadForm">
                  <label for="upload" class="btn btn-primary me-2 mb-4" tabindex="0">
                    <span class="d-none d-sm-block">上传新头像</span>
                    <i class="bx bx-upload d-block d-sm-none"></i>
                    <input
                        type="file"
                        id="upload"
                        class="account-file-input"
                        name="upload"
                        hidden
                        accept="image/png, image/jpeg"
                        @change="handleFileUpload"
                    />
                  </label>

                  <button type="submit"
                          class="btn btn-outline-secondary account-image-reset mb-4">
                    <i class="bx bx-reset d-block d-sm-none"></i>
                    <span class="d-none d-sm-block">保存头像</span>
                  </button>
                </form>
                <p class="text-muted mb-0">仅支持上传JPG或PNG格式的图片.</p>
              </div>
            </div>
          </div>
          <hr class="my-0"/>
          <div class="card-body">
            <form id="formAccountSettings" method="POST" @submit.prevent="validatePhoneNumber">
              <div class="row">
                <div class="mb-3 col-md-6">
                  <label for="firstName" class="form-label">姓</label>
                  <input
                      class="form-control"
                      type="text"
                      id="firstName"
                      name="firstName"
                      v-model="user.UFirstName"
                      autofocus
                  />
                </div>
                <div class="mb-3 col-md-6">
                  <label for="lastName" class="form-label">名</label>
                  <input class="form-control" type="text" name="lastName" id="lastName"
                         v-model="user.ULastName"/>
                </div>
                <div class="mb-3 col-md-6">
                  <label for="email" class="form-label">邮箱地址</label>
                  <input
                      class="form-control"
                      type="text"
                      id="email"
                      name="email"
                      v-model="user.Uemail"
                      placeholder="john.doe@example.com"
                  />
                </div>
                <div class="mb-3 col-md-6">
                  <label for="organization" class="form-label">组织</label>
                  <input
                      type="text"
                      class="form-control"
                      id="organization"
                      name="organization"
                      v-model="user.Uorgnization"
                  />
                </div>
                <div class="mb-3 col-md-6">
                  <label class="form-label" for="phoneNumber">手机</label>
                  <div class="input-group input-group-merge">
                    <span class="input-group-text">China (+86)</span>
                    <input
                        type="text"
                        id="phoneNumber"
                        name="phoneNumber"
                        class="form-control"
                        placeholder="Phone Number"
                        v-model="user.Uphone"
                    />
                  </div>
                </div>
                <div class="mb-3 col-md-6">
                  <label for="address" class="form-label">职位</label>
                  <input type="text" class="form-control" id="address" name="address"
                         placeholder="Address" v-model="user.Uposition"/>
                </div>

              </div>
              <div class="mt-2">
                <button type="submit" class="btn btn-primary me-2">保存修改</button>
              </div>
            </form>
          </div>
          <!-- /Account -->
        </div>
        <div class="card mb-4">
          <div class="card">
            <h5 class="card-header">修改密码</h5>
            <div class="card-body">
              <form id="changepassword" @submit.prevent="changPassword" method="post">
                <div class="mb-3 col-12 mb-0">
                  <div class="mb-3 col-md-12">
                    <label for="old_password" class="form-label">请输入当前密码</label>
                    <input type="password" class="form-control" id="old_password"
                           v-model="old_password" placeholder="*********"/>
                  </div>
                  <div class="mb-3 col-md-12">
                    <label for="password" class="form-label">输入新密码</label>
                    <input class="form-control" type="password" id="password"
                           v-model="password" placeholder="**********"/>
                  </div>
                  <div class="mb-3 col-md-12">
                    <label for="confirm-password"
                           class="form-label">再次输入新密码</label>
                    <input class="form-control" type="password" id="confirm-password"
                           v-model="confirm_password" placeholder="**********"/>
                  </div>
                </div>

                <button type="submit" class="btn btn-primary me-2" id="changePasswordBtn">
                  确认修改
                </button>
              </form>
            </div>
          </div>
        </div>


        <div class="card">
          <h5 class="card-header">删除账户</h5>
          <div class="card-body">
            <div class="mb-3 col-12 mb-0">
              <div class="alert alert-warning">
                <h6 class="alert-heading fw-bold mb-1">您确定要删除此账户吗？</h6>
                <p class="mb-0">注意！此操作无法更改，请您慎重考虑！</p>
              </div>
            </div>
            <form id="formAccountDeactivation" @submit.prevent="deleteAccount" method="post">
              <div class="form-check mb-3">
                <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="accountActivation"
                    id="accountActivation"
                />
                <label class="form-check-label" for="accountActivation"
                >我确认要删除此账户</label
                >
              </div>
              <button type="submit" class="btn btn-danger deactivate-account">删除账户！
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- / Content -->
</template>

<style scoped>

</style>