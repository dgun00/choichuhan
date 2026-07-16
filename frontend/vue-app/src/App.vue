<template>
  <div class="relative overflow-x-hidden">
    <!-- 배경 꾸미기용 은은한 블루 구체 -->
    <div class="fixed top-[-10%] left-[-10%] w-96 h-96 bg-cerulean-300/30 rounded-full blur-3xl pointer-events-none"></div>
    <div class="fixed bottom-[10%] right-[-5%] w-[30rem] h-[30rem] bg-blue-400/20 rounded-full blur-3xl pointer-events-none"></div>

    <div class="relative z-10 max-w-6xl mx-auto px-4 py-6 sm:py-8">
  <!-- 🌊 상단 네비게이션 헤더 (배경 그라데이션 및 입체감 추가) -->
  <header class="relative bg-gradient-to-r from-white/90 via-sky-50/80 to-blue-50/90 backdrop-blur-2xl border border-white rounded-[2rem] px-6 py-4 mb-8 flex flex-col sm:flex-row justify-between items-center shadow-[0_8px_30px_rgb(14,165,233,0.1)] gap-4 overflow-hidden">
    <!-- 헤더 내부 장식용 빛 반사 효과 -->
    <div class="absolute top-0 left-0 w-full h-1/2 bg-gradient-to-b from-white/60 to-transparent pointer-events-none"></div>

    <div class="relative z-10 flex items-center space-x-2 cursor-pointer transition-transform hover:scale-105" @click="currentTab = 'home'">
      <span class="text-3xl drop-shadow-sm">🌊</span>
      <h1 class="text-2xl font-black tracking-tight text-slate-800" style="letter-spacing: -0.05em;">
        BUSAN WAVE
        <span class="inline-block text-[10px] bg-gradient-to-r from-sky-500 to-indigo-600 text-white px-2.5 py-0.5 rounded-full ml-1 align-middle font-bold tracking-widest shadow-md">LIVE</span>
      </h1>
    </div>
    
    <nav class="relative z-10 flex p-1.5 bg-white/60 backdrop-blur-md rounded-2xl border border-white shadow-inner">
      <button @click="currentTab = 'home'" :class="currentTab === 'home' ? 'bg-white text-sky-600 shadow-sm font-extrabold' : 'text-slate-500 hover:text-sky-600 font-semibold'" class="px-5 py-2.5 rounded-xl transition-all text-sm flex items-center">
        <span class="mr-1.5 text-lg">📊</span> 로컬 대시보드
      </button>
      <button @click="currentTab = 'weather'" :class="currentTab === 'weather' ? 'bg-white text-sky-600 shadow-sm font-extrabold' : 'text-slate-500 hover:text-sky-600 font-semibold'" class="px-5 py-2.5 rounded-xl transition-all text-sm flex items-center">
        <span class="mr-1.5 text-lg">🌤️</span> 부산 여행날씨
      </button>
      <button @click="currentTab = 'board'" :class="currentTab === 'board' ? 'bg-white text-sky-600 shadow-sm font-extrabold' : 'text-slate-500 hover:text-sky-600 font-semibold'" class="px-5 py-2.5 rounded-xl transition-all text-sm flex items-center">
        <span class="mr-1.5 text-lg">💬</span> 실시간 라운지
      </button>
    </nav>
  </header>

  <!-- 탭 1: 대시보드 -->
  <DashboardView 
    v-show="currentTab === 'home'" 
    :posts="posts"  
  />

  <!-- 탭 2: 익명 게시판 -->
  <BoardView 
    v-show="currentTab === 'board'" 
    :posts="posts" 
    @refresh-posts="loadPosts"
    @open-write="showWriteModal = true"
    @open-detail="handleOpenDetail" 
  />

  <!-- 탭 3: 날씨 정보 -->
  <WeatherStrip 
  v-show="currentTab === 'weather'" />

  <!-- 플로팅 챗봇 -->
  <ChatbotWidget />
  </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import DashboardView from './components/DashboardView.vue';
import BoardView from './components/BoardView.vue';
import ChatbotWidget from './components/ChatbotWidget.vue';
import WeatherStrip from './components/WeatherStrip.vue';
import api from './api';

const ACTIVE_TAB_KEY = 'localhub.currentTab';
const currentTab = ref(localStorage.getItem(ACTIVE_TAB_KEY) || 'home');
const posts = ref([]);
const showWriteModal = ref(false);
const selectedPost = ref(null);

watch(currentTab, (tab) => {
  localStorage.setItem(ACTIVE_TAB_KEY, tab);
});

const loadPosts = async () => {
  try {
    const response = await api.get('/api/posts');
    console.log('API /api/posts response:', response.data);
    posts.value = response.data;
  } catch (error) {
    console.error("게시글 로드 실패, 기본 데이터 사용", error);
  }
};

const handleOpenDetail = (post) => {
  selectedPost.value = post;
  // 상세 모달 열기 로직 추가
};

onMounted(() => {
  loadPosts();
});
</script>
