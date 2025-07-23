<script setup>
import {computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch} from 'vue';
import {API_BASE_URL} from "@/api/config.js";
import axios from "axios";

const repositoryURL = ref('');
const loading = ref(false);

const projectName = ref('');
const modelName = ref('');
const fileSelected = ref(null);
const Proname = ref('');

const user = ref({
  UFacePath: '/path/to/user/image.png',
  Uname: 'User Name',
  Uposition: 'User Position'
});

const projects = ref([]);
// Variables for project information, initialized as needed

const project = ref({
  Proname: '',
  Pfilepath: '',
  Pmodel: ''
});


const qrCode = ref({
  Proname: '',
  Pimage: '',
  Pmodel: '',
})


const localProject = ref({
  Proname: '',
  Pmodel: '',
  Pfile: ''
});

const canSubmit1 = computed(() => {
  return project.value.Proname.trim() && project.value.Pfilepath.trim() && project.value.Pmodel;
});

const canSubmit2 = computed(() => {
  return qrCode.value.Proname.trim() && qrCode.value.Pimage && qrCode.value.Pmodel;
});

const canSubmit3 = computed(() => {
  return localProject.value.Proname.trim() && localProject.value.Pfile && localProject.value.Pmodel;
});

async function submitProject() {
  showProgress(true);
  console.log('Submitting project:', project.value);
  const formData = new FormData();
  formData.append('url', project.value.Pfilepath);
  formData.append('model', project.value.Pmodel);

  try {
    const response = await fetch(`${API_BASE_URL}/upload/url`, {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    console.log('Upload response:', data);
    isReadyCheck.value = true;
    md5.value = data.md5;
    console.log('URL upload succeeded, returned md5:', md5.value);
    alert("Upload successful!");
  } catch (error) {
    console.error('Error uploading file:', error);
    alert("Upload failed, MD5 already exists!");
  }

  showProgress(false);
}

function showProgress(isShow) {
  loading.value = isShow;
  const contu = document.getElementById("contu");
  if (contu) {
    contu.style.setProperty("padding-top", isShow ? "0.8rem" : "1.625rem", "important");
  }
}

async function submitQRProject() {
  showProgress(true);
  console.log('Submitting QR project:', qrCode.value);
  const formData = new FormData();
  formData.append('image', qrCode.value.Pimage);
  formData.append('model', qrCode.value.Pmodel);

  try {
    const response = await fetch(`${API_BASE_URL}/upload/qr`, {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    console.log('Upload response:', data);
    isReadyCheck.value = true;
    md5.value = data.md5;
    console.log('QR code upload succeeded, returned md5:', md5.value);
    alert("Upload successful!");
  } catch (error) {
    console.error('Error uploading file:', error);
    alert("Upload failed, MD5 already exists!");
  }

  showProgress(false);
}

function fetchProjects() {
  // Example stub; replace with real API call
  projects.value = [
    { Pname: 'Project A', Ptime: '2021-01-01T00:00:00Z', Pvul: 5, Pfix: 3 },
    // ...
  ];
}

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file && !file.type.startsWith('application/vnd.android.package-archive')) {
    alert("Please upload an APK file");
    return;
  }
  localProject.value.Pfile = file;
};

async function submitLocalProject() {
  showProgress(true);
  const formData = new FormData();
  formData.append('file', localProject.value.Pfile);
  formData.append('model', localProject.value.Pmodel);

  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData
    });
    if (response.ok) {
      const data = await response.json();
      isReadyCheck.value = true;
      md5.value = data.md5;
      console.log('Local upload succeeded, returned md5:', md5.value);
      alert("Upload successful!");
    } else {
      console.error('File upload failed');
      alert("Upload failed, MD5 already exists!");
    }
  } catch (error) {
    console.error('Error:', error);
    alert("Upload failed, MD5 already exists!");
  }

  showProgress(false);
}

const handleQRChange = (event) => {
  const file = event.target.files[0];
  if (file && !file.type.startsWith('image/')) {
    alert("Please upload an image file");
    return;
  }
  qrCode.value.Pimage = file;
};

const postProject = () => {
  console.log('Posting project:', project.value);
};

const maxHeight = ref(0);

const setMaxHeight = () => {
  nextTick(() => {
    const cards = ['.link-card', '.qr-code-card', '.local-card'].map(sel => document.querySelector(sel));
    if (cards.every(c => c)) {
      const heights = cards.map(c => c.offsetHeight);
      maxHeight.value = Math.max(...heights);
      cards.forEach(c => c.style.height = maxHeight.value + 'px');
    }
  });
};
// --------------进度条----------------
const progress = ref(0);
const progressText = ref('0%');
const progressBarWidth = ref('0%');
const intervalId = ref(null);
const isReadyCheck = ref(false);
const md5 = ref('');

async function simulateLoading() {
  isReadyCheck.value = false;
  progress.value = 0;
  intervalId.value = setInterval(() => {
    const speed = Math.random() * 2;
    progress.value += speed;
    progressBarWidth.value = `${progress.value}%`;
    progressText.value = `${Math.round(progress.value)}%`;
    if (progress.value >= 95) {
      clearInterval(intervalId.value);
      progressBarWidth.value = `99%`;
      progressText.value = `99%`;
    }
  }, 1500); // 每隔500毫秒更新一次
}

async function startDetect() {
  if (md5.value) {
    try {
      await axios.post('/detect', {
        md5: md5.value,
      }).then(res => {
        if (res.status === 200) {
          if (progress.value < 95) {
            clearInterval(intervalId.value);
          }
          progress.value = 100;
          progressBarWidth.value = `100%`;
          progressText.value = `100%`;
          // isReadyCheck.value = false;
        } else {
          progress.value = 0;
          progressBarWidth.value = `0%`;
          progressText.value = `0%`;
          isReadyCheck.value = true;
          // alert("检测失败，请重新上传文件");
          throw new Error('Service not 200');
        }
        fetchCatalogue();
      })
    } catch (error) {
      // 处理网络错误或其他异常
      progress.value = 0;
      progressBarWidth.value = '0%';
      progressText.value = '0%';
      isReadyCheck.value = true;
      clearInterval(intervalId.value);
      alert("检测失败，请稍后再试");
      console.error('Network or other error:', error);
    }
  }
}


import {marked} from 'marked';

const leftChats = reactive([
  {name: "Package Tracer", message: "", parsedMessage: computed(() => marked("Hello, I am Package Tracer."))},
  {name: "Content Analizer", message: "", parsedMessage: computed(() => marked("Hello, I am Content Analyzer."))},
  {
    name: "Certificate Inspector",
    message: "",
    parsedMessage: computed(() => marked("Hello, I am Certificate Inspector."))
  }
]);

const rightChats = reactive([
  {name: "Icon Analizer", message: "", parsedMessage: computed(() => marked("Hello, I am Icon Analyzer."))},
  {
    name: "Sensitive Analizer",
    message: "",
    parsedMessage: computed(() => marked("Hello, I am Sensitive Info Analyzer."))
  },
  {
    name: "Relationship Analizer",
    message: "",
    parsedMessage: computed(() => marked("Hello, I am Relationship Analyzer."))
  }
]);

const updateParsedMessages = () => {
  leftChats.forEach(chat => {
    chat.parsedMessage = computed(() => marked(chat.message));
  });

  rightChats.forEach(chat => {
    chat.parsedMessage = computed(() => marked(chat.message));
  });
};

const fetchCatalogue = async () => {
  try {
    const response = await axios.get(`/api/chat-messages?md5=${md5.value}`);
    const data = response.data;

    leftChats[0].message = data.leftChats[0]; // Package Tracer
    leftChats[1].message = data.rightChats[1]; // Content Analizer
    leftChats[2].message = data.leftChats[2]; // Certificate Inspector
    rightChats[0].message = data.rightChats[0]; // Icon Analizer
    rightChats[1].message = data.leftChats[1]; // Sensitive Info Analizer
    rightChats[2].message = data.rightChats[2]; // Relationship Analizer

    updateParsedMessages();
  } catch (error) {
    console.error('Error fetching chat messages:', error);
  }
};

onMounted(() => {
  fetchProjects();
  setMaxHeight();
});

onBeforeUnmount(() => {
  clearInterval(intervalId.value);
});
</script>


<template>
  <transition name="fade">
    <div class="loader-container" v-if="loading">
      <div class="loader-bar"></div>
    </div>
  </transition>
  <div class="container-xxl flex-grow-1 container-p-y" id="contu">
    <div class="row">
      <!-- URL Upload -->
      <div class="col-md-4">
        <div class="card mb-4 link-card">
          <h5 class="card-header">Link</h5>
          <div class="d-flex justify-content-center align-items-center" style="height: 100px;">
            <i class='bx bxs-archive-in' style="font-size: 100px;"></i>
          </div>
          <div class="card-body demo-vertical-spacing demo-only-element">
            <form @submit.prevent="submitProject">
              <div class="row mb-3">
                <label class="col-sm-3 col-form-label" for="basic-url1">Download URL</label>
                <div class="col-sm-9">
                  <input type="text" class="form-control" id="basic-url1"
                         placeholder="URL"
                         v-model="project.Pfilepath" />
                </div>
              </div>
              <div class="row mb-2">
                <label class="col-sm-3 col-form-label" for="model-select">Select Model</label>
                <div class="col-sm-9 d-flex">
                  <select class="form-select me-2" id="model-select" v-model="project.Pmodel">
                    <option value="Precise Detection">Precise Detection</option>
                    <option value="Fast Detection">Fast Detection</option>
                  </select>
                  <button class="btn btn-outline-primary" type="submit">Upload!</button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- QR Code Upload -->
      <div class="col-md-4">
        <div class="card mb-4 qr-code-card">
          <h5 class="card-header">QR Code</h5>
          <div class="d-flex justify-content-center align-items-center" style="height: 100px;">
            <i class='bx bx-qr-scan' style="font-size: 100px;"></i>
          </div>
          <div class="card-body demo-vertical-spacing demo-only-element">
            <form @submit.prevent="submitQRProject">
              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">QR Code</label>
                <div class="col-sm-9">
                  <input type="file" class="form-control"
                         accept="image/*"
                         @change="handleQRChange" />
                </div>
              </div>
              <div class="row mb-2">
                <label class="col-sm-3 col-form-label">Select Model</label>
                <div class="col-sm-9 d-flex">
                  <select class="form-select me-2" v-model="qrCode.Pmodel">
                    <option value="Precise Detection">Precise Detection</option>
                    <option value="Fast Detection">Fast Detection</option>
                  </select>
                  <button class="btn btn-outline-primary" type="submit">Upload!</button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Local File Upload -->
      <div class="col-md-4">
        <div class="card mb-4 local-card">
          <h5 class="card-header">Local</h5>
          <div class="text-center" style="height: 100px;">
            <i class='bx bx-code-block' style="font-size: 100px;"></i>
          </div>
          <div class="card-body demo-vertical-spacing demo-only-element">
            <form @submit.prevent="submitLocalProject">
              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">Upload APK</label>
                <div class="col-sm-9">
                  <input type="file" class="form-control"
                         accept=".apk,application/vnd.android.package-archive"
                         @change="handleFileChange" />
                </div>
              </div>
              <div class="row mb-2">
                <label class="col-sm-3 col-form-label">Select Model</label>
                <div class="col-sm-9 d-flex">
                  <select class="form-select me-2" v-model="localProject.Pmodel">
                    <option value="Precise Detection">Precise Detection</option>
                    <option value="Fast Detection">Fast Detection</option>
                  </select>
                  <button class="btn btn-outline-primary" type="submit">Upload!</button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!--      下面的内容     -->
      <div class="col-md-12">
        <!-- Contextual Classes -->
        <div class="card">
          <div class="d-flex align-items-center align-content-center justify-content-between">
            <h5 class="card-header w-25">Detection Progress <span class="text-primary">{{ progressText }}</span></h5>
            <div class="px-4">
              <button class="btn-primary btn rounded w-15" :disabled="!isReadyCheck"
                      @click="simulateLoading(); startDetect();">
                Start Detection
              </button>
            </div>
          </div>

          <div class="card-body">
            <div class="progress">
              <div class="progress-bar progress-bar-striped progress-bar-animated bg-primary"
                   role="progressbar" :style="{ width: progressBarWidth }" :aria-valuenow="progress"
                   aria-valuemin="0" aria-valuemax="100"></div>
            </div>
          </div>

          <div class="card-body" style="display: block">
            <div class="row" style="height: 100%; width: 100%">
              <div class="col-md-6">
                <div class="chat-left" v-for="(item, index) in leftChats" :key="'left-' + index">
                  <div class="role-container" style="width: 85px;">
                    <img :src="`/role${index + 1}.jpg`" alt="role image" class="role-image">
                    <div class="role-name">{{ item.name }}</div>
                  </div>
                  <div class="speech-bubble" v-html="item.parsedMessage"></div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="chat-right" v-for="(item, index) in rightChats" :key="'right-' + index">
                  <div class="speech-bubble" v-html="item.parsedMessage"></div>
                  <div class="role-container" style="width: 85px;">
                    <img :src="`/role${index + 4}.jpg`" alt="role image" class="role-image">
                    <div class="role-name">{{ item.name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!--/ Contextual Classes -->
      </div>
    </div>
  </div>

</template>


<style scoped>
.report-loading-text {
  justify-content: center;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.loader-container {
  width: 100%;
  height: 4px; /* 加载条的高度 */
  margin-top: 0.8%;
//background-color: white; //border: 1px solid #ccc; border-radius: 2px; overflow: hidden; /* 隐藏超出容器部分的加载条 */
  position: relative;
}

.loader-bar {
  width: 10%; /* 加载条的初始宽度 */
  height: 100%;
  background-color: rgb(96, 91, 255); /* 加载条颜色 */
  position: absolute;
  animation: slide 4s ease-in-out infinite; /* 动画，持续时间2秒，线性速度，无限循环 */
}

@keyframes slide {
  from {
    left: -10%; /* 从左边界开始，开始时加载条不可见 */
  }
  to {
    left: 100%; /* 移动到容器的右端，结束时加载条不可见 */
  }
}

.row {
  display: flex;
  justify-content: space-between;
}

.chat-left, .chat-right {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
}

.chat-left {
  justify-content: flex-start;
  width: 100%;
}

.chat-right {
  justify-content: flex-end;
  width: 100%;
}

.role-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 10px;
}

.chat-right .role-container {
  margin-left: 10px;
  margin-right: 0;
}

.role-image {
  width: 50px;
  height: 50px;
}

.speech-bubble {
  background-color: #f0f0f0;
  border-radius: 10px;
  padding: 10px;
  width: 100%;
  word-wrap: break-word;
  //max-width: 100%; 
  word-break: break-all;  /* 强制在单词内断行 */
}

.chat-right .speech-bubble {
  background-color: #d0e6ff;
}

.role-name {
  font-size: 14px;
  color: #333;
  margin-top: 5px;
  text-align: center;
}


:deep(.speech-bubble h1) {
  font-size: 1.75em;
}

:deep(.speech-bubble h2) {
  font-size: 1.5em;
}

:deep(.speech-bubble h3) {
  font-size: 1.25em;
}

:deep(.speech-bubble h4) {
  font-size: 1.25em;
}

:deep(.speech-bubble h5) {
  font-size: 1em;
}

:deep(.speech-bubble h6) {
  font-size: 0.875em;
}

</style>