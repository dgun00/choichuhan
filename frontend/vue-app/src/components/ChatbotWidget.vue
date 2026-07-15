<template>
  <div class="fixed bottom-6 right-6 z-40">
    <button v-if="!showChat" @click="showChat = true" class="w-14 h-14 bg-cerulean-700 hover:bg-cerulean-800 text-white rounded-full shadow-2xl flex items-center justify-center text-2xl transition transform hover:scale-110 border-2 border-white/40">
      💬
    </button>

    <div v-else class="glass-modal w-80 sm:w-96 h-[28rem] rounded-3xl shadow-2xl border border-white flex flex-col overflow-hidden animate-fade-in">
      <div class="bg-cerulean-700 text-white px-4 py-3 flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <span class="text-xl">🤖</span>
          <div>
            <h4 class="font-bold text-xs">LocalHub AI 챗봇</h4>
            <p class="text-[10px] text-cerulean-200">부산 권역 공공데이터 기반 답변</p>
          </div>
        </div>
        <button @click="showChat = false" class="text-white/80 hover:text-white font-bold">✕</button>
      </div>

      <div ref="chatScrollRef" class="flex-1 p-3 overflow-y-auto space-y-3 text-xs">
        <div v-for="(msg, index) in chatHistory" :key="index" :class="msg.role === 'user' ? 'text-right' : 'text-left'">
          <span :class="msg.role === 'user' ? 'bg-cerulean-700 text-white rounded-br-none' : 'bg-white/80 text-slate-700 border border-white rounded-bl-none shadow-sm'" class="inline-block px-3 py-2 rounded-2xl max-w-[80%] whitespace-pre-wrap text-left">
            {{ msg.content }}
          </span>
        </div>

        <div v-if="isChatLoading" class="text-left">
          <span class="inline-block px-3 py-2 rounded-2xl bg-white/80 text-slate-400 border border-white rounded-bl-none shadow-sm">
            답변 작성 중...
          </span>
        </div>
      </div>

      <div class="p-2 bg-white/60 border-t border-white/80 flex space-x-1">
        <input v-model="chatInput" @keyup.enter="sendChatMessage" type="text" placeholder="이번 주말 부산 축제 알려줘!" class="flex-1 bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs outline-none focus:ring-2 focus:ring-cerulean-500">
        <button @click="sendChatMessage" class="bg-cerulean-700 hover:bg-cerulean-800 text-white px-3 py-2 rounded-xl text-xs font-bold transition">전송</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch} from 'vue';
import axios from 'axios';

const showChat = ref(false);
const chatInput = ref('');
const chatHistory = ref([
  { role: 'assistant', content: '안녕하세요! 부산 권역 정보 커뮤니티 LocalHub AI입니다. 축제, 맛집, 관광지 무엇이든 물어보세요! 🐬' }
]);

const isChatLoading = ref(false);
const chatScrollRef = ref(null);

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const scrollChatToBottom = async () => {
  await nextTick();
  if (chatScrollRef.value) {
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight;
  }
};

watch([chatHistory, isChatLoading, showChat], scrollChatToBottom, { deep: true });

const sendChatMessage = async () => {
  if (!chatInput.value.trim()) return;
  const userMsg = chatInput.value;
  chatHistory.value.push({ role: 'user', content: userMsg });
  chatInput.value = '';

  try {
    const res = await axios.post(`${API_BASE}/api/chat`, { message: userMsg });
    const answer = res?.data?.answer ?? '죄송합니다. 응답을 받지 못했습니다.';
    chatHistory.value.push({ role: 'assistant', content: answer });
  } catch (err) {
    // 백엔드 서버가 켜져있지 않을 때를 대비한 더미 응답
    setTimeout(() => {
      chatHistory.value.push({
        role: 'assistant',
        content: `[AI 챗봇 더미 응답] "${userMsg}"에 대한 부산 공공데이터 조회 결과입니다. 이번 주말 광안리나 해운대 인근 모범음식점 방문을 추천드립니다!`
      });
    }, 600);
  }
};
</script>