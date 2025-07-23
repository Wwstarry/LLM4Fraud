<template>
  <div>
    <canvas ref="canvas" class="screen" @click="handleCanvasClick"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';

const canvas = ref(null);
let intervalId = null;

const startCapturing = () => {
  intervalId = setInterval(captureScreen, 1000); // 每秒捕获一次屏幕
};

const stopCapturing = () => {
  if (intervalId !== null) {
    clearInterval(intervalId);
    intervalId = null; // 确保 intervalId 被重置
  }
};

// 通知父组件
defineExpose({
  startCapturing,
  stopCapturing,
});


const captureScreen = async () => {
  try {
    const response = await axios.post('/getScreen');
    if (response.data.frame) {
      updateCanvas(response.data.frame);
    }
  } catch (error) {
    console.error('Error capturing screen:', error);
  }
};

const updateCanvas = (base64Image) => {
  const context = canvas.value.getContext('2d');
  const img = new Image();
  img.src = 'data:image/png;base64,' + base64Image;
  img.onload = () => {
    // 确保canvas大小与图片分辨率一致
    canvas.value.width = img.width;
    canvas.value.height = img.height;
    context.clearRect(0, 0, canvas.value.width, canvas.value.height); // 清空画布
    context.drawImage(img, 0, 0);
  };
};

const handleCanvasClick = (event) => {
  const rect = canvas.value.getBoundingClientRect();
  const scaleX = 540 / rect.width;
  const scaleY = 960 / rect.height;
  const x = (event.clientX - rect.left) * scaleX;
  const y = (event.clientY - rect.top) * scaleY;

  console.log(`Click at: ${x}, ${y}`);
  axios.post('/click', { x, y })
      .then(response => {
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
};

onMounted(() => {

});

onBeforeUnmount(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});
</script>

<style>
.screen {
  width: 100%;
  height: 100%;
  display: block; /* 确保canvas作为块级元素 */
}

button {
  margin: 5px;
}
</style>
