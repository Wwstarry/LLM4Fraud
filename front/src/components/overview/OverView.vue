<script setup>
import {ref, onMounted, onUnmounted, computed} from 'vue';
import PerfectScrollbar from 'perfect-scrollbar';
import IpTracking from "@/components/map/ipTracking.vue";
import { API_BASE_URL } from "@/api/config.js";
import indexMap from "@/components/map/indexMap.vue";
import graph from "@/components/map/graph.vue";
import axios from 'axios';
import * as echarts from 'echarts';


const user = {
  UFacePath: 'path/to/user/image',
  Uname: 'User Name',
  Uposition: 'User Position'
};

const monthFixCount = ref(0);
const monthFixIncreasePercentage = ref(0);
const monthVulCount = ref(0);
const monthVulIncreasePercentage = ref(0);
const fixIncreasePercentage = ref(0);
const distinctDaysCount = ref(0);
const totalVulCount = ref(0);
const gambleCount = ref(0);
const sexCount = ref(0);
const scamCount = ref(0);
const otherCount = ref(0);
const userProjects = ref([]);
const Vul_num = ref([]);
const monthlyVuls = ref([]);
const recentSixDaysFixes = ref([]);
let whiteIndustryPercentage = ref(0);
const graphData = ref({});

const totalRevenueChart = ref(null);
let incomeChart = null;
let profileReportChart = null;
let statisticsChart = null;

let cardColor, headingColor, axisColor, shadeColor, borderColor;

cardColor = config.colors.white;
headingColor = config.colors.headingColor;
axisColor = config.colors.axisColor;
borderColor = config.colors.borderColor;
const filteredLinks = ref([]);
const revenueData = ref([]);

const fetchData = async () => {
  try {
    const response = await axios.get('/home/index');
    // monthFixCount.value = response.data.monthFixCount;
    monthVulIncreasePercentage.value = response.data.monthFixIncreasePercentage;
    // monthVulCount.value = response.data.monthVulCount;
    monthFixIncreasePercentage.value = response.data.monthVulIncreasePercentage;

    otherCount.value = response.data.otherCount;
    sexCount.value = response.data.sexCount;
    gambleCount.value = response.data.gambleCount;
    scamCount.value = response.data.scamCount;
    graphData.value = response.data.graphData;

    // 排序 userProjects 根据 Pdanger
    userProjects.value = response.data.userProjects
        .map(project => ({
          Pname: project.Pname,
          Pdanger: project.Pdanger,
          MD5: project.MD5,
        }))
        .sort((a, b) => b.Pdanger - a.Pdanger);

    // 排序 graphData.links 根据 weight
    graphData.value.links = response.data.graphData.links.sort((a, b) => b.weight - a.weight);
    filteredLinks.value = graphData.value.links;

    Vul_num.value = response.data.highRisk.map(v => ({
      date: v.date,
      total_vul: v.total_vul,
      total_fix: v.total_fix,
    }));

    whiteIndustryPercentage.value = response.data.whiteIndustryPercentage;
    totalVulCount.value = gambleCount.value + sexCount.value + scamCount.value + otherCount.value;

    const res = await axios.get('/home/revenue');
    revenueData.value = res.data;

    const res2 = await axios.get('/home/sum_count');
    monthFixCount.value = res2.data.res_one_count;
    monthVulCount.value = res2.data.prob_not_zero_count;

  } catch (error) {
    console.error('Error fetching data:', error);
  }

  fixIncreasePercentage.value = 10;
  distinctDaysCount.value = 15;
};


const getIconUrl = (name) => {
  const node = graphData.value.nodes.find(node => node.id === name);
  // console.log(name)
  // console.log(node.id)
  // console.log(111,graphData.value)
  // console.log(node.md5)
  const icon = node ? `${API_BASE_URL}/icon/${node.md5}.png` : '';
  // console.log(icon)
  return icon
};

function findNodesUpdate(md5) {
  if (md5 === null){
    filteredLinks.value = graphData.value.links;
  } else {
    const target = graphData.value.nodes.find(node => node.md5 === md5).id;
    filteredLinks.value = graphData.value.links.filter(link => link.source === target || link.target === target);
  }
}


const app_totalbar = ref('');

// -------------------- 密度图 --------------------
const densityChart = ref(null);
const binEdges = ref([]);
const density = ref([]);

async function createDensityChart() {
  const chart = echarts.init(densityChart.value);
  await axios.get('/home/density').then(res => {
    binEdges.value = res.data.bin_edges;
    density.value= res.data.density;
  });

  // 准备图表数据
  const xAxisData = binEdges.value.map((edge, index) => {
    if (index === binEdges.value.length - 1) {
      return `${edge}+`;
    } else {
      return `${binEdges.value[index+1]}`;
    }
  });

  const seriesDataAll = density.value.all_apps;
  const seriesDataBlacklisted = density.value.blacklisted_apps;

  const option = {
    // title: {
      // text: 'APP大小密度分布图',
      // left: 'center'
    // },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const dataIndex = params[0].dataIndex; // 假设获取第一个系列的数据索引
        const seriesName1 = params[0].seriesName; // 获取系列名称
        const seriesName2 = params[1].seriesName; // 获取系列名称
        const yValue1 = params[0].value;
        const yValue2 = params[1].value;
        const edgeStart = xAxisData[dataIndex];
        const edgeEnd = xAxisData[dataIndex + 1];
        const originalMark1 = params[0].marker; // 获取原来的标记
        const originalMark2 = params[1].marker;
        return `${edgeStart} MB - ${edgeEnd} MB <br/> <div style="margin-top: 8px"> ${originalMark1} ${seriesName1}: ${yValue1}
 <br/> ${originalMark2} ${seriesName2}: ${yValue2} </div>`;
      },
      // extraCssText: 'display: none;',
    },
    legend: {
      data: ['Fraud', 'Scam'],
      top: 5,
    },
    grid:{
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      name: 'Size',
      type: 'category',
      data: xAxisData,
      axisLabel: {
        rotate: 0,
        interval: 2
      },
      nameLocation: 'end',
      nameTextStyle: {
        align: 'right',
        verticalAlign: 'bottom',
      },

    },
    yAxis: {
      name: 'APP Number',
      type: 'value',
      // splitLine: {
      //   show: false,
      // }
    },
    series: [

      {
        name: '黑名单数',
        type: 'bar',
        data: seriesDataBlacklisted,
        itemStyle: {
          borderRadius: [5, 5, 0, 0]  // 圆角设置，数组分别对应左上、右上、右下、左下的圆角半径
        }
      },
      {
        name: '已检测数',
        type: 'bar',
        data: seriesDataAll,
        itemStyle: {
          borderRadius: [5, 5, 0, 0]  // 圆角设置，数组分别对应左上、右上、右下、左下的圆角半径
        }
      },
     
    ],
    color: ['#8592a3', '#696cff',],
  };

  // 使用指定的配置显示图表
  chart.setOption(option);
}

const fitDensity = (binEdges, data) => {
  // const totalCount = data.reduce((acc, curr) => acc + curr, 0);
  // const density = data.map(count => count / totalCount);
  return data;
};

// --------------  选择风险APP --------------
const selectedProject = ref(null);
function selectProject(project){
  if (selectedProject.value === project) {
    // 如果重复点击同一个项目，则取消选中
    selectedProject.value = null;
  } else {
    // 否则，选择新项目
    selectedProject.value = project;
  }
  totalRevenueChartOptions.value = {
    series: [
      {
        name: 'Final Risk',
        data: [selectedData.value.black, selectedData.value.gamble, selectedData.value.scam, selectedData.value.sex, selectedData.value.white]
      },
      {
        name: 'Icon Risk',
        data: [selectedData.value.icon_black, selectedData.value.icon_gamble, selectedData.value.icon_scam, selectedData.value.icon_sex, selectedData.value.icon_white]
      },
      {
        name: 'Content Risk',
        data: [selectedData.value.content_black, selectedData.value.content_gamble, selectedData.value.content_scam, selectedData.value.content_sex, selectedData.value.content_white]
      }
    ],
    chart: {
      height: 400,
      stacked: false,
      type: 'bar',
      toolbar: { show: false }
    },
    plotOptions: {
      bar: {
        horizontal: true,
        columnWidth: '33%',
        borderRadius: 12,
        startingShape: 'rounded',
        endingShape: 'rounded'
      }
    },
    colors: ['#696cff', '#6c757d', '#9da5b9'],
    dataLabels: { enabled: false },
    tooltip: {
      y: {
        formatter: val => Math.abs(val)
      }
    },
    stroke: {
      curve: 'smooth',
      width: 6,
      lineCap: 'round',
      colors: ['#fff']
    },
    legend: {
      show: true,
      horizontalAlign: 'left',
      position: 'top',
      markers: {
        height: 8,
        width: 8,
        radius: 12,
        offsetX: -3
      },
      labels: { colors: '#6c757d' },
      itemMargin: { horizontal: 10 }
    },
    grid: {
      borderColor: '#e7eaf3',
      padding: { top: 0, bottom: 0, left: 20, right: 20 }
    },
    labels: ['Blake', 'Gambling', 'Scam', 'Sex', 'White'],
    xaxis: {
      labels: {
        show: true,
        style: { fontSize: '13px', colors: '#6c757d' }
      },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: {
      labels: {
        type: 'category',
        style: { fontSize: '13px', colors: '#6c757d' },
        // formatter: val => Math.abs(val)
      }
    }
  };
  totalRevenueChart.value.updateOptions(totalRevenueChartOptions.value)

  findNodesUpdate(selectedProject.value);
}

const app_taokebar = ref(null);

// 使用 computed 计算属性来获取选定项目对应的特定数据项
let selectedData = computed(() => {
  if (!selectedProject.value) {
    // 如果 selectedProject.value 为空，则返回 revenueData 的第一项作为默认值
    return revenueData.value[0];
  } else {
    // 否则返回与 selectedProject.value 相匹配的数据项
    return revenueData.value.find(item => item.md5 === selectedProject.value);
  }
});

const totalRevenueChartOptions = ref({})
onMounted(async () => {
  await fetchData();

  const app_totalscrollbar = new PerfectScrollbar(app_totalbar.value, {
    wheelSpeed: 0.5,
    wheelPropagation: false,
    minScrollbarLength: 20
  });

  const app_taokescrollbar = new PerfectScrollbar(app_taokebar.value, {
    wheelSpeed: 0.5,
    wheelPropagation: false,
    minScrollbarLength: 20
  });

  totalRevenueChartOptions.value = {
    series: [
      {
        name: 'Final Risk',
        data: [selectedData.value.black, selectedData.value.gamble, selectedData.value.scam, selectedData.value.sex, selectedData.value.white]
      },
      {
        name: 'Icon Risk',
        data: [selectedData.value.icon_black, selectedData.value.icon_gamble, selectedData.value.icon_scam, selectedData.value.icon_sex, selectedData.value.icon_white]
      },
      {
        name: 'Content Risk',
        data: [selectedData.value.content_black, selectedData.value.content_gamble, selectedData.value.content_scam, selectedData.value.content_sex, selectedData.value.content_white]
      }
    ],
    chart: {
      height: 400,
      stacked: false,
      type: 'bar',
      toolbar: { show: false }
    },
    plotOptions: {
      bar: {
        horizontal: true,
        columnWidth: '33%',
        borderRadius: 12,
        startingShape: 'rounded',
        endingShape: 'rounded'
      }
    },
    colors: ['#696cff', '#6c757d', '#9da5b9'],
    dataLabels: { enabled: false },
    tooltip: {
      y: {
        formatter: val => Math.abs(val)
      }
    },
    stroke: {
      curve: 'smooth',
      width: 6,
      lineCap: 'round',
      colors: ['#fff']
    },
    legend: {
      show: true,
      horizontalAlign: 'left',
      position: 'top',
      markers: {
        height: 8,
        width: 8,
        radius: 12,
        offsetX: -3
      },
      labels: { colors: '#6c757d' },
      itemMargin: { horizontal: 10 }
    },
    grid: {
      borderColor: '#e7eaf3',
      padding: { top: 0, bottom: 0, left: 20, right: 20 }
    },
    labels: ['Blake', 'Gambling', 'Scam', 'Sex', 'White'],
    xaxis: {
      labels: {
        show: true,
        style: { fontSize: '13px', colors: '#6c757d' }
      },
      axisTicks: { show: false },
      axisBorder: { show: false }
    },
    yaxis: {
      labels: {
        type: 'category',
        style: { fontSize: '13px', colors: '#6c757d' },
        // formatter: val => Math.abs(val)
      }
    }
  };

  const totalRevenueChartEl = document.querySelector('#totalRevenueChart');
  if (totalRevenueChartEl) {
    if (totalRevenueChart.value) totalRevenueChart.value.destroy();
    totalRevenueChart.value = new ApexCharts(totalRevenueChartEl, totalRevenueChartOptions.value);
    totalRevenueChart.value.render();
  }

  const incomeChartOptions = {
    series: [{ name: 'vul', data: monthlyVuls.value }],
    chart: {
      height: 315,
      parentHeightOffset: 0,
      parentWidthOffset: 0,
      toolbar: { show: true },
      type: 'area'
    },
    dataLabels: { enabled: false },
    stroke: { width: 2, curve: 'smooth' },
    legend: { show: false },
    markers: {
      size: 6,
      colors: 'transparent',
      strokeColors: 'transparent',
      strokeWidth: 4,
      discrete: [
        {
          fillColor: '#fff',
          seriesIndex: 0,
          dataPointIndex: 7,
          strokeColor: '#696cff',
          strokeWidth: 2,
          size: 6,
          radius: 8
        }
      ],
      hover: { size: 7 }
    },
    colors: ['#696cff'],
    fill: {
      type: 'gradient',
      gradient: {
        shade: 'light',
        shadeIntensity: 0.6,
        opacityFrom: 0.5,
        opacityTo: 0.25,
        stops: [0, 95, 100]
      }
    },
    grid: {
      borderColor: '#e7eaf3',
      strokeDashArray: 3,
      padding: { top: -20, bottom: -8, left: 8, right: 8 }
    },
    xaxis: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      axisBorder: { show: false },
      axisTicks: { show: false },
      labels: {
        show: true,
        style: { fontSize: '13px', colors: '#6c757d' }
      }
    },
    yaxis: {
      labels: { show: false },
      min: 10,
      max: 50,
      tickAmount: 4
    }
  };

  const incomeChartEl = document.querySelector('#incomeChart');
  if (incomeChartEl) {
    if (incomeChart) incomeChart.destroy();
    incomeChart = new ApexCharts(incomeChartEl, incomeChartOptions);
    incomeChart.render();
  }

  const profileReportChartOptions = {
    chart: {
      height: 80,
      type: 'line',
      toolbar: { show: false },
      dropShadow: {
        enabled: true,
        top: 10,
        left: 5,
        blur: 3,
        color: '#ffc107',
        opacity: 0.15
      },
      sparkline: { enabled: true }
    },
    grid: {
      show: false,
      padding: { right: 8 }
    },
    colors: ['#ffc107'],
    dataLabels: { enabled: false },
    stroke: { width: 5, curve: 'smooth' },
    series: [{ name: 'Fixes', data: recentSixDaysFixes.value }],
    xaxis: {
      show: false,
      lines: { show: false },
      labels: { show: false },
      axisBorder: { show: false }
    },
    yaxis: { show: false }
  };

  const profileReportChartEl = document.querySelector('#profileReportChart');
  if (profileReportChartEl) {
    if (profileReportChart) profileReportChart.destroy();
    profileReportChart = new ApexCharts(profileReportChartEl, profileReportChartOptions);
    profileReportChart.render();
  }

  const chartOrderStatistics = document.querySelector('#orderStatisticsChart'),
    orderChartConfig = {
      chart: {
        height: 165,
        width: 130,
        type: 'donut'
      },
      labels: ['Gambling', 'Sex', 'Scam', 'Other Fraudulent'],
      series: [gambleCount.value, sexCount.value, scamCount.value, otherCount.value],
      colors: [config.colors.primary, config.colors.success, config.colors.info, config.colors.secondary],
      stroke: {
        width: 5,
        colors: cardColor
      },
      dataLabels: {
        enabled: false,
        formatter: function (val, opt) {
          return parseInt(val) + '%';
        }
      },
      legend: {
        show: false
      },
      grid: {
        padding: {
          top: 0,
          bottom: 0,
          right: 15
        }
      },
      plotOptions: {
        pie: {
          donut: {
            size: '75%',
            labels: {
              show: true,
              value: {
                fontSize: '1.5rem',
                fontFamily: 'Public Sans',
                color: headingColor,
                offsetY: -15,
                formatter: function (val) {
                  return parseInt(val) + '%';
                }
              },
              name: {
                offsetY: 20,
                fontFamily: 'Public Sans'
              },
              total: {
                show: true,
                fontSize: '0.8125rem',
                color: axisColor,
                label: '白色产业占比',
                formatter: function (w) {
                  return `${whiteIndustryPercentage.value}%`;
                }
              }
            }
          }
        }
      }
    };

  if (typeof chartOrderStatistics !== undefined && chartOrderStatistics !== null) {
    statisticsChart = new ApexCharts(chartOrderStatistics, orderChartConfig);
    statisticsChart.render();
  }

  await createDensityChart();
});

onUnmounted(() => {
  if (totalRevenueChart.value) totalRevenueChart.value.destroy();
  if (incomeChart) incomeChart.destroy();
  if (profileReportChart) profileReportChart.destroy();
  if (statisticsChart) statisticsChart.destroy();
});
</script>



<template>
  <div class="container-xxl flex-grow-1 container-p-y" style="">


    <div class="row">

      <div class="col-12 col-lg-8 order-2 order-md-3 order-lg-2 mb-4">
        <div class="card">
          <div class="row row-bordered g-0">
            <div class="col-md-12">
              <h5 class="card-header m-0 me-2 pb-3">Risk IP Distribution</h5>
                          
              <div class="" style="height: 325px">
            <indexMap></indexMap>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 第三个卡片列 -->
      <div class="col-12 col-md-8 col-lg-4 order-3 order-md-2">
        <div class="row">
          <div class="col-6 mb-4">
            <div class="card">
              <div class="card-body">
                <div class="card-title d-flex align-items-start justify-content-between">
                  <div class="avatar flex-shrink-0">
                    <img
                        src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAAXNSR0IArs4c6QAABFpJREFUaEPtmVnIVVUUx38mFpUKYiXlgIlDkkGpD+JAk1GGODaYkqQPDpmo4ICamPkQ9BAoVkRpzmlWJkKm6INhpmj5oDg+OKKWZhYmQpDuf+xjm9M+5+x97v3oCt+Cjw/uXeu/13+vtddae98G3OLS4Bb3n3oC/3cEK41AX2Ao0B1oDtwDNAF+Bi4CZ4BvgDXAL3VBtgwBOTjDOPQ60CzCqa3ATGBvhE2haiwBOT3P7nQheIbCemAKcLIsgGsXSuAuYB3wfDUWBX4zkegP7KwUL4TA/cBm4JGcHf0cOAictbn/INAKeA54EeiQYTsKWFoJiSICd9hd6ppa5FeT/wuAhSYdfg9w4GlgDvB4Svdv4EnguwAMr0oRgVXA8JSlwj4AEIlY0Y5/DDR0DC8BjwGnYsGkn0fgZVv+XNzVwIgyCzk2TwHbUhjfA73L4GYRaAQcN7vV0gHdDjwD/FVmoZSNescXqc8GA1/HYmcRUJl7zwG7DOhg6n+15APT8MY7YEdMxB+KBc8ioBrdxgF7y9b/WPw8fVW3E8DtjpKqlipesPgI6ED95CBcBVoAV4JRwxUXm8M72lH/0Hb4YAQfgfnAmw6COueQYMQ4Re34JsfkHPBADISPgIavfg7ISGBFDGik7p+AOn0iSt3ToRg+AvtMNXjUAegJ/BAKWEJP6aq0TaQPsCMUx0dA44AOWCKdTDM7GgpYQm+DbYyJqRrnZ6E4PgKa4zXbJ9K2WpNjhlPLAKVpIm8A71dCYL9pMl0cgB7mTOwOBSyht8U2yMT0Fc8EkAnri8C3JuefdSwGmRxVmOtKDphR/WEHXLe89KgRReAjMxaPcSw0dU6uI+/vs9dPF17n73zoer4IaMdV+xOJrs2hi9tRQiNFIoeBzhH23mn0TjvzuC2+1KBV4IhGajnc3tETmQmVEpC9XhE0TidyDOgYAxygq/t1utrodePHANubKlnDnGq/roi3OWC6fU2KAc/RVZrsAe52dDTEabSIkrwLTfowCziqRmd4ojvGLntndlVESikVJXkENIGqJ9ybQnwHmBW1yr/K3YCNqU6vb0uP60V34l4Zc4nCPc7O86Fcppmh7d0M5RfMq8eXoUCuXhEB6erW5JY6117RWJ4T+qbAQDueFxWBUg0zhIAc1kV+Zc4OHTJVS3/qGX/Y/G4NPBG5q9GRCCUgPzQTfeXJ30gfuWYeBmbbDuzblGGmma0NBY0hIEw1uanAdKBx6CKOnvqLHnh1F86LrCKuJ5xCiSWQAOoZ/SVAh1xpkncN1Gu0RpNPbYqlnXrVnqP050E3wbIE0otpKNMh1bOIyq5+C9BvA7ptXSjcRtCL3RKPXuHbabUIBPhYqKLXiU9Sr4XXTbq9lhGhfwBriYD8EQk9tbgiEmPtm+p/dqHWCMhBX9+ZaH5UWeSLYS0SSJOYa4bKt7MSsFYJJCTaARpBMqWWCRSe+lo8xEFOu0r1EYjesiob1EegyhsaDXcDOg+jMYo5z68AAAAASUVORK5CYII="/>
                  </div>
                </div>
                <span class="fw-semibold d-block mb-1">Identified Fruad</span>
                <h3 class="card-title text-nowrap mb-2">{{ monthFixCount }}</h3>
                <small v-if="monthFixIncreasePercentage >= 0" class="text-danger fw-semibold">
                  <i class="bx bx-up-arrow-alt"></i>{{ monthFixIncreasePercentage }}
                </small>
                <small v-else class="text-success fw-semibold">
                  <i class="bx bx-down-arrow-alt"></i>{{ monthFixIncreasePercentage }}
                </small>
              </div>
            </div>
          </div>

          <!-- 第一个卡片列 -->
          <div class="col-6 mb-4">
            <div class="card">
              <div class="card-body">
                <div class="card-title d-flex align-items-start justify-content-between">
                  <div class="avatar flex-shrink-0">
                    <img
                        src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAAXNSR0IArs4c6QAAA91JREFUaEPtmEnIjlEUx39fNmYhImRlylAslDJGxqKEyJCpkKKEpMhKCbFjY0iIxEIpU6aF2FAyzwsW5ijTiuev+9Tjeu5z7zP4Xp++u3l7n3vuuf//Oeeee8+po4GPugaOn0YCtfZgowf+Rw+0BJYC2+qD3N8IoY3AaqA78MFDohUg+SlAN+AhsB/YEUq+SgLjgANAx8Tm5w24LymAOgGXgF4pcxeAScA3H5EqCWgvhc4us+kjYCjw2gH+CtAjA2AQibwEWgODjOXS9p4InDKgXxpZW06W94GP15wGJmR5IS+BzUbhQIfSTcAN4DKwF1gCvE3IKrwUNn2s9XeA5cAxoIM1p28zXCTyEBgGnAWaAquiQ7cn+v1kKW4GfE18awF8Nv+zwI+KCLwB+gMXgfaWXh3yk2kkQgjMNYczbf1RYKbvoBmryiu25e9GHhlpwMdqBhgvtU3o3QqsLUpA66ab9NY8oUSpTp7wDYVEGniFTWx5W8dxYGrio8JxURkCWnsdGJxQosP4yoNeYSPwvS25e1GojLAsH4soNBda8suA3WUItAPeAcos94HRwJwoDR7KICDLK9vY4GV5hU3ycMdqZOkFls7b5mykbhVyBrRQcT4EWG8OpTZRJlrhIOAC/8DcDTZ44dANPM/S9wJQ8njuMlQoAcW+fZumfdM+rpjX3DpgSwoY3eBKFskhb+sidIKXcCgB30GN512Wj+d/AIvNHRHvfzglk3ktHyuskoAPfNIIOj8CXgp8lR7IChuX95SdlIlyh01yQRUeyGP5rFAMDpsqCdQUfNkQqjn4MgT+CfBFCQi8Xox9Q3OrQy4rz4+J7gBVc96R9xDXh+VVpd0yNXLac+M3UnkI1Ad4gdsX3b7zTVdjjc8FoQSK5Pm0vZUqhwPPrEnpVxGjTobKSA09XVRO6sWrh2SqN0II/G3LqyuheO+aYW09AnUuZIBcIaSS8BrQz+dKz7wOrCz/1CGn2uIMoGrMHlcBNQs+pq31eUBFhArzMkNW05PBBT7WrSbXE6uof+xpvXhfo4o9FTNFR57nQRvTyUsa9XvUpdN3/aYOnwf0/C06fGFj651lXqfywnZgA9AZGAucK0pAFuxSgEEey8fqVZG9N1WfWooKKTUO1LpxNg98HlgJ7MxJIK/lY/U9TXPX3s71/Zecj4BkDgKzA0kUBR+o/k+xEAJNos7CEWCaZ5ciYVMYeLwwhIBkReJE1Pec7NixJuBDQyiJOS2clKvHmxxe2qJ5FYR6IKlXPSFd62q13zRtkriBm3f/0vJFCJTetEoFjQSqtGYRXY0eKGK1Ktc0eA/8BGfmxDFooh7qAAAAAElFTkSuQmCC"/>
                  </div>
                </div>
                <span class="fw-semibold d-block mb-1">Total Scanned</span>
                <h3 class="card-title mb-2">{{ monthVulCount }}</h3>
                <small v-if="monthVulIncreasePercentage >= 0" class="text-danger fw-semibold">
                  <i class="bx bx-up-arrow-alt"></i>{{ monthVulIncreasePercentage }}
                </small>
                <small v-else class="text-success fw-semibold">
                  <i class="bx bx-down-arrow-alt"></i>{{ monthVulIncreasePercentage }}
                </small>
              </div>
            </div>
          </div>


          <!--          tips-->
          <div class="col-12 mb-4 w-100 h-100">
            <div class="card w-100" style="height: 174px">
                <div class="d-flex flex-sm-row flex-column gap-3 w-100 h-100 p-2">
                  <div class="w-100" ref="densityChart" ></div>
                </div>


            </div>
          </div>

        </div>
      </div>
    </div>



    <div class="row">
      <div class="col-md-6 col-lg-4 col-xl-4 order-0 mb-4">
        <div class="card h-100">
          <div class="card-header d-flex align-items-center justify-content-between pb-0">
            <div class="card-title mb-0">
              <h5 class="m-0 me-2">Fraudulent APP Distribution</h5>
            </div>
          </div>
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div class="d-flex flex-column align-items-center gap-1">
                <h2 class="mb-2">{{ totalVulCount }}</h2>
                <span>Total</span>
              </div>
              <div id="orderStatisticsChart"></div>
            </div>
            <ul class="p-0 m-0">
              <li class="d-flex mb-4 pb-1">
                <div class="avatar flex-shrink-0 me-3">
                  <span class="avatar-initial rounded bg-label-primary"><i class="bx bx-mobile-alt"></i></span>
                </div>
                <div class="d-flex w-100 flex-wrap align-items-center justify-content-between gap-2">
                  <div class="me-2">
                    <h6 class="mb-0">Gambling</h6>
                    <small class="text-muted"></small>
                  </div>
                  <div class="user-progress">
                    <small class="fw-semibold">{{gambleCount}}</small>
                  </div>
                </div>
              </li>
              <li class="d-flex mb-4 pb-1">
                <div class="avatar flex-shrink-0 me-3">
                  <span class="avatar-initial rounded bg-label-success"><i class="bx bx-closet"></i></span>
                </div>
                <div class="d-flex w-100 flex-wrap align-items-center justify-content-between gap-2">
                  <div class="me-2">
                    <h6 class="mb-0">Sex</h6>
                    <small class="text-muted"></small>
                  </div>
                  <div class="user-progress">
                    <small class="fw-semibold">{{sexCount}}</small>
                  </div>
                </div>
              </li>
              <li class="d-flex mb-4 pb-1">
                <div class="avatar flex-shrink-0 me-3">
                  <span class="avatar-initial rounded bg-label-info"><i class="bx bx-home-alt"></i></span>
                </div>
                <div class="d-flex w-100 flex-wrap align-items-center justify-content-between gap-2">
                  <div class="me-2">
                    <h6 class="mb-0">Scam</h6>
                    <small class="text-muted"></small>
                  </div>
                  <div class="user-progress">
                    <small class="fw-semibold">{{scamCount}}</small>
                  </div>
                </div>
              </li>
              <li class="d-flex">
                <div class="avatar flex-shrink-0 me-3">
                  <span class="avatar-initial rounded bg-label-secondary"><i class="bx bx-football"></i></span>
                </div>
                <div class="d-flex w-100 flex-wrap align-items-center justify-content-between gap-2">
                  <div class="me-2">
                    <h6 class="mb-0">Other Fraudulent</h6>
                    <small class="text-muted"></small>
                  </div>
                  <div class="user-progress">
                    <small class="fw-semibold">{{otherCount}}</small>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-4 order-2 mb-4">
        <div class="card h-100">
          <div class="card-header d-flex align-items-center justify-content-between">
            <h5 class="card-title m-0 me-2">Wrapper APP Analysis</h5>
          </div>
          <div ref="app_taokebar" class="card-body overflow-auto" id="vertical-example" style="max-height: 400px;">
            <ul class="list-unstyled m-0">
              <li v-for="link in filteredLinks" :key="link.source + '-' + link.target" class="mb-4 pb-1">
                <div class="row">
                  <div class="col-3 d-flex">
                    <div class="avatar flex-shrink-0 me-3">
                      <img :src="getIconUrl(link.source)" alt="Source Icon" class="rounded w-100"/>
                    </div>
                    <div class="avatar flex-shrink-0">
                      <img :src="getIconUrl(link.target)" alt="Target Icon" class="rounded w-100"/>
                    </div>
                  </div>
                  <div class="col-5 d-flex align-items-center">
                    <h6 class="mb-0">{{ link.source }} - {{ link.target }}</h6>
                  </div>
                  <div class="col-4 d-flex align-items-center justify-content-end">
                    <div class="user-progress d-flex align-items-center">
                      <h6 class="mb-0 me-2">Sim:</h6>
                      <span class="text-muted">{{ link.weight.toFixed(2) }}</span>
                    </div>
                  </div>
                </div>
              </li>
            </ul>

          </div>
        </div>
      </div>

      <div class="col-md-6 col-lg-4 order-3 mb-4">
        <div class="card h-100">
          <div class="card-header d-flex align-items-center justify-content-between">
            <h5 class="card-title m-0 me-2">APP Risk</h5>
          </div>

          <div ref="app_totalbar" class="card-body overflow-auto" id="vertical-example" style="max-height: 400px;">
            <ul class="list-unstyled m-0">
              <li v-for="project in userProjects" :key="project.Pname" class="mb-4 pb-1" :class="{'selected': selectedProject === project.MD5}"
                  @click="selectProject(project.MD5)">
                <div class="row">
                  <div class="col-2">
                    <div class="avatar flex-shrink-0 me-3">
                      <img :src="`${API_BASE_URL}/icon/${project.MD5}.png`" alt="Risk Icon" class="rounded w-100"/>
                    </div>
                  </div>
                  <div class="col-5 d-flex align-items-center">
                    <div>
                      <h6 class="mb-0">{{ project.Pname }}</h6>
                    </div>
                  </div>
                  <div class="col-5 d-flex align-items-center justify-content-end">
                    <div class="user-progress d-flex align-items-center">
                      <h6 class="mb-0 me-2">Risk Rate:</h6>
                      <span class="text-muted">{{ project.Pdanger.toFixed(2) }}</span>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
          </div>

        </div>
      </div>
    </div>


    <!-- 第二行 -->
    <div class="row">
      <!-- 第二个卡片列 -->
      <div class="col-12 col-lg-8 order-1 order-md-3 order-lg-2 mb-4">
        <div class="card h-100">
          <div class="row row-bordered g-0">
            <div class="col-md-12">
              <h5 class="card-header m-0 me-2 pb-3">Similarity Analysis</h5>
              <div>
                <graph :md5="selectedProject"></graph>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6 col-lg-4 order-2 mb-4">
        <div class="card h-100">
          <h5 class="card-header m-0 me-2 pb-3">APP Risk Composition</h5>
          <div class="card-body px-0">
            <div id="totalRevenueChart" class="px-2" style="margin-left: auto; margin-right: auto; margin-top: auto;margin-bottom: auto;"></div>
          </div>
        </div>
      </div>


    </div>


    <!-- / Content -->
  </div>
</template>

<style scoped>
.selected {
  background-color: rgba(105, 108, 255, 0.16);
  border-radius: 5px;
  transition: background-color 0.3s ease; 

}
</style>
