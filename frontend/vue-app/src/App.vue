<template>
  <div class="relative overflow-x-hidden">
    <!-- 배경 꾸미기용 은은한 블루 구체 -->
    <div class="fixed top-[-10%] left-[-10%] w-96 h-96 bg-cerulean-300/30 rounded-full blur-3xl pointer-events-none"></div>
    <div class="fixed bottom-[10%] right-[-5%] w-[30rem] h-[30rem] bg-blue-400/20 rounded-full blur-3xl pointer-events-none"></div>

    <div class="relative z-10 max-w-5xl mx-auto px-4 py-6">
      <header class="glass-nav text-white rounded-2xl px-6 py-4 mb-8 flex justify-between items-center shadow-lg">
        <div class="flex items-center space-x-2 cursor-pointer" @click="currentTab = 'home'">
          <span class="text-2xl">🐳</span>
          <h1 class="text-xl font-bold tracking-wider">LocalHub <span class="text-xs bg-white/20 px-2 py-0.5 rounded-full ml-1">BUSAN</span></h1>
        </div>
        <nav class="flex space-x-2 text-sm font-medium">
          <button @click="currentTab = 'home'" :class="currentTab === 'home' ? 'bg-white text-cerulean-700 shadow' : 'hover:bg-white/10'" class="px-4 py-2 rounded-xl transition">📊 대시보드</button>
          <button @click="currentTab = 'board'" :class="currentTab === 'board' ? 'bg-white text-cerulean-700 shadow' : 'hover:bg-white/10'" class="px-4 py-2 rounded-xl transition">💬 익명 게시판</button>
        </nav>
      </header>

      <!-- 탭 1: 대시보드 -->
      <DashboardView v-show="currentTab === 'home'" 
      :posts="posts"  />

      <!-- 탭 2: 익명 게시판 -->
      <BoardView 
        v-show="currentTab === 'board'" 
        :posts="posts" 
        @refresh-posts="loadPosts"
        @open-write="showWriteModal = true"
        @open-detail="handleOpenDetail" 
      />

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
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}/api/posts`);
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
