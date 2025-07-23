<script setup>
import {computed, onMounted, reactive, ref} from "vue";
import PerfectScrollbar from "perfect-scrollbar";
import axios from "axios";
import arrowDown from '@/assets/arrow-down.svg';
import arrowRight from '@/assets/arrow-right.svg';
import { saveAs } from 'file-saver';
import { Parser } from '@json2csv/plainjs';

// Fields for custom entry
const set_md5 = ref(''); // APK MD5
const set_name = ref(''); // APK Name
const set_pack = ref(''); // APK Package Name
const set_cate = ref(''); // APK Category
const set_size = ref(''); // APK Size
const categories = ref([
  { label: 'Gambling', value: 'gamble' },
  { label: 'Adult', value: 'sex' },
  { label: 'Fraud', value: 'scam' },
  { label: 'Other Illicit', value: 'black' },
  { label: 'Unknown', value: 'Unknown' },
  { label: 'Legitimate', value: 'white' },
]);

// Data arrays
const blackdata = ref([]);
const whitedata = ref([]);

// Dropdown button labels
const dropButtonText_1 = ref('Select');
const dropButtonText_2 = ref('Select');

// Filter inputs
const filterValue1 = ref('');
const filterValue2 = ref('');

// Filtered arrays
const filteredData1 = ref([...blackdata.value]);
const filteredData2 = ref([...whitedata.value]);

// Category map for API labels
const cate_map = {
  'white': 'Legitimate',
  'gamble': 'Gambling',
  'sex': 'Adult',
  'scam': 'Fraud',
  'black': 'Other Illicit',
  'Unknown': 'Unknown',
}

// Fetch blacklist/whitelist data
const fetchData = async () => {
  try {
    const response = await axios.get("/get_blackList"); // Replace with real endpoint
    const data = response.data;

    const mappedData = data.map(item => ({
      name: item.App_Name,
      category: item.Label === '-1' ? 'Unknown' : cate_map[item.Label],
      risk: item.prob === '未检测' ? 'Not Detected' : parseFloat(item.prob),
      version: item.Package_Name,
      size: item.size,
      blackList: item.blackList,
      md5: item.MD5,
    }));

    blackdata.value = mappedData.filter(item => item.blackList === 1);
    whitedata.value = mappedData.filter(item => item.blackList === 0);
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};

// Update dropdown label
const updateButtonText = (num, newText) => {
  if (num === null) return;
  if (num === 1) {
    dropButtonText_1.value = newText;
  } else {
    dropButtonText_2.value = newText;
  }
};

// Risk badge class
const riskClass = (risk) => {
  if (risk === 'Not Detected') return 'badge bg-secondary me-1';
  if (risk >= 0.8) return 'badge bg-danger me-1';
  if (risk >= 0.5) return 'badge bg-warning me-1';
  return 'badge bg-primary me-1';
};

// Move to whitelist
const moveToWhite = async (item) => {
  const index = blackdata.value.findIndex(d => d.md5 === item.md5);
  if (index === -1) { console.error('Item not found in blacklist'); return; }
  try {
    const res = await axios.post('/update_blackList', { md5: item.md5, blackList: 0 });
    if (res.status === 200) {
      blackdata.value.splice(index, 1);
      whitedata.value.push(item);
      filteredData1.value = [...blackdata.value];
      filteredData2.value = [...whitedata.value];
      selectWhite(); selectBlack();
    }
  } catch (err) {
    console.error('Error moving to whitelist:', err);
  }
};

// Move to blacklist
const moveToBlack = async (item) => {
  const index = whitedata.value.findIndex(d => d.md5 === item.md5);
  if (index === -1) { console.error('Item not found in whitelist'); return; }
  try {
    const res = await axios.post('/update_blackList', { md5: item.md5, blackList: 1 });
    if (res.status === 200) {
      whitedata.value.splice(index, 1);
      blackdata.value.push(item);
      filteredData1.value = [...blackdata.value];
      filteredData2.value = [...whitedata.value];
      selectWhite(); selectBlack();
    }
  } catch (err) {
    console.error('Error moving to blacklist:', err);
  }
};

// Add to blacklist
const addBlack = async () => {
  const postData = { md5: set_md5.value, name: set_name.value, pack: set_pack.value, cate: set_cate.value, size: set_size.value, blackList: 1 };
  try {
    await axios.post('/addBlack', postData);
    alert('Added to blacklist successfully!');
    set_md5.value = set_name.value = set_pack.value = set_cate.value = set_size.value = '';
  } catch (err) {
    console.error('Error adding to blacklist:', err);
    alert('Failed to add to blacklist.');
  }
};

// Add to whitelist
const addWhite = async () => {
  const postData = { md5: set_md5.value, name: set_name.value, pack: set_pack.value, cate: set_cate.value, size: set_size.value, blackList: 0 };
  try {
    await axios.post('/addBlack', postData);
    alert('Added to whitelist successfully!');
    set_md5.value = set_name.value = set_pack.value = set_cate.value = set_size.value = '';
  } catch (err) {
    console.error('Error adding to whitelist:', err);
    alert('Failed to add to whitelist.');
  }
};

// Generic filter
const selectData_ = (filteredData, filterValue, sourceData, dropButtonText) => {
  const text = filterValue.value.trim().toLowerCase();
  if (!text) return filteredData.value = [...sourceData.value];
  switch (dropButtonText.value) {
    case 'Name':    filteredData.value = sourceData.value.filter(i => i.name.toLowerCase().includes(text)); break;
    case 'Size':    filteredData.value = sourceData.value.filter(i => i.size.toLowerCase().includes(text)); break;
    case 'Category':filteredData.value = sourceData.value.filter(i => i.category.toLowerCase().includes(text)); break;
    case 'Risk':    filteredData.value = sourceData.value.filter(i => i.risk.toString().toLowerCase().includes(text)); break;
    default: filteredData.value = sourceData.value.filter(i => i.name.toLowerCase().includes(text)
      || i.size.toLowerCase().includes(text)
      || i.category.toLowerCase().includes(text)
      || i.risk.toString().toLowerCase().includes(text));
  }
};
const selectBlack = () => selectData_(filteredData1, filterValue1, blackdata, dropButtonText_1);
const selectWhite = () => selectData_(filteredData2, filterValue2, whitedata, dropButtonText_2);

// Export CSV
const exportToCsv = (tableData, isBlack) => {
  if (!tableData.length) return console.error('No data to export.');
  const fields = [
    { label: 'MD5', value: 'md5' },
    { label: 'App Name', value: 'name' },
    { label: 'Package', value: 'version' },
    { label: 'Size', value: 'size' },
    { label: 'Category', value: 'category' },
    { label: 'Risk', value: 'risk' },
    { label: 'Is Blacklist', value: 'blackList' },
  ];
  const parser = new Parser({ fields });
  const csv = parser.parse(tableData);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, isBlack ? 'blacklist.csv' : 'whitelist.csv');
};

// Data table scrollbars
onMounted(async () => {
  await fetchData();
  filteredData1.value = [...blackdata.value];
  filteredData2.value = [...whitedata.value];
  new PerfectScrollbar('#blackbar');
  new PerfectScrollbar('#whitebar');
});
</script>

<template>
  <div class="container-xxl flex-grow-1 container-p-x">
    <div class="row container-p-y" style="padding-bottom:0!important;">

      <!-- Blacklist Section -->
      <div class="col-md-6">
        <div class="card mb-4" style="height:700px;">
          <div class="d-flex" style="max-height:20%;">
            <h5 class="card-header">Blacklist Settings</h5>
            <div class="card-header d-flex align-items-center ms-auto">
              <div class="btn-group">
                <button class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown">{{ dropButtonText_1 }}</button>
                <ul class="dropdown-menu">
                  <li @click="updateButtonText(1,'Name')"><a class="dropdown-item">Name</a></li>
                  <li @click="updateButtonText(1,'Size')"><a class="dropdown-item">Size</a></li>
                  <li @click="updateButtonText(1,'Category')"><a class="dropdown-item">Category</a></li>
                  <li @click="updateButtonText(1,'Risk')"><a class="dropdown-item">Risk</a></li>
                </ul>
              </div>
              <input v-model="filterValue1" @keyup.enter="selectBlack" class="form-control mx-3" placeholder="Filter..." style="width:50%;">
              <button @click="selectBlack" class="btn btn-primary" style="width:20%">Filter</button>
            </div>
            <div class="d-flex align-items-center ms-auto px-2" @click="exportToCsv(blackdata,1)">
              <i class="bx bx-download" style="cursor:pointer;"></i>
            </div>
          </div>
          <div id="blackbar" class="card-body overflow-auto" style="padding:0!important;">
            <table class="table table-hover table-sm text-center">
              <thead>
                <tr>
                  <th>Name</th><th>Package</th><th>Size</th><th>Category</th>
                  <th>Risk <i @click="rankByRisk1" class="bx" :class="isUpArrow1 ? 'bxs-up-arrow' : 'bxs-down-arrow'" style="cursor:pointer;"></i></th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item,index) in filteredData1" :key="index">
                  <td><strong>{{ item.name }}</strong></td>
                  <td>{{ item.version }}</td>
                  <td>{{ item.size }}</td>
                  <td>{{ item.category }}</td>
                  <td><span :class="riskClass(item.risk)">{{ item.risk }}</span></td>
                  <td><button class="btn p-0" @click="moveToWhite(item)"><i class="bx bxs-chevrons-right"></i></button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Whitelist Section -->
      <div class="col-md-6">
        <div class="card mb-4" style="height:700px;">
          <div class="d-flex" style="max-height:20%;">
            <h5 class="card-header">Whitelist Settings</h5>
            <div class="card-header d-flex align-items-center ms-auto">
              <div class="btn-group">
                <button class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown">{{ dropButtonText_2 }}</button>
                <ul class="dropdown-menu">
                  <li @click="updateButtonText(2,'Name')"><a class="dropdown-item">Name</a></li>
                  <li @click="updateButtonText(2,'Size')"><a class="dropdown-item">Size</a></li>
                  <li @click="updateButtonText(2,'Category')"><a class="dropdown-item">Category</a></li>
                  <li @click="updateButtonText(2,'Risk')"><a class="dropdown-item">Risk</a></li>
                </ul>
              </div>
              <input v-model="filterValue2" @keyup.enter="selectWhite" class="form-control mx-3" placeholder="Filter..." style="width:50%;">
              <button @click="selectWhite" class="btn btn-primary" style="width:20%">Filter</button>
            </div>
            <div class="d-flex align-items-center ms-auto px-2" @click="exportToCsv(whitedata,0)">
              <i class="bx bx-download" style="cursor:pointer;"></i>
            </div>
          </div>
          <div id="whitebar" class="card-body overflow-auto" style="padding:0!important;">
            <table class="table table-hover table-sm text-center">
              <thead>
                <tr>
                  <th>Name</th><th>Package</th><th>Size</th><th>Category</th>
                  <th>Risk <i @click="rankByRisk2" class="bx" :class="isUpArrow2 ? 'bxs-up-arrow' : 'bxs-down-arrow'" style="cursor:pointer;"></i></th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item,index) in filteredData2" :key="index">
                  <td><strong>{{ item.name }}</strong></td>
                  <td>{{ item.version }}</td>
                  <td>{{ item.size }}</td>
                  <td>{{ item.category }}</td>
                  <td><span :class="riskClass(item.risk)">{{ item.risk }}</span></td>
                  <td><button class="btn p-0" @click="moveToBlack(item)"><i class="bx bxs-chevrons-left"></i></button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

    <!-- Custom Entry Section -->
    <div class="row container-p-y" style="padding-top:0!important;">
      <div class="col-12">
        <div class="card mb-4">
          <h5 class="card-header">Configure Custom List</h5>
          <div class="card-body">
            <div class="row flex-wrap">
              <div class="col-2">
                <label class="form-label">APK MD5</label>
                <input v-model="set_md5" class="form-control" placeholder="e.g. mds2342dacz4122" />
              </div>
              <div class="col-2">
                <label class="form-label">APK Name</label>
                <input v-model="set_name" class="form-control" placeholder="e.g. BananaComic" />
              </div>
              <div class="col-2">
                <label class="form-label">APK Package</label>
                <input v-model="set_pack" class="form-control" placeholder="e.g. com.mhapp (optional)" />
              </div>
              <div class="col-2">
                <label class="form-label">APK Category</label>
                <select v-model="set_cate" class="form-select">
                  <option v-for="it in categories" :key="it.value" :value="it.value">{{ it.label }}</option>
                </select>
              </div>
              <div class="col-2">
                <label class="form-label">APK Size</label>
                <input v-model="set_size" class="form-control" placeholder="e.g. 16.2 MB" />
              </div>
            </div>
            <div class="text-end mt-3">
              <button class="btn btn-primary me-2" @click.stop="addBlack">Add to Blacklist</button>
              <button class="btn btn-primary" @click.stop="addWhite">Add to Whitelist</button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>


<style scoped>
.rule-content {
  display: flex;
  flex-direction: column;
  overflow: auto;
  height: 95%;
}

.item-row {
  display: flex;
  position: relative;
  padding: 12px 10px 10px 20px;
  border-radius: 10px 10px 0 0;
  align-items: center; /* 添加这一行来实现垂直居中 */

}

.item-row span {
  margin-left: 18px;
  font-family: "Microsoft YaHei", sans-serif; /* 修正并添加备用字体 */
  font-size: 15px;
  font-weight: normal;
  color: #030229;
}

.rule-item {
  margin: 10px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #d8d8d8;
  align-items: center;
}

.item-row.all-selected {
  background: rgba(96, 101, 255, 0.1);
  border-bottom: 1px solid #D8D8D8;
}

.item-row.partial-selected {
  background: rgba(96, 91, 255, 0.1);
  border-bottom: 1px solid #D8D8D8;
}

.dropdown {
  padding-top: 5px;
  margin-bottom: 5px;
  border-radius: 0 0 10px 10px;
  opacity: 1;
  background: #ffffff;
  box-sizing: border-box;
  border-top: 1px solid #d8d8d8;
}


.single-rule {
  display: flex;
  align-items: center; /* 垂直居中对齐 */
  padding: 5px 15px 5px 30px;
}

.single-rule span {
  flex: 1; /* 使span能够自动调整宽度 */
  padding-left: 10px;
  font-family: "Microsoft YaHei", sans-serif;
  font-size: 14px;
  font-weight: normal;
}

.single-rule.selected span {
  font-family: Microsoft YaHei, sans-serif;
  font-weight: bold;
  letter-spacing: 0;
  color: #605bff;
  align-items: center; /* 添加这一行来实现垂直居中 */
}

/* 规则项复选框样式 */
.rule-item-checkbox {
  width: 20px; /* 调整复选框的宽度 */
  height: 20px; /* 调整复选框的高度 */
}

.rule-item-checkbox.all-selected {
  accent-color: #605bff; /* 全选时的复选框颜色 */
}

.rule-item-checkbox.partial-selected {
  position: relative; /* 添加相对定位 */

}

.rule-item-checkbox.partial-selected::after {
  content: ""; /* 添加伪元素 */
  display: block;
  width: 70%; /* 调整圆形大小 */
  height: 70%; /* 调整圆形大小 */
  border-radius: 50%;
  background-color: transparent; /* 设置背景色为透明 */
  border: 3px solid #605bff; /* 添加边框 */
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.single-rule input[type="checkbox"] {
  width: 20px; /* 固定checkbox宽度 */
  height: 20px; /* 固定checkbox高度 */
  margin-right: 10px; /* 与span元素保持间距 */
}

.single-rule input[type="checkbox"].selected {
  width: 20px; /* 固定checkbox宽度 */
  height: 20px; /* 固定checkbox高度 */
  margin-right: 10px; /* 与span元素保持间距 */
  accent-color: #605bff;
}

.single-rule.selected span {
  font-family: Microsoft YaHei, sans-serif;
  font-weight: bold;
  letter-spacing: 0;
  color: #605bff;
}

.expand-indicator {
  margin-left: auto; /* 确保箭头在最右侧 */
  padding-right: 10px; /* 右侧留一些间距 */
  cursor: pointer; /* 将鼠标光标改为指针 */
  height: 10px; /* 根据需要调整大小 */
  width: auto; /* 保持SVG的宽高比 */
}

.add-rule {
  position: relative;
  margin: 15px;
  height: 47px;
  border-radius: 7px;
  /* 外部/Text */
  background: rgba(3, 2, 41, 0.03);
  cursor: pointer;
}

.add-rule div {
  padding-top: 5px;
  font-family: "Microsoft YaHei UI", serif;
  font-size: 36px;
  font-weight: 900;
  line-height: 34px;
  text-align: center;
  vertical-align: center;
  letter-spacing: 0;

  font-feature-settings: "kern" on;
  color: #030229;
}

.add-category {
  display: flex;
  margin: 10px;
  border-radius: 10px;
  min-height: 66px;
  background: #ffffff;
  border: 1px solid #d8d8d8;
  align-items: center;
  justify-content: space-evenly;
  cursor: pointer;
}

.add-category div {
  font-family: "Microsoft YaHei UI", serif;
  font-size: 36px;
  font-weight: 900;
  line-height: 34px;
  text-align: center;
  vertical-align: center;
  letter-spacing: 0;

  font-feature-settings: "kern" on;
  /* 外部/Primary */
  color: #605BFF;
}

#blackbar {
  min-height: 80%;

}

#whitebar {
  min-height: 80%;

}

/*!* Define global styles *!*/
/*.table-responsive {*/
/*  overflow-x: auto; !* Enable horizontal scrolling *!*/
/*}*/

/*!* Set max-width and allow scrolling for all columns except the first one *!*/
/*.table-responsive table.table.table-hover.table-sm th:not(:first-child),*/
/*.table-responsive table.table.table-hover.table-sm td:not(:first-child) {*/
/*  max-width: 120px; !* Adjust max-width as needed *!*/
/*  overflow: auto;*/
/*  white-space: nowrap; /* Prevent text wrapping */
/* }*/

.scrollable-td {
  max-width: 150px; /* 设置最大宽度，超出部分会水平滚动 */
  overflow-x: auto; /* 水平溢出时显示滚动条 */
  white-space: nowrap; /* 禁止文本换行 */
  position: relative;
}

.pack_bar {
  max-width:90px;
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


.w-20 {
  width: 20%;
}

.alert {
  width: 50%;
  position: fixed; /* 或者使用合适的布局方式 */
  top: 20px;
  z-index: 99999; /* 确保提示框在其他内容之上 */
}
</style>