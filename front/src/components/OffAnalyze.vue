<script setup>
import {computed, onMounted, ref} from "vue";
import PerfectScrollbar from 'perfect-scrollbar';
import "/assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.css";
import {useRoute, useRouter} from "vue-router";
import axios from "axios";
import {marked} from "marked";
import {API_BASE_URL} from "@/api/config.js";
import Probability_distribution_chart from "@/components/project/Probability_distribution_chart.vue";
import Off_prob from "@/components/off_prob.vue";

const route = useRoute();
const md5 = route.params.md5;

const isloading = ref(true);
// scrollbar
const file_text = ref('');
const report_content = ref('');
const perm_content = ref('');
const region_bar = ref('');
const report_taokebar = ref('');


const permissions = ref([]);
const risk_counts = ref({});

const apk_data = ref({
  Activities: "",
  App_Name: "",
  Cert_Hash_Algo: "",
  Cert_Issuer: "",
  Cert_SHA1: "",
  Cert_SHA256: "",
  Cert_Serial_Number: 0,
  Cert_Signature_Algo: "",
  Cert_Subject: "",
  Label: "",
  Logo_Path: "",
  MD5: "",
  Main_Activity: "",
  Package_Name: "",
  Permissions: [],
  Receivers: [],
  Services: [],
  black: 0,
  blackList: 0,
  gamble: 0,
  scam: 0,
  sex: 0,
  size: "",
  white: 0
});

const result_data = ref({
  MD5: "",
  model: "",
  prob: 0,
  res: ""
});

const ip_data = ref({
  MD5: "",
  city: [],
  country: [],
  domain: null,
  ip: [],
  loc: [],
  region: []
});

const modelReport0 = ref('');
const modelReport1 = ref('');
const modelReport2 = ref('');
const modelReport3 = ref('');
const modelReport4 = ref('');
const modelReport5 = ref('');
const parsedMarkdown0 = computed(() => marked(modelReport0.value));
const parsedMarkdown1 = computed(() => marked(modelReport1.value));
const parsedMarkdown2 = computed(() => marked(modelReport2.value));
const parsedMarkdown3 = computed(() => marked(modelReport3.value));
const parsedMarkdown4 = computed(() => marked(modelReport4.value));
const parsedMarkdown5 = computed(() => marked(modelReport5.value));

const graphData = ref({
  nodes: [],
  links: []
});
const filteredLinks = ref([]);

// --------------------------------获取数据-------------------------------------
const fetchData = async (md5) => {
  try {
    const response = await axios.get(`/report/info?md5=${md5}`);
    const data = response.data;

    apk_data.value = data["apk_data"];
    result_data.value = data["result_data"];
    ip_data.value = data["ip_data"];


    const response_list = await axios.get(`/get_permissions?md5=${md5}`);
    permissions.value = response_list.data.detailed_permissions;
    risk_counts.value = response_list.data.risk_counts;
    console.log("数据获取成功")


    const ps = new PerfectScrollbar(file_text.value, {
      wheelSpeed: 0.2,
      wheelPropagation: false,
      minScrollbarLength: 20
    });
    const ps2 = new PerfectScrollbar(perm_content.value, {
      wheelSpeed: 0.2,
      wheelPropagation: false,
      minScrollbarLength: 20
    });
    const ps3 = new PerfectScrollbar(report_content.value, {
      wheelSpeed: 0.3,
      wheelPropagation: false,
      minScrollbarLength: 20
    });

    // 报告的API
    isloading.value = true;
    const response2 = await axios.get(`/report/agent?md5=${md5}`);
    modelReport0.value = response2.data.ip_analysis;
    modelReport1.value = response2.data.permission_analysis;
    modelReport2.value = response2.data.activity_analysis;
    modelReport3.value = response2.data.certificate_analysis;
    modelReport4.value = response2.data.summary;
    modelReport5.value = response2.data.limitations;
    isloading.value = false;


  } catch (error) {
    console.error('获取数据时出错:', error);
    // 处理错误情况
  }
}

// --------------------------------域名数据-------------------------------------
const domainRegionData = ref([]);


// --------------------------------权限数据-------------------------------------

// const highRiskCount = computed(() => {
//   return violations.value.filter(item => item.rule_rank ===2).length;
// });
//
// const mediumRiskCount = computed(() => {
//   return violations.value.filter(item => item.rule_rank ===1).length;
// });
//
// 根据风险百分比获取数值的颜色
const getRiskColor = (riskPercentage) => {
  if (riskPercentage === 2) {
    return 'red';
  } else if (riskPercentage === 1) {
    return 'orange';
  }
  return 'inherit'; // 默认颜色
};
//
// 根据风险百分比获取对应的图标路径
const getRiskIcon = (riskPercentage) => {
  if (riskPercentage === 2) {
    return '/src/assets/risk-high.svg'; // 红色图标路径
  } else if (riskPercentage === 1) {
    return '/src/assets/risk-low.svg'; // 橙色图标路径
  }
  return ''; // 低于60%不显示图标
};
//
// // 对风险数据进行排序，优先显示高风险
// const sortedRiskData = computed(() => {
//   console.log( violations.value)
//   return violations.value
//       .filter(item => item.rule_rank!==0)
//       .sort((a, b) => {
//         // 首先根据 rule_id 排序，使得 rule_id 为 2 的项排在前面
//         if (a.rule_rank !== b.rule_rank) {
//           return b.rule_rank - a.rule_rank; // 2 会排在 1 前面
//         }
//         // 如果 rule_id 相同，则根据 riskPercentage 排序，风险高的排前面
//         return b.riskPercentage - a.riskPercentage;
//       });
// });

// ------------------------------------套壳APP风险分析------------------------------------
const getIconUrl = (name) => {
  const node = graphData.value.nodes.find(node => node.id === name);
  const icon = node ? `${API_BASE_URL}/icon/${node.md5}.png` : '';
  return icon
};


// ------------------------------------挂载------------------------------------
onMounted(async () => {

  await fetchData(md5);


});
</script>

<template>
  <div class="container-xxl flex-grow-1 container-p-x">
    <div class="container-p-y" style="min-height: 80vh; height: 120vh;">
      <div class="row" style="height: 100%">


        <div class="col-lg-6 col-md-6 mb-4" style="height: 100%">

          <!--          APP详情         -->
          <div class="card mb-4" style="height: 30%">
            <div class="card-body" style="height: 100%">
              <div class="row logo_info" style="height: 100%;">
                <div class="col-lg-4 col-md-4" style="height: 100%">
                  <div class="row flex-wrap  align-items-center logo-title">
                    <i class='bx bxl-android bx-sm col-2' style="color: #566a7f"></i>
                    <span class="fw-bolder fs-4 col-8">{{ apk_data.App_Name }}</span>
                  </div>
                  <div class="flex-wrap justify-content-center align-items-center logo-img">
                    <div
                        style="width: 80px; height: 80px; overflow: hidden; display: flex; justify-content: center; align-items: center;">
                      <img :src="`${API_BASE_URL}/icon/${md5}.png`" alt="APP图标" class="img-fluid"
                           style="object-fit: cover; max-width: 100%; max-height: 100%; border-radius: 10px;">
                    </div>
                  </div>
                </div>


                <div class="row" style="width: 78%; height: 100%">
                  <div class="col-12 file-info mt-2">
                    <ul ref="file_text" class="list-unstyled" style="max-height: 100%; overflow-y: auto">
                      <li><span class="info-label">文件名</span> <span class="info-value">{{
                          apk_data?.Package_Name
                        }}</span></li>
                      <li><span class="info-label">文件大小</span> <span class="info-value">{{ apk_data?.size }}</span>
                      </li>
                      <li><span class="info-label">MD5值</span> <span class="info-value">{{ apk_data?.MD5 }}</span></li>
                      <li><span class="info-label">SHA1值</span> <span class="info-value">{{
                          apk_data?.Cert_SHA1
                        }}</span></li>
                      <li><span class="info-label">SHA256值</span> <span class="info-value">{{
                          apk_data?.Cert_SHA256
                        }}</span></li>
                      <li><span class="info-label">包名</span> <span class="info-value">{{
                          apk_data?.Package_Name
                        }}</span></li>
                      <li><span class="info-label">主活动Activity</span> <span
                          class="info-value">{{ apk_data?.Main_Activity }}</span></li>
                      <!--                    <li><span class="info-label">证书机构</span> <span class="info-value">{{ apk_data?.Cert_Subject }}</span></li>-->
                      <li><span class="info-label">证书哈希算法</span> <span
                          class="info-value">{{ apk_data?.Cert_Hash_Algo }}</span></li>
                      <li><span class="info-label">证书签名算法</span> <span
                          class="info-value">{{ apk_data?.Cert_Signature_Algo }}</span></li>
                      <li><span class="info-label">证书序列号</span> <span
                          class="info-value">{{ apk_data?.Cert_Serial_Number }}</span></li>
                    </ul>
                  </div>
                </div>


              </div>
            </div>
          </div>
          <!--        权限         -->
          <div class="card mb-4" style="height: 35%">
            <div class="card-body" style="height:100%; padding-top: 1.2rem; padding-right: 0px;">
              <div class="row visual_info" style="height: 100%">
                <div class="col-lg-12 col-md-12 text-nowrap" style="height: 100%; padding-right: 0px">
                  <div class="row flex-wrap align-items-center ip_header">
                    <i class='bx bxs-chip bx-sm ip_icon' style="color: #566a7f"></i>
                    <span class="fw-bolder fs-5 mx-2 ip_title" style="width: 30%">权限控制</span>
                    <div class="ml-auto" style="flex: 1;"></div> <!-- 空白的自动增长的列 -->
                    <div class="risk-summary text-end" style="width: 25%;">
                      <div v-if="risk_counts['2'] > 0" style="margin-right: 15px">
                        <img src="/src/assets/risk-high.svg" class="risk-icon"> {{ risk_counts['2'] }}
                      </div>
                      <div v-if="risk_counts['1'] > 0">
                        <img src="/src/assets/risk-low.svg" class="risk-icon"> {{ risk_counts['1'] }}
                      </div>
                    </div>
                  </div>
                  <div class="list-container mt-3" ref="perm_content">
                    <div v-for="(item, index) in permissions" :key="index" class="risk-item">
                      <div class="risk-content">
                        <div class="risk-header">
                          <img :src="getRiskIcon(item.risk)" class="risk-icon">
                          该APP使用
                          <!--                        <span class="risk-attribute" style="background-color: rgba(96,91,255,0.1)">-->
                          <span class="risk-attribute" style="background-color: rgb(86, 106, 127); color: white;">

                          {{ item.name }} </span>
                          权限
                          <span :style="{ color: getRiskColor(item.risk) }" style="font-weight:bold"> {{
                              item.value
                            }} </span>。
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
          </div>



          <!--        指标         -->
          <div class="card mb-4" style="height: 30.4%">
            <div class="card-body">
              <div class="row flex-wrap align-items-center ip_header">
                <i class='bx bxs-bar-chart-alt-2 bx-sm ip_icon' style="color: #566a7f"></i>
                <span class="fw-bolder fs-5 mx-2 ip_title">观测指标</span>
              </div>

              <div class="" style="">
                <off_prob></off_prob>
              </div>
            </div>
          </div>


        </div>


        <div class="col-lg-6 col-md-6 mb-4" style="height: 100%;">

          <!--        APP检测报告         -->
          <div class="card mb-4" style="height:100%; min-height: 0px">
            <h5 class="card-header d-flex justify-content-between align-items-center">
              <div>
                <i class='bx bx-sm bxs-book-content ip_icon'></i>
                <span class="text-dark fw-bolder mx-4">
                {{ apk_data.App_Name }} APP检测报告
              </span>
              </div>
              <div class="text-end">
                <span class="text-dark fw-bolder "></span>
                <i class="bx bx-sm bx-download ip_icon mx-2" style="cursor: pointer;"></i> <!-- 根据需要选择合适的下载图标 -->
              </div>
            </h5>
            <div ref="report_content" class="report card-body mb-3 pt-0"
                 style="overflow-y: auto;height: 92%; max-height: 92%;min-height: 0px">
              <transition name="fade">
                <div class="loader-container" v-if="isloading">
                  <div class="loader-bar"></div>
                </div>
              </transition>
              <h4 v-if="!isloading" class="eachh-title">一、权限分析（Permission Analysis）</h4>
              <div class="parent-class" v-html="parsedMarkdown1" id="report1"></div>
              <h4 v-if="!isloading" class="eachh-title">二、活动分析（Activity Analysis）</h4>
              <div class="parent-class" v-html="parsedMarkdown2" id="report2"></div>
              <h4 v-if="!isloading" class="eachh-title">三、证书分析（Certificate Analysis）</h4>
              <div class="parent-class" v-html="parsedMarkdown3" id="report3"></div>
              <h4 v-if="!isloading" class="eachh-title">四、总结（Summary）</h4>
              <div class="parent-class" v-html="parsedMarkdown4" id="report4"></div>
              <h4 v-if="!isloading" class="eachh-title">五、局限性（Limitations）</h4>
              <div class="parent-class" v-html="parsedMarkdown5" id="report5"></div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>


</template>

<style scoped>
@import "/assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.css";

td {
  max-width: 30px;
  overflow-x: auto;
}

.ip_header {
  text-align: left;
  height: 34px;
}

.logo-img {
  display: flex;
  height: 70%;
}

.logo_info {
  width: 100%;
  height: 40%;
  display: flex;
  flex-direction: column;
}

.visual_info {
  width: 100%;
  height: 60%;
}

.ipMap {
  width: 100%;
  height: 100%;
  padding-bottom: 0px;
}

.ip_icon {
  width: 5%;
}

.ip_title {
  width: 60%;
}

.report {
  height: 60%;
  width: 100%;
}

.file-info {
  height: 100%;

}

.risk-summary {
  /*margin-left: 20px;*/
  display: flex;
  align-items: center;
  justify-content: start; /* 从容器的起始位置排列 */
  /*margin-top: 3px;*/
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

.risk-attribute {
  display: flex;
  padding-left: 2px;
  padding-right: 2px;
  border-radius: 4px;

}

.risk-explanation {
  margin-top: 4px;
  font-size: 0.8em;
  font-weight: 200;
}

.list-container {
  height: 85%;
  overflow-y: auto;
  margin-top: 5px;
  margin-left: 20px;
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
  /*background-color: white;
  border: 1px solid #ccc;*/
  border-radius: 2px;
  overflow: hidden; /* 隐藏超出容器部分的加载条 */
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


.parent-class > h1 {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  /* 其他样式 */
}

.parent-class > h2 {
  font-size: 10px !important;
  font-weight: bold;
  color: #555;
  /* 其他样式 */
}

.parent-class h3 {
  font-size: 10px !important;
  font-weight: bold;
  color: #777;
  /* 其他样式 */
}

.info-label {
  font-size: 12px;
  font-weight: bold;
  color: #ffffff;
  margin-right: 10px;
  background-color: rgb(86, 106, 127);
  padding: 2px;
  border-radius: 4px;
}

.info-value {
  color: #666;
  word-wrap: break-word; /* 在单词内部换行 */
  word-break: break-all;
}

/* 使用 :deep() 选择器来改变 v-html 内容的样式 */
:deep(.parent-class h1) {
  font-size: 1.75em;
}

:deep(.parent-class h2) {
  font-size: 1.5em;
}

:deep(.parent-class h3) {
  font-size: 1.25em;
}

:deep(.parent-class h4) {
  font-size: 1.25em;
}

:deep(.parent-class h5) {
  font-size: 1em;
}

:deep(.parent-class h6) {
  font-size: 0.875em;
}

.eachh-title {
  font-weight: bold;
}

.pack_bar {
  max-width: 90px;
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
