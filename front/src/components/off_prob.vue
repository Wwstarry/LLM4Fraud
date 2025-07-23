<template>
  <div class="chart-info-container">
    <div class="chart-container">
      <div id="main666" class="chart"></div>
    </div>
    <div class="info-container">
      <ul>
        <li v-for="(item, index) in trafficWay" :key="item.name" class="info-item">
          <div class="item-text">
            <span class="item-name">{{ item.name }}：</span>
            <span class="item-value">{{ item.value.toFixed(2) }}</span>
            <div class="progress">
              <div class="progress-bar" :style="{ width: (item.value / totalValue * 100) + '%', backgroundColor: getColor(index) }"></div>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
import { useRoute } from 'vue-router';

export default {
  setup() {
    const trafficWay = ref([]);
    const colors = ["#ffaa00", "#5bd887", "#696DFF", "#4ad2ff", "#248ae0"]; // 对应的颜色数组
    const largestIndustry = ref("");
    const route = useRoute(); // 使用 useRoute 获取路由参数
    const md5 = route.params.md5;

    const getColor = (index) => {
      return colors[index % colors.length];
    };

    const totalValue = computed(() => {
      return trafficWay.value.reduce((sum, item) => sum + item.value, 0);
    });

    onMounted(() => {
      initChart();
    });

    const initChart = async () => {
      const myChart = echarts.init(document.getElementById("main666"));

      try {
        const response = await axios.get(`/report/info?md5=${md5}`);
        trafficWay.value = response.data.probability;

        // 找到数量最多的产业
        const maxItem = trafficWay.value.reduce((prev, current) => (prev.value > current.value) ? prev : current);
        largestIndustry.value = maxItem.name;

        // 构建饼图数据
        const data = trafficWay.value.flatMap((item, index) => ([
          {
            value: item.value,
            name: item.name,
            itemStyle: {
              borderWidth: 2,
              borderColor: colors[index],
            },
          },
          {
            value: 0.02, // 用于间隙
            name: '',
            itemStyle: {
              color: 'rgba(0,0,0,0)', // 完全透明
            },
          }
        ]));

        const option = {
          backgroundColor: "rgba(0,0,0,0)",
          color: colors,
          tooltip: {
            trigger: 'item',
            formatter: (params) => {
              let item = trafficWay.value.find(item => item.name === params.name);
              return `${item.name}: ${item.value.toFixed(1)}`;
            },
          },
          series: [
            {
              name: "白色产业占比",
              type: "pie",
              clockWise: false,
              radius: ['50%', '70%'],
              hoverAnimation: true,
              itemStyle: {
                borderWidth: 2,
                borderColor: '#fff',
              },
              data: data,
              label: {
                normal: {
                  position: 'center',
                  formatter: () => `${maxItem.value.toFixed(1)}\n${maxItem.name}`,
                  textStyle: {
                    fontSize: '16',
                    fontWeight: 'bold',
                    color: '#5E7185'

                  }
                }
              }
            },
          ],
        };

        myChart.setOption(option);
      } catch (error) {
        console.error('获取数据时出错:', error);
      }
    };

    return {
      trafficWay,
      getColor,
      largestIndustry,
      totalValue
    };
  },
};
</script>

<style scoped>
.chart-info-container {
  display: flex;
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.chart {
  width: 250px;
  height: 250px;
}

.info-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  font-weight: bold;
  width: 300px;
}

.info-container ul {
  list-style-type: none;
  padding: 0;
  margin: 0; /* 移除默认边距 */
}

.info-container li {
  margin: 10px 0; /* 减少行间距 */
  display: flex;
  align-items: center;
  font-size: 1.2rem; /* 放大字体 */
  font-weight: bold; /* 加粗字体 */
}

.info-item {
  width: 100%; /* 使每行占据整个宽度 */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.item-name {
  flex: 0 0 110px; /* 固定宽度，确保对齐 */
  text-align: left;
  font-weight: bold;
  color: #5E7185;
}

.item-value {
  flex: 0 0 50px; /* 固定宽度，确保对齐 */
  text-align: right;
  font-weight: bold; /* 加粗字体 */
  color: #5E7185;
}

.progress {
  width: 40%; /* 使进度条占用剩余空间 */
  height: 10px;
  background-color: #e9ecef;
  border-radius: 0.25rem;
  overflow: hidden;
  margin-left: 10px; /* 使进度条与文字之间有一定间距 */
}

.progress-bar {
  height: 100%;
  transition: width 0.6s ease;
}
</style>
