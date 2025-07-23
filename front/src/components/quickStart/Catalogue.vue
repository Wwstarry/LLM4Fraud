<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { marked } from 'marked';

const inputText = ref('');
const messages = ref([]);

const sendMessage = async () => {
  const trimmedText = inputText.value.trim();
  if (!trimmedText) return;

  // User message
  messages.value.push({ text: trimmedText, type: 'user-message' });
  inputText.value = '';

  // Spinner placeholder
  const spinner = {
    text: '<div class="spinner-border text-primary" style="width: 2rem; height: 2rem;" role="status"><span class="visually-hidden">Loading...</span></div>',
    type: 'spinner'
  };
  messages.value.push(spinner);

  try {
    const response = await axios.post('catalogue', {
      message: trimmedText,
    });

    // Remove spinner
    messages.value = messages.value.filter(msg => msg.type !== 'spinner');
    // Model response
    messages.value.push({ text: marked(response.data.answer), type: 'model-message' });
  } catch (error) {
    // Remove spinner on error
    messages.value = messages.value.filter(msg => msg.type !== 'spinner');
    console.error('Error:', error);
  }
};
</script>

<template>
  <div class="container-xxl flex-grow-1 container-p-y">
    <div class="col-md-12">
      <div class="card" style="height: 76.5vh;">
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 1.125rem; font-weight: 500; opacity: 0.7;">
            What questions do you have about scam apps?
          </div>
        </div>
        <div class="card-body">
          <div class="chat-body" id="answer-content">
            <div
              v-if="messages.length === 0"
              id="initial-message"
              style="margin:auto; justify-content:center; align-items:center; text-align:center"
            >
              <img
                src="/assets/picture/Logo.png"
                alt="Logo"
                style="height: 100%; opacity: 0.2;"
              >
            </div>
            <div
              v-for="(message, index) in messages"
              :key="index"
              :class="['chat-message', message.type]"
            >
              <div v-html="message.text"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="margin: 20px auto 0; height: 7.5vh;">
        <div class="input-group" style="height: 100%;">
          <span class="input-group-text" id="basic-addon11">@</span>
          <textarea
            v-model="inputText"
            class="form-control"
            placeholder="Start your conversation"
            aria-label="User input"
            aria-describedby="basic-addon11"
            id="prompt"
            style="resize: none;"
            @keydown.enter.prevent="sendMessage"
            @keydown.shift.enter
          ></textarea>
          <button
            class="btn btn-outline-primary"
            type="button"
            @click="sendMessage"
            style="margin: 0"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  </div>
</template>



<style scoped>
.chat-body {
  flex-grow: 1;
  padding: 16px;
  height: 65vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
#initial-message {
  color: #fff;
  font-size: 2rem;
  font-weight: bold;
  text-align: center;
}
.chat-message {
  padding: 12px 12px;
  border-radius: 16px;
  max-width: 70%;
  margin: 8px;
}
.user-message {
  background-color: #5e5bd6;
  align-self: flex-end;
  color: #fdfdfe;
  font-weight: 600;
}
.model-message {
  align-self: flex-start;
  color: #9087e5;
  background-color: #e7e6f9;
  font-weight: 600;
}
.spinner {
  align-self: center;
}
</style>
