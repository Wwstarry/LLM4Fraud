<script setup>
import {ref, onMounted} from 'vue';
import axios from 'axios';
import {useRouter} from "vue-router";

const router = useRouter();
const page_obj = ref({
  has_previous: false,
  previous_page_number: 1,
  has_next: false,
  next_page_number: 2,
  number: 1,
  paginator: {
    page_range: [1, 2, 3],
    num_pages: 3
  }
});
const isEmpty = ref(false);

const projects = ref([]);
const currentPage = ref(1);
const totalPages = ref(1);
const perPage = ref(15);

const fetchData = async (page = 1) => {
  try {
    const response = await axios.get(`/apk_data?page=${page}&per_page=${perPage.value}`);
    const data = response.data;
    projects.value = data.data.map((item, index) => ({
      Pname: item.App_Name,
      Pmd5: item.MD5,
      Pprob: item.prob === '0' ? '尚未检测' : item.prob,
      Pres: item.res === '-1' ? '尚未检测' : item.res,
      Pmodel: item.model,
      Ppackage: item.Package_Name,
      Plabel: item.Label
    }));
    console.log("data::",data)
    page_obj.value.number = data.page;
    page_obj.value.has_previous = data.page > 1;
    page_obj.value.previous_page_number = data.page - 1;
    page_obj.value.has_next = data.page < data.total_pages;
    page_obj.value.next_page_number = data.page + 1;
    page_obj.value.paginator.num_pages = data.total_pages;
    page_obj.value.paginator.page_range = Array.from({ length: data.total_pages }, (_, i) => i + 1);

    isEmpty.value = projects.value.length === 0;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

const submitAction = async (action, projectMD5) => {
  console.log(`Action: ${action}, Project ID: ${projectMD5}`);
  if (action === 'lookInside') {
    router.push({
      name: 'projectDetail',
      params: {md5: projectMD5},
    });
  }
  if (action === 'startCheck') {
    try {
      const response = await axios.post('/detect', { md5: projectMD5 });
      console.log('Start checking project:', response.data); // Log success or response data
      // ElMessage({
      //   showClose: true,
      //   plain: true,
      //   type: 'success',
      //   message: '成功开始检测APK！',
      // });
      alert('成功检测APK！');
    } catch (error) {
      console.error('Error starting checking project:', error);
      // ElMessage({
      //   showClose: true,
      //   plain: true,
      //   type: 'error',
      //   message: '检测APK失败！',
      // });
      alert('检测APK失败！');
    }
  }
  if (action === 'deleteProject') {
    try {
      // Send a POST request to delete project by MD5
      const response = await axios.post('/delete_apk', { md5: projectMD5 });
      console.log('Delete project:', response.data); // Log success or response data
      // Optionally, refresh data after deletion
      await fetchData(currentPage.value); // Refresh the project list
      // ElMessage({
      //   showClose: true,
      //   plain: true,
      //   type: 'success',
      //   message: '成功删除APK信息！',
      // });
      alert('成功删除APK信息！');
    } catch (error) {
      console.error('Error deleting project:', error);
      // ElMessage({
      //   showClose: true,
      //   plain: true,
      //   type: 'error',
      //   message: '删除APK信息失败！',
      // });
      alert('删除APK信息失败！');
    }
  }
  if (action === 'dynamicSim') {
    await router.push({
      name: 'realTimeDetect',
      params: {package_name: projectMD5},
    });
  }
};

onMounted(() => fetchData(currentPage.value));

</script>

<template>
  <div class="container-xxl flex-grow-1 container-p-y">
    <div class="col-md-12">
      <!-- Bootstrap Table with Caption -->
      <div v-if="!isEmpty" class="card">
<h5 class="card-header">APK List</h5>
<div class="table-responsive text-nowrap">
  <table class="table" style="text-align: center;" id="main_table">
    <thead>
    <tr>
      <th>App Name</th>
      <th>MD5</th>
      <th>Package Name</th>
      <th>Risk Level</th>
      <th>Detection Result</th>
      <th>Model</th>
      <th>Actions</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(project, index) in projects" :key="index">
              <td><i class="fab fa-angular fa-lg text-danger me-3"></i> <strong>{{ project.Pname }}</strong></td>
              <td>{{ project.Pmd5 }}</td>
              <td class="pack_bar">{{ project.Ppackage }}</td>
              <td><div v-if="project.Pprob=== 0">未检测</div>
                  <div v-else>{{ project.Pprob }}</div>
              </td>
              <td>
                <span v-if="project.Pres === '1'"
                      class="badge bg-label-danger me-1">{{ project.Plabel }}</span>
                <span v-else-if="project.Pprob=== 0"
                      class="badge bg-label-info me-1">未检测</span>
                <span v-else class="badge bg-label-success me-1">White</span>
              </td>
              <td>{{ project.Pmodel }}</td>
              <td>
                <div class="dropdown">
                  <button type="button" class="btn p-0 dropdown-toggle hide-arrow" data-bs-toggle="dropdown">
                    <i class="bx bx-dots-vertical-rounded"></i>
                  </button>
                  <div class="dropdown-menu">
                    <button @click="submitAction('lookInside', project.Pmd5)" class="dropdown-item"
                            :disabled="project.Pprob === 0">
                      <i class="bx bx-edit-alt me-1"></i> 查看详情
                    </button>
                    <button @click="submitAction('startCheck', project.Pmd5)" class="dropdown-item">
                      <i class="bx bx-check-circle me-1"></i> 检测
                    </button>
                    <button @click="submitAction('dynamicSim', project.Ppackage)" class="dropdown-item">
                      <i class="bx bx-code-alt me-1"></i> 动态模拟
                    </button>
                    <button @click="submitAction('deleteProject', project.Pmd5)" class="dropdown-item">
                      <i class="bx bx-trash me-1"></i> 删除
                    </button>
                  </div>
                </div>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
        <!-- Pagination -->
        <div class="ms-4"
             style="display: flex; justify-content: space-between; align-items: center; margin-right: 5%">
          <div>
            List of Projects
          </div>
          <!-- Basic Pagination -->
          <div style="margin-top: 2%">
            <nav aria-label="Page navigation">
              <ul class="pagination">
                <li v-if="page_obj.has_previous" class="page-item first">
                  <a class="page-link" @click.prevent="fetchData(1)" href="#">最前</a>
                </li>
                <li v-if="page_obj.has_previous" class="page-item prev">
                  <a class="page-link" @click.prevent="fetchData(page_obj.previous_page_number)" href="#">上一页</a>
                </li>

                <li v-for="num in page_obj.paginator.page_range" :key="num" class="page-item" :class="{active: page_obj.number === num}">
                  <a class="page-link" @click.prevent="fetchData(num)" href="#">{{ num }}</a>
                </li>

                <li v-if="page_obj.has_next" class="page-item next">
                  <a class="page-link" @click.prevent="fetchData(page_obj.next_page_number)" href="#">下一页</a>
                </li>
                <li v-if="page_obj.has_next" class="page-item last">
                  <a class="page-link" @click.prevent="fetchData(page_obj.paginator.num_pages)" href="#">最后</a>
                </li>
              </ul>
            </nav>
            <!--/ Basic Pagination -->
          </div>
        </div>
      </div>
      <div v-else class="card">
        <div class="container-xxl container-p-y">
          <div class="misc-wrapper" style="text-align: center">
            <h2 class="mb-2 mx-2">项目列表为空！</h2>
            <p class="mb-4 mx-2">还没有进行过检测噢！请先去上传项目吧~</p>
            <a href="/home/upgradeProjectView" class="btn btn-primary">去检测</a>
            <div class="mt-4">
              <img src="/assets/img/illustrations/girl-doing-yoga-light.png" alt="girl-doing-yoga-light" width="500"
                   class="img-fluid"/>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
td .dropdown {
  position: static;
}

.pack_bar {
  max-width: 250px;
  overflow-x: auto;
}

.pack_bar::-webkit-scrollbar {
  width: 7px;
  height: 7px;
}

/* 滚动条轨道 */
.pack_bar::-webkit-scrollbar-track {
  background: #f1f1f1; /* 滚动条轨道背景色设置为透明 */
}

/* 滚动条滑块 */
.pack_bar::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2); /* 滚动条的颜色，可以调整透明度 */
  border-radius: 5px; /* 滚动条滑块的圆角 */
}

/* 滚动条滑块悬停时 */
.pack_bar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.4); /* 滚动条滑块悬停时的颜色，可以调整透明度 */
}

/* 隐藏滚动条两端的箭头 */
.pack_bar::-webkit-scrollbar-button {
  display: none;
}

</style>
