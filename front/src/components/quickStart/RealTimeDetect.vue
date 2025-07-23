<template>
  <!-- Content -->
  <div class="container-xxl flex-grow-1 container-p-y">
    <div class="row">
      <div class="col-md-8">
        <div class="row">
          <div class="col-md-6">
            <div class="card" id="code">
              <div class="card-header"
                   style="display: flex; justify-content: space-between; padding-bottom: 10px; align-items: center">
                <h5 style="margin-bottom: 0">Emulator Controls</h5>
              </div>
              <div class="card-body">
                <small class="text-light fw-semibold d-block pt-3">Install App</small>
                <div class="input-group" id="selectapp">
                  <select v-model="selectedApp" class="form-select custom-select" id="inputGroupSelect04"
                          aria-label="Example select with button addon">
                    <option disabled value="">Choose...</option>
                    <option v-for="app in apps" :key="app.md5" :value="app.md5">{{ app.name }}</option>
                  </select>
                  <button class="btn btn-outline-primary" type="button" style="margin: 0" @click="installApp">
                    Install
                  </button>
                </div>

                <small class="text-light fw-semibold d-block pt-3">Keyboard Input</small>
                <div class="input-group">
                  <input v-model="inputText" type="text" class="form-control" placeholder="">
                  <button class="btn btn-outline-primary" type="button" style="margin: 0" @click="inputTextToDevice">
                    Send
                  </button>
                </div>

                <small class="text-light fw-semibold d-block pt-3">Menu Keys</small>
                <div class="btn-group" role="group" aria-label="First group"
                     style="justify-content: space-between; display: flex">
                  <button type="button" class="btn btn-outline-secondary" @click="sendKeyEvent(4)">
                    <i class="tf-icons bx bx-arrow-back"></i>
                  </button>
                  <button type="button" class="btn btn-outline-secondary" @click="sendKeyEvent(3)">
                    <i class="tf-icons bx bxs-home"></i>
                  </button>
                  <button type="button" class="btn btn-outline-secondary" @click="sendKeyEvent(187)">
                    <i class="tf-icons bx bx-minus-back"></i>
                  </button>
                </div>

                <div class="btn-group" role="group" aria-label="First group"
                     style="justify-content: space-between; display: flex">
                  <button type="button" class="btn btn-outline-secondary" @click="play">
                    <i class="tf-icons bx bx-play"></i>
                  </button>
                  <button type="button" class="btn btn-outline-secondary" @click="stop">
                    <i class="tf-icons bx bx-stop"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card" id="code">
              <div class="card-header"
                   style="display: flex; justify-content: space-between; padding-bottom: 10px; align-items: center">
                <h5 style="margin-bottom: 0">Sensitive Permissions Monitor</h5>
              </div>
              <div class="card-body">
                <div class="input-group">
                  <input v-model="packageName" type="text" class="form-control" placeholder="Package Name">
                  <button class="btn btn-outline-primary" style="margin: 0" type="button" id="button-addon2"
                          @click="setPackageName">Confirm
                  </button>
                </div>
              </div>
              <div class="card-body" ref="permissionContainer" style="overflow-y: auto">
                <div v-for="(item, index) in permissions" :key="index" class="risk-item">
                  <div class="risk-content">
                    <div class="risk-header">
                      <img :src="getRiskIcon(item.risk)" class="risk-icon">
                      This app uses
                      <span class="risk-attribute" style="background-color: rgb(86, 106, 127); color: white;">
                        {{ item.name }}
                      </span>
                      permission
                      <span :style="{ color: getRiskColor(item.risk) }" style="font-weight:bold">
                        {{ item.value }}
                      </span>.
                    </div>
                    <div class="risk-explanation">
                      {{ item.detail }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card mt-4 h-50">
          <div class="card-header"
               style="display: flex; justify-content: space-between; padding-bottom: 10px; align-items: center">
            <h5 style="margin-bottom: 0">System Logs</h5>
          </div>
          <div class="card-body h-px-200" ref="logContainer" style="overflow-y: auto">
            <pre>{{ systemLogs }}</pre>
          </div>
        </div>
      </div>

      <!-- Emulator -->
      <div class="col-md-4">
        <div class="card" style="height: calc(85vh - 10px); position: relative;">
          <div class="card-body overflow-auto stimulate" style="padding: 0">
            <AndroidEmulator class="container-andro" ref="emulator"/>
          </div>
        </div>
      </div>
    </div>
    <div class="content-backdrop fade"></div>
  </div>
</template>


<script setup>
import {ref, onMounted, nextTick, onUnmounted} from 'vue';
import axios from 'axios';
import AndroidEmulator from '@/components/quickStart/androidScreen.vue';
import {useRoute} from "vue-router";

const selectedApp = ref('');
const inputText = ref('');
const apps = ref([]);
const dealmd5 = ref('')

const emulator = ref(null);
const systemLogs = ref('');
const permissions = ref('');
const logContainer = ref(null);
const permissionContainer = ref(null);
let logIntervalId = null;
let permissionIntervalId = null;
const risk_counts = ref(null);

onMounted(async () => {
  try {
    const response = await axios.get('/apps');
    apps.value = response.data.map(app => ({
      name: app[0],
      md5: app[1]
    }));
  } catch (error) {
    console.error('Error fetching apps:', error);
  }
});

const installApp = async () => {
  if (!selectedApp.value) {
    alert('Please select an app to install.');
    return;
  }
  try {
    dealmd5.value = selectedApp.value;
    const response = await axios.post('/install', {md5: selectedApp.value});
    console.log(response.data);
  } catch (error) {
    console.error('Error installing app:', error);
  }
};

const inputTextToDevice = async () => {
  if (!inputText.value) {
    alert('Please enter text to send.');
    return;
  }
  try {
    const response = await axios.post('/input-text', {text: inputText.value});
    console.log(response.data);
  } catch (error) {
    console.error('Error inputting text:', error);
  }
};

const sendKeyEvent = async (keycode) => {
  try {
    const response = await axios.post('/keyevent', {keycode});
    console.log(response.data);
  } catch (error) {
    console.error('Error sending keyevent:', error);
  }
};


const fetchSystemLogs = async () => {
  try {
    const response = await axios.get('/systemlogs');
    if (response.data.logs) {
      systemLogs.value = response.data.logs;
      console.log(systemLogs.value);
      await nextTick();
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    }
  } catch (error) {
    console.error('Error fetching system logs:', error);
  }
};

// const fetchPermissions = async (packageName) => {
//   try {
//     const response = await axios.get(`http://localhost:5000/permissions/${packageName}`);
//     if (response.data.permissions) {
//       permissions.value = response.data.permissions;
//       console.log(permissions.value);
//       await nextTick();
//       permissionContainer.value.scrollTop = permissionContainer.value.scrollHeight;
//     }
//   } catch (error) {
//     console.error(`Error fetching permissions for ${packageName}:`, error);
//   }
// };

const getRiskIcon = (riskPercentage) => {
  if (riskPercentage === 2) {
    return '/src/assets/risk-high.svg'; // 红色图标路径
  } else if (riskPercentage === 1) {
    return '/src/assets/risk-low.svg'; // 橙色图标路径
  }
  return ''; // 低于60%不显示图标
};

const getRiskColor = (riskPercentage) => {
  if (riskPercentage === 2) {
    return 'red';
  } else if (riskPercentage === 1) {
    return 'orange';
  }
  return 'inherit'; // 默认颜色
};

const fetchPermissions = async (packageName) => {
  try {
    const response = await axios.get(`/get_permissions?pack=${packageName}`);
    if (response.data) {
      permissions.value = response.data.detailed_permissions;
      risk_counts.value = response.data.risk_counts;
      console.log(permissions.value);
      await nextTick();
      permissionContainer.value.scrollTop = permissionContainer.value.scrollHeight;
    }
  } catch (error) {
    console.error(`Error fetching permissions for ${packageName}:`, error);
  }
};

const route = useRoute();
const packageName = ref(route.params.package_name);

const setPackageName = () => {
  dealmd5.value = packageName.value;
};

const play = () => {
  if (emulator.value) {
    emulator.value.startCapturing();
  }
  logIntervalId = setInterval(fetchSystemLogs, 1000); // 每3秒请求一次系统日志
  permissionIntervalId = setInterval(() => fetchPermissions(dealmd5.value), 5000);
};

const stop = () => {
  if (emulator.value) {
    emulator.value.stopCapturing();
  }
  if (logIntervalId !== null) {
    clearInterval(logIntervalId);
    logIntervalId = null;
  }
  if (permissionIntervalId !== null) {
    clearInterval(permissionIntervalId);
    permissionIntervalId = null;
  }
};

onUnmounted(() => {
  stop();
});
</script>

<style scoped>
.container-andro {
  width: 100%;
  height: 100%;
  display: block; /* 确保canvas作为块级元素 */
}

#code {
  height: calc(40vh - 10px);
}

#feedbackOverlay {
  display: flex;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
  align-items: center;
  justify-content: center;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.stimulate {
  position: relative;
  padding: 5px;
  border: 5px solid #5e7185; /* 与 padding 值相同 */
  border-radius: 10px;
}

.custom-select {
  max-height: 50px; /* 设置下拉菜单的最大高度 */
  overflow-y: auto; /* 添加垂直滚动条 */
}

.custom-select option {
  max-height: 50px; /* 设置选项的最大高度 */
}

.risk-explanation {
  margin-top: 4px;
  font-size: 0.8em;
  font-weight: 200;
}

.risk-attribute {
  display: flex;
  padding-left: 2px;
  padding-right: 2px;
  border-radius: 4px;
}

.risk-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-size: 1em;
}

.risk-icon {
  margin-right: 8px;
}

.risk-content {
  display: flex;
  flex-direction: column;
}

.risk-header {
  font-weight: 200;
  vertical-align: center;
  display: flex;
}

</style>
